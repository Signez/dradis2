from dradis.models import db
from dradis.sqlalchemy_jsonapi import JSONAPIMixin


class Action(JSONAPIMixin, db.Model):
    __tablename__ = "action"
    jsonapi_key = "action"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    task = db.Column(db.String(255), nullable=False)

    def __unicode__(self):
        if self.title:
            mtd = self.title
        elif self.command:
            mtd = self.command
        else:
            mtd = u"(vide)"
        return mtd

    def __repr__(self):
        return u"<Action #%r : '%s'>" % (self.id, self.__unicode__())
