import datetime
from sqlalchemy import orm
from dradis.models import db
from dradis.models.playlist_element import PlaylistElement
from dradis.sqlalchemy_jsonapi import JSONAPIMixin, as_relationship


class CantMoveError(Exception):
    pass


class CantDeleteError(Exception):
    pass


class Playlist(JSONAPIMixin, db.Model):
    jsonapi_key = "playlist"
    jsonapi_relationships_override = {
        'elements': lambda x: x.elements_after_history
    }

    id = db.Column(db.Integer, primary_key=True)
    curpos = db.Column(db.Integer, default=0)
    name = db.Column(db.String(200), default=u"Sans nom")

    state = db.Column(db.String(200), default=u"stopped")

    last_changed_at = db.Column(db.DateTime)

    MOVABLE_STATES = ['ready', 'nothing']

    def __repr__(self):
        return u"<Playlist #%s : '%s' (%d elements, %s)>" % (self.id,
                                                             self.name,
                                                             len(self),
                                                             self.total_duration())

    def __len__(self):
        return len(self.elements)

    def total_duration(self):
        """
        Total duration of the playlist.
        """
        duration = 0
        for element in self.elements:
            duration += element.length
        return duration

    @as_relationship(to_many=True, linked_key="playlist_elements", link_key="elements")
    def elements_after_history(self):
        return self.elements_query.filter(PlaylistElement.position >= self.curpos - 2).all()

    @property
    def elements_query(self):
        """
        Return a collection containing all elements.
        """
        return db.session.query(PlaylistElement).filter_by(playlist=self)

    @property
    def pending_elements(self):
        """
        Return a collection containing all pending elements, including current_element.
        """
        return self.elements_query.filter(PlaylistElement.position >= self.curpos) \
            .order_by(PlaylistElement.position)

    @property
    def current_element(self):
        """
        Return current_element, the currently played element if the playlist is played, or the
        next element to play if the playlist is not playing.
        """
        try:
            return self.elements_query.filter(PlaylistElement.position == self.curpos).first()
        except orm.exc.NoResultFound:
            return None

    @property
    def elements_to_play(self):
        """
        Return a collection containing all pending elements but current_element.

        If current_element is playing, it is the same as pending_elements.
        """
        if self.current_element is None or self.current_element != "playing":
            return self.elements_query.filter(PlaylistElement.position >= self.curpos).order_by(PlaylistElement.position)
        else:
            return self.elements_query.filter(PlaylistElement.position > self.curpos).order_by(PlaylistElement.position)

    @staticmethod
    def element_by_uid(uid):
        try:
            element = db.session.query(PlaylistElement).get(uid)
            return element
        except db.exc.ObjectDeletedError:
            return None

    def element_by_position(self, position):
        try:
            element = self.elements_query.filter(PlaylistElement.position == position).first()
            return element
        except orm.exc.NoResultFound:
            return None

    @property
    def last_element(self):
        """
        Return last element of the playlist.
        """
        try:
            return self.elements_query.filter(PlaylistElement.position > -100) \
                .order_by(PlaylistElement.position.desc()).first()
        except orm.exc.NoResultFound:
            return None

    @property
    def last_element_played(self):
        """
        Return last played element, using its on_air_since property.
        """
        try:
            return self.elements_query.filter(PlaylistElement.on_air_since is not None) \
                .order_by(PlaylistElement.on_air_since.desc()).first()
        except orm.exc.NoResultFound:
            return None

    def time_before_next_action(self):
        """
        Compute time before the next action, or end of playlist.
        """
        base = 0

        for element in self.pending_elements.all():
            base += element.pending_time

        return base

    def mark_as_changed(self):
        """
        Mark playlist as changed. Will be used by clients to force an update on
        their list.
        """
        self.last_changed_at = datetime.datetime.now()

        if self.studio:
            self.studio.mark_as_changed()

    @property
    def next_action_at(self):
        """
        Compute next action on_air time, using current element on_air_since and next length.
        """

        if not self.current_element:
            return None

        base = self.current_element.on_air_since

        if base is None:
            return None

        for element in self.pending_elements.all():
            if element.action is not None:
                return base

            base += datetime.timedelta(seconds=element.length)

        return base

    @property
    def next_action_slug(self):
        """
        Compute next action on_air time, using current element on_air_since and next length.
        """

        if not self.current_element:
            return None

        # TODO: Dude, I'm sure I can do something better than that.
        for element in self.pending_elements.all():
            if element.action is not None:
                return element.action.slug

        return None

    def add_element(self, element):
        """
        Add an element to playlist, at its end.
        """
        if element in self.elements:
            return  # U ARE ALREADY HERE DUDE

        if self.last_element:
            element.position = self.last_element.position + 1
        else:
            element.position = 0

        element.added_at = datetime.datetime.now()

        element.playlist = self
        self.elements.append(element)

        self.mark_as_changed()

    def remove_element(self, target_element):
        """
        Remove an element from the playlist if available. Will raise CantDeleteError if is not
        available.
        """
        if target_element not in self.elements:
            return  # U DON'T BELONG HERE DUDE

        if self.curpos > target_element.position:
            raise CantDeleteError("Can't remove an element already aired.")

        elements_after = self.elements_query.filter(PlaylistElement.position > target_element.position).all()

        for element_after in elements_after:
            element_after.position -= 1

        self.elements.remove(target_element)

        target_element.playlist = None

        self.mark_as_changed()

    def move_element(self, element, target_position):
        """
        Move element before element with target_position.

         0  1  2  3  4                         0  1  2  3  4
        [A, B, C, D, E] ; move_element(B, 3); [A, C, B, D, E]

         0  1  2  3  4                         0  1  2  3  4
        [A, B, C, D, E] ; move_element(D, 1); [A, D, B, C, E]
        """
        if element not in self.elements:
            return  # U DON'T BELONG HERE DUDE

        previous_position = element.position
        previous_last_element_position = self.last_element.position

        if target_position == previous_position or target_position == previous_position + 1:
            raise CantMoveError("Can't move to the same position.")

        if target_position < self.curpos:
            raise CantMoveError("Can't move an element before the playing element (target position was {}, playing element at {}).".format(
                target_position, self.curpos
            ))

        if previous_position < self.curpos:
            raise CantMoveError("Can't move an already played element.")

        try:
            lastnonreadypos = self.elements_to_play \
                .filter(~PlaylistElement.status.in_(self.MOVABLE_STATES)) \
                .order_by(PlaylistElement.position.desc()).first()

            if isinstance(lastnonreadypos, PlaylistElement) and target_position <= lastnonreadypos.position:
                raise CantMoveError("Can't move an element before an already played element (curpos = {}).".format(lastnonreadypos.position))
        except orm.exc.NoResultFound:
            pass

        if target_position == self.curpos and self.current_element is not None and \
           self.current_element.status not in self.MOVABLE_STATES:
            return

        if self.last_element == element and target_position > previous_position:
            raise CantMoveError("Can't move an the last element after itself.")

        self.remove_element(element)
        db.session.commit()

        if target_position > previous_last_element_position:
            target_position = self.last_element.position + 1
        else:
            if target_position > previous_position:
                allafter = self.elements_query.filter(PlaylistElement.position >= target_position - 1).all()
                target_position -= 1
            else:
                allafter = self.elements_query.filter(PlaylistElement.position >= target_position).all()

            for el in allafter:
                el.position += 1

        element.position = target_position

        element.playlist = self
        self.elements.append(element)

        self.mark_as_changed()

    def insert_element(self, element, position):
        """
        Insert an element in playlist, at given position.

        Technically, it consists of adding the element, then moving it on the right
        place.
        """

        if self.last_element is not None and position > self.last_element.position:
            self.add_element(element)
        else:
            self.add_element(element)
            self.move_element(element, position)
