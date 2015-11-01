from sqlalchemy import orm
from dradis.sqlalchemy_jsonapi import JSONAPIMixin
from dradis.models import db
from dradis.models.action import Action
from dradis.models.media import Media
import datetime


class PlaylistElement(JSONAPIMixin, db.Model):
    jsonapi_key = "playlist_element"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    status = db.Column(db.String(8), default="ready")

    added_at = db.Column(db.DateTime)
    edited_at = db.Column(db.DateTime)
    on_air_since = db.Column(db.DateTime)
    done_since = db.Column(db.DateTime)
    skipped = db.Column(db.Boolean)

    length_hint = db.Column(db.Integer)
    comment = db.Column(db.Text)

    media_id = db.Column(db.Integer, db.ForeignKey('media.id', ondelete="SET NULL"))
    media = db.relationship("Media")

    action_id = db.Column(db.Integer, db.ForeignKey('action.id'))
    action = db.relationship("Action")

    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    playlist = db.relationship("Playlist", backref="elements")

    live_content = db.Column(db.Text)

    @property
    def will_end_at(self):
        """
        Return estimated end time for an element.
        """
        if self.on_air_since is None:
            return None

        return int(self.on_air_since) + self.length

    @property
    def content(self):
        """
        Return action or media contained in this element.
        """
        if self.action:
            return self.action
        else:
            return self.media

    @property
    def length(self):
        """
        Return estimated length of element, if available.
        """
        if self.action:
            return self.length_hint if self.length_hint is not None else 0
        elif self.media:
            return self.media.length
        else:
            return 0  # Empty playlist element

    @property
    def elapsed_time(self):
        if self.status == "playing":
            return (datetime.datetime.now() - self.on_air_since).total_seconds()
        elif self.status == "done":
            return self.length
        else:
            return 0

    @property
    def pending_time(self):
        if self.status == "playing":
            return self.length - self.elapsed_time
        elif self.status == "done":
            return 0
        else:
            return self.length

    def mark_as_done(self, skipped=None):
        self.status = "done"
        self.done_since = datetime.datetime.now()

        if skipped is not None:
            self.skipped = skipped

    def __repr__(self):
        return "<PlaylistElement #%r, position=%d, '%s'>" % (self.id, int(self.position), repr(self.content))

    @staticmethod
    def find_by(uid=None, pos=None, playlist=None):
        try:
            if uid is not None:
                return db.session.query(PlaylistElement).get(uid)
            elif pos is not None and playlist is not None:
                return PlaylistElement.query.filter_by(position=pos).filter_by(playlist=playlist).first()
            else:
                return None
        except orm.exc.NoResultFound:
            return None

    @staticmethod
    def build_from_content(content):
        if isinstance(content, Media):
            return PlaylistElement(media=content)
        elif isinstance(content, Action):
            return PlaylistElement(action=content)
        else:
            return None

    @staticmethod
    def forge(content_type, content_id):
        try:
            if content_type == "action":
                the_action = Action.query.get(content_id)
                return PlaylistElement(action=the_action)
            else:
                the_media = Media.query.get(content_id)
                return PlaylistElement(media=the_media)
        except orm.exc.NoResultFound:
            return None
