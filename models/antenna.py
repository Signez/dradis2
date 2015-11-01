from sqlalchemy import orm
from dradis.sqlalchemy_jsonapi import JSONAPIMixin
from dradis.models import db


class Antenna(JSONAPIMixin, db.Model):
    jsonapi_key = "show"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)

    def __str__(self):
        return "<Antenna slug=%r>" % self.slug

    @staticmethod
    def find_by(uid=None, slug=None):
        try:
            if uid is not None:
                return db.session.query(Antenna).get(uid)
            elif slug is not None:
                return db.session.query(Antenna).filter_by(slug=slug).one()
            else:
                return None
        except orm.exc.NoResultFound:
            return None
