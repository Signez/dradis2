import datetime
from sqlalchemy import orm
from dradis.sqlalchemy_jsonapi import JSONAPIMixin
from dradis.models import db


class Studio(JSONAPIMixin, db.Model):
    jsonapi_key = "studio"

    id = db.Column(db.Integer, primary_key=True)

    antenna_id = db.Column(db.Integer, db.ForeignKey("antenna.id"))
    antenna = db.relationship("Antenna", backref=db.backref("studios"))

    name = db.Column(db.String(100))
    slug = db.Column(db.String(10), unique=True)

    jukebox = db.relationship("Playlist", backref=db.backref("studio", uselist=False))
    jukebox_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    jukebox_liqname = db.Column(db.String(100))

    bed_id = db.Column(db.Integer, db.ForeignKey('media.id'))  # ManyToOne('Media')
    bed = db.relationship("Media")
    #  bed_uid = db.Column(db.Integer)
    bed_on_air_since = db.Column(db.DateTime)
    bed_repeat = db.Column(db.Boolean)
    bed_liqname = db.Column(db.String(100))

    fx_liqname = db.Column(db.String(100))

    rec_show_liqname = db.Column(db.String(100))
    rec_show_enabled = db.Column(db.Boolean)
    rec_show_active = db.Column(db.Boolean)
    rec_gold_liqname = db.Column(db.String(100))
    rec_gold_enabled = db.Column(db.Boolean)
    rec_gold_active = db.Column(db.Boolean)

    selected = db.Column(db.Boolean)

    last_changed_at = db.Column(db.DateTime)

    current_show_name = db.Column(db.Text)

    def __str__(self):
        return "<Studio slug=%r>" % self.slug

    def mark_as_changed(self):
        self.last_changed_at = datetime.datetime.now()

    @staticmethod
    def find_by(uid=None, slug=None):
        try:
            if uid is not None:
                return db.session.query(Studio).get(uid)
            elif slug is not None:
                return db.session.query(Studio).filter_by(slug=slug).one()
            else:
                return None
        except orm.exc.NoResultFound:
            return None
