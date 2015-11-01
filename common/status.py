from itertools import chain
import json
import re
import socket
import time
import urllib2
from dradis.common.helpers import iso8601
from dradis.models.studio import Studio
from dradis.models.playlist import Playlist
from dradis.models import db
from dradis.main import app, liq
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from os import listdir
from os.path import isfile, join, getctime, basename, getsize
from heapq import nlargest


def serialize_date(date):
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return date


def serialize_timestamp(date):
    if isinstance(date, datetime):
        epoch = datetime.utcfromtimestamp(0)
        delta = date - epoch
        return round(delta.total_seconds() * 1000.0)
    else:
        return date


def get_public_url(path):
    with app.app_context():
        path = path.replace(app.config.get('RECORDS_ROOT'), app.config.get('RECORDS_URL'))
        path = path.replace(app.config.get('MEDIA_ROOT'), app.config.get('MEDIA_URL'))
        return path


def get_files_info(files):
    return [{
        "filename": basename(path),
        "url": get_public_url(path),
        "size": getsize(path)
    } for path in files]


def get_ten_last_files(pattern):
    with app.app_context():
        records_path = app.config.get('RECORDS_ROOT')
        all_records = [join(records_path, f) for f in listdir(records_path) if isfile(join(records_path, f)) and pattern in f]
        return get_files_info(f for f in nlargest(10, all_records, key=getctime))


def get_ten_last_piges():
    with app.app_context():
        pige_path = join(app.config.get('RECORDS_ROOT'), "pige")
        day_dirs = nlargest(10, [join(pige_path, day_dir) for day_dir in listdir(pige_path)], key=getctime)
        all_records = [join(day_dir, f) for day_dir in day_dirs for f in listdir(day_dir) if isfile(join(day_dir, f))]
        return get_files_info(f for f in nlargest(10, all_records, key=getctime))


def get_waiting_uploaded_files():
    with app.app_context():
        uploaded_path = join(app.config.get('MEDIA_ROOT'), "uploads")
        all_waiting_files = [join(uploaded_path, f) for f in listdir(uploaded_path) if isfile(join(uploaded_path, f))]
        return get_files_info(all_waiting_files)


prog = re.compile(r'^mount=.+?, artist=(?P<artist>.*?), title=(?P<title>.*?), listeners=(?P<listeners>.*?)$')


def fetch_listeners():
    # TODO: Fetch from Redis (add an external tool which only usage is to track statistics on listeners)
    return 42

    try:
        content = urllib2.urlopen("http://live.synopslive.net:8000/status4.xsl", timeout=1)

        listeners = 0

        for line in [prog.match(line) for line in content if line.startswith("mount=")]:
            listeners += int(line.group("listeners"))

        return listeners

    except urllib2.URLError:
        return 0

    except socket.timeout:
        return 0


def unserialize_booleans(string):
    if string == "true" or string == "on":
        return True
    elif string == "false" or string == "off":
        return False

    return string


def simple_camelize(underscore_key):
    words = underscore_key.split('_')

    other_words = ''
    if len(words) > 1:
        other_words = ''.join(word[0].upper() + word[1:] for word in words[1:])

    return words[0] + other_words


def send_command(command):
    return liq.send_command(command)


def system_status(liquidsoap_json_status, liquidsoap_json_updated_at):
    with app.app_context():
        last_changed_at_query = func.max(Studio.last_changed_at).label("last_changed_at")

        try:
            liquidsoap_content = json.loads(liquidsoap_json_status)
        except ValueError:
            liquidsoap_content = False

        playlist_last_updated_times = db.session.query(Playlist.id, Playlist.last_changed_at).all()

        status = {
            'type': 'status',
            'serverTime': int(time.time()),
            'lastChangedAt': serialize_timestamp(db.session.query(last_changed_at_query).first()[0]),
            'online': False,
            'listeners': fetch_listeners(),
            'playlistLastChangedAt': dict([(content[0], serialize_timestamp(content[1])) for content in playlist_last_updated_times]),
            'lastPigeRecords': get_ten_last_piges(),
            'waitingUploadedFiles': get_waiting_uploaded_files()
        }

        liquidsoap_studios = False

        if liquidsoap_content:
            liquidsoap_studios = {
                'studio_a': json.loads(liquidsoap_content['studio_a']['json_encoded']),
                'studio_b': json.loads(liquidsoap_content['studio_b']['json_encoded'])
            }
            liquidsoap_global_status = liquidsoap_content['global']

            liquidsoap_selected = liquidsoap_global_status['selected']
            liquidsoap_updated_at = datetime.fromtimestamp(float(liquidsoap_json_updated_at) / 1000.0)

            online = liquidsoap_selected is not None and (datetime.now() - liquidsoap_updated_at) < timedelta(seconds=20)

            status['selected'] = liquidsoap_selected
            status['liquidsoapOnline'] = online
            status['liquidsoapUpdatedAt'] = liquidsoap_updated_at.strftime("%Y-%m-%dT%H:%M:%S")

            status["pigeRecorderOn"] = unserialize_booleans(liquidsoap_global_status.get("recorder.pige.on", "off"))

            try:
                status["liveMetadata"] = json.loads(liquidsoap_global_status.get("live.metadata", "{}"))
            except TypeError:
                pass

        for studio in db.session.query(Studio).all():
            studio = db.session.query(Studio).get(studio.id)
            jukebox = db.session.query(Playlist).get(studio.jukebox_id)

            studio_x = studio.slug

            status[studio_x] = {}
            status[studio_x]["selected"] = studio.selected
            status[studio_x]["lastShowRecords"] = get_ten_last_files("show_{}".format(studio_x))
            status[studio_x]["lastGoldRecords"] = get_ten_last_files("gold_{}".format(studio_x))
            status[studio_x]["bedRepeat"] = studio.bed_repeat

            next_action_at = jukebox.next_action_at
            if next_action_at:
                status[studio_x]["nextActionAt"] = next_action_at.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                status[studio_x]["nextActionAt"] = None

            next_action_slug = jukebox.next_action_slug
            if next_action_slug:
                status[studio_x]["nextActionSlug"] = next_action_slug
            else:
                status[studio_x]["nextActionSlug"] = None

            if liquidsoap_studios:
                liquidsoap_status = liquidsoap_studios[studio_x][studio_x]

                liquidsoap_status = dict(chain(liquidsoap_status[0].items(), liquidsoap_status[1].items()))
                liquidsoap_status["recorderShowOn"] = liquidsoap_status["{}.recorders.show.on".format(studio_x)]
                liquidsoap_status["recorderGoldOn"] = liquidsoap_status["{}.recorders.gold.on".format(studio_x)]

                for key, value in liquidsoap_status.iteritems():
                    formatted_key = simple_camelize(key.replace('.', '_').replace(studio_x + '_', ''))
                    status[studio_x][formatted_key] = unserialize_booleans(value)

    return status
