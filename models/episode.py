from sqlalchemy import orm
from dradis.sqlalchemy_jsonapi import JSONAPIMixin
from dradis.models import db


class Episode(JSONAPIMixin, db.Model):
    jsonapi_key = "episode"

    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    show = db.relationship("Show", backref=db.backref("episodes"))
    number = db.Column(db.String(10))
    name = db.Column(db.String(100))

    def __str__(self):
        return "<Episode slug=%r>" % self.slug

    @staticmethod
    def find_by(uid=None, slug=None):
        try:
            if uid is not None:
                return db.session.query(Episode).get(uid)
            elif slug is not None:
                return db.session.query(Episode).filter_by(slug=slug).one()
            else:
                return None
        except orm.exc.NoResultFound:
            return None
