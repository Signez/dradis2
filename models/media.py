from dradis.sqlalchemy_jsonapi import JSONAPIMixin
from dradis.models import db
from dradis.main import app
import os.path


class Media(JSONAPIMixin, db.Model):
    jsonapi_key = "media"
    jsonapi_columns_include = ["public_url", "kind"]

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(255))
    title = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    album = db.Column(db.String(255))
    length = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @property
    def public_url(self):
        if self.path:
            return self.path.replace(app.config['MEDIA_ROOT'], app.config['MEDIA_URL'])
        else:
            return None

    @property
    def kind(self):
        if self.path:
            kind = self.path.replace(app.config['MEDIA_ROOT'], '').strip('/').split('/', 1)[0]
            return kind
        else:
            return None

    def __unicode__(self):
        if self.title and self.artist:
            mtd = u"%s - %s" % (self.title, self.artist)
        else:
            mtd = os.path.basename(u"%s" % self.path)
        return mtd

    def __repr__(self):
        return u"<Media #%r : '%s'>" % (self.id, self.__unicode__())
