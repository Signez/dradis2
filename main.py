from __future__ import print_function

from flask import Flask
from flask.ext.assets import Environment, Bundle
from celery import Celery
from datetime import timedelta
import os
from os.path import isfile
import sys
from flask.ext.uwsgi_websocket import WebSocket
import jinja2
from dradis.common.liquidsoap import LiquidsoapConnection

dradis_root = os.path.dirname(__file__)


def load_env(root):
    env_filepath = os.path.join(root, ".env")

    if isfile(env_filepath):
        env_file = open(env_filepath)

        for line in env_file:
            key, content = line.split('=', 1)
            if key not in os.environ:
                os.environ[key] = content.strip("\n")


def check_env():
    required_env = [
        'DRADIS_API_KEY',
        'DRADIS_SQL',
        'RECORDS_ROOT',
        'MEDIA_ROOT',
        'MEDIA_URL'
    ]

    for key in required_env:
        if key not in os.environ:
            print("ERROR: Environment variable {} is required to run Dradis.".format(key), file=sys.stderr)
            sys.exit(1)

load_env(dradis_root)
check_env()

app = Flask('dradis.workers.webserver')
app.jinja_loader = jinja2.FileSystemLoader(os.path.join(dradis_root, "templates"))

app.config.update(
    DRADIS_API_KEY=os.environ['DRADIS_API_KEY'],
    DRADIS_ROOT=dradis_root,
    RECORDS_ROOT=os.environ['RECORDS_ROOT'],
    RECORDS_URL=os.environ['RECORDS_URL'],
    MEDIA_ROOT=os.environ['MEDIA_ROOT'],
    MEDIA_URL=os.environ['MEDIA_URL'],
    SQLALCHEMY_DATABASE_URI=os.environ['DRADIS_SQL'],
    SQLALCHEMY_ECHO=False
)


assets = Environment(app)
assets.debug = True

css = Bundle(
    'css/bootstrap.css',
    'css/dradis.less',
    'css/components/navbar.less',
    'css/components/media-element.less',
    'css/components/library.less',
    'css/components/playlist.less',
    'css/components/playlist-element.less',
    filters='less',
    output='gen/dradis-compiled.css'
)
assets.register('css_all', css)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    CELERY_ACCEPT_CONTENT=['json', 'pickle'],
    CELERY_DISABLE_RATE_LIMITS=True,
    CELERY_TIMEZONE='Europe/Paris',
    CELERYBEAT_SCHEDULE={}
)


def make_celery(flask_app):
    celery_app = Celery(flask_app.import_name, broker=flask_app.config['CELERY_BROKER_URL'])
    celery_app.conf.update(flask_app.config)
    task = celery_app.Task

    class ContextTask(task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return task.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


celery = make_celery(app)

liq = LiquidsoapConnection()

ws = WebSocket(app)

try:
    from dradis.debugger import debugger
except ImportError:
    def debugger():
        pass
