# coding=utf-8
import calendar
import os
import taglib
from dradis.main import app
from dradis.models import db
from dradis.models.action import Action
from dradis.models.media import Media
from dradis.models.playlist import Playlist
from dradis.models.studio import Studio
from dradis.models.playlist_element import PlaylistElement
from unicodedata import normalize


def generate_studios():
    created_studios = 0

    for letter in ('a', 'b'):
        if Studio.query.filter_by(slug=u"studio_%s" % letter).count() == 0:
            studio_x = Studio(name=u"Studio %s" % letter.upper(),
                              slug=u"studio_%s" % letter,
                              jukebox_liqname=u"studio_%s_jukebox_playlist" % letter,
                              bed_liqname=u"studio_%s_bed_playlist" % letter,
                              fx_liqname=u"studio_%s_fx_playlist" % letter,
                              rec_show_liqname=u"studio_%s_recorder_show" % letter,
                              rec_show_enabled=False,
                              rec_show_active=False,
                              rec_gold_liqname=u"studio_%s_recorder_gold" % letter,
                              rec_gold_enabled=False,
                              rec_gold_active=False,
                              selected=False)
            db.session.add(studio_x)
            created_studios += 1

    db.session.commit()

    return created_studios


def attach_empty_playlists():
    attached_empty_playlists = 0

    for letter in ('a', 'b'):
        studio = Studio.query.filter_by(slug=u"studio_%s" % letter).one()

        if studio.jukebox is None:
            studio.jukebox = Playlist()
            studio.jukebox.name = "Jukebox {}".format(letter.upper())
            db.session.add(studio)
            attached_empty_playlists += 1

    db.session.commit()

    return attached_empty_playlists


def add_default_actions():
    added_default_actions = 0
    modified_default_actions = 0

    default_actions = {
        "run_studio": {
            "title": "Début d'antenne",
            "task": "dradis.common.tasks.select_studio"
        },
        "live": {
            "title": "Plateau",
            "task": "dradis.common.tasks.start_live"
        },
        "end_studio": {
            "title": "Fin d'antenne",
            "task": "dradis.common.tasks.end_studio"
        }
    }

    for slug, action_content in default_actions.iteritems():
        action = Action.query.filter_by(slug=slug).first()

        if action is None:
            action = Action()
            added_default_actions += 1
        else:
            modified_default_actions += 1

        action.slug = slug
        action.title = action_content["title"]
        action.task = action_content["task"]

        db.session.add(action)
    db.session.commit()

    return {
        "status": "done",
        "added_default_actions": added_default_actions,
        "modified_default_actions": modified_default_actions
    }


def tags_for_file(filepath):
    track_file = taglib.File(filepath)
    tags = track_file.tags

    return dict(tags.items() + {
        "title": tags.get('TITLE', [None])[0],
        "artist": tags.get('ARTIST', [None])[0],
        "album": tags.get('ALBUM', [None])[0],
        "length": int(track_file.length)
    }.items())


def write_tags(filepath, tags):
    track_file = taglib.File(filepath)

    for key, value in tags.iteritems():
        if key in ['title', 'artist', 'album']:
            key = key.upper()

        track_file.tags[key] = [value]

    return track_file.save()


def secure_filename(filename):
    if isinstance(filename, unicode):
        filename = normalize('NFKD', filename).encode('ascii', 'ignore')

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')

    return filename.strip('._ ')


def generate_new_path(filepath):
    with app.app_context():
        saved_tags = tags_for_file(filepath)

        safe_artist = secure_filename(saved_tags["ARTIST"][0])
        safe_album = secure_filename(saved_tags["ALBUM"][0])
        safe_title = secure_filename(saved_tags["TITLE"][0])

        if "TRACKNUMBER" in saved_tags:
            track_number = int(saved_tags["TRACKNUMBER"][0].split("/")[0])

            safe_title = "{track_number:02}._{safe_title}".format(track_number=track_number, safe_title=safe_title)

        if "ORIGINALFILENAME" in saved_tags:
            safe_title += "." + saved_tags["ORIGINALFILENAME"][0].rsplit(".", 1)[1].lower()
        else:
            safe_title += "." + filepath.rsplit(".", 1)[1].lower()

        return os.path.join(app.config.get('MEDIA_ROOT'), "music", safe_artist, safe_album, safe_title)


def rescan(force=False):
    with app.app_context():
        media_folder = app.config.get('MEDIA_ROOT')

        total_seconds = files_without_tags = files_with_tags = total = 0
        files_added = files_updated = files_deleted = untouched_files = 0

        modified_times_cache = {}
        not_found_files = []

        for path, updated_at in db.session.query(Media.path, Media.updated_at):
            modified_times_cache[path.encode("utf-8")] = calendar.timegm(updated_at.utctimetuple())
            not_found_files.append(path.encode("utf-8"))

        for root, dirs, files in os.walk(media_folder):
            for name in files:
                if os.path.join(app.config.get('MEDIA_ROOT'), "uploads") in root:
                    continue

                if app.config.get('MEDIA_ROOT') == root:
                    continue

                if name.lower().endswith("mp3") or name.lower().endswith("ogg"):
                    track_path = os.path.join(os.path.abspath(root), name)
                    track_filename = os.path.basename(track_path)
                    already_exists = track_path in modified_times_cache.keys()

                    if already_exists:
                        not_found_files.remove(track_path)

                    if force or not already_exists or track_path in modified_times_cache and \
                            os.stat(track_path).st_mtime > modified_times_cache[track_path]:
                        tags = tags_for_file(os.path.join(root, name))

                        if "title" in tags and "artist" in tags:
                            files_with_tags += 1
                        else:
                            files_without_tags += 1

                        total_seconds += tags["length"]

                        if not already_exists:
                            db.session.add(Media(path=track_path,
                                                 filename=track_filename,
                                                 title=tags["title"],
                                                 artist=tags["artist"],
                                                 album=tags["album"],
                                                 length=tags["length"],
                                                 added_at=db.func.now(),
                                                 updated_at=db.func.now()))

                            files_added += 1

                        elif already_exists:
                            media = Media.query.filter_by(path=track_path).first()

                            media.filename = track_filename
                            media.title = tags["title"]
                            media.album = tags["album"]
                            media.artist = tags["artist"]
                            media.length = tags["length"]
                            media.updated_at = db.func.now()

                            files_updated += 1

                        del track_path
                        del tags

                        total += 1
                    else:
                        untouched_files += 1

        if len(not_found_files):
            for apath in not_found_files:
                media = Media.query.filter_by(path=apath).first()
                PlaylistElement.query.filter_by(media=media).update({"media_id": None})

                db.session.delete(media)

                files_deleted += 1

        db.session.commit()

        return {
            "added": files_added,
            "updated": files_updated,
            "deleted": files_deleted,
            "total": total,
            "untouched": untouched_files,
            "tagged": files_with_tags,
            "untagged": files_without_tags,
            "total_seconds": total_seconds
        }
