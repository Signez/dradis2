from dradis.main import app, celery
from dradis.models import db

# Importing api routes
from dradis.api import *

db.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(**{
        "debug": True,
        "master": True,
        "threads": 4,
        "lazy": True,
        "lazy-apps": True,
        "log-master": True,
        "worker-reload-mercy": 2,
        "py-autoreload": 1
    })
