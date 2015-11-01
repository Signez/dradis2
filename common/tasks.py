import json
import datetime
import urllib
from celery.utils.log import get_task_logger
import redis
from dradis.common.helpers import error_message, ok
from dradis.models import db
from dradis.models.action import Action
from dradis.models.media import Media
from dradis.models.playlist import Playlist, CantMoveError, CantDeleteError
from dradis.models.playlist_element import PlaylistElement
from dradis.models.studio import Studio
from dradis.common import status
from dradis.main import app, celery, liq
from celery.signals import worker_process_init


redis_instance = redis.StrictRedis()
logger = get_task_logger(__name__)


@celery.task()
def add_content_to_playlist(content_type, content_id, playlist_id, position=None):
    playlist = Playlist.query.get(playlist_id)
    if not isinstance(playlist, Playlist):
        return error_message("bad_argument", "Unable to read playlist.")

    if content_type == "media":
        content = Media.query.get(content_id)
    elif content_type == "action":
        content = Action.query.get(content_id)
    else:
        return error_message("bad_argument", "Wrong content_type.")

    playlist_element = PlaylistElement.build_from_content(content)

    if not playlist_element:
        return error_message("bad_argument", "Failed to create playlist element.")

    with redis_instance.lock("playlist_{}_add_lock".format(playlist_id)):
        if position:
            playlist.insert_element(playlist_element, position)
        else:
            playlist.add_element(playlist_element)
        db.session.add(playlist_element)
        db.session.commit()

    return ok()


@celery.task()
def remove_element_from_playlist(playlist_element_id, playlist_id):
    playlist_element = PlaylistElement.query.get(playlist_element_id)
    playlist = Playlist.query.get(playlist_id)

    if not playlist_element or not isinstance(playlist_element, PlaylistElement) or not isinstance(playlist, Playlist):
        return error_message("bad_argument")

    try:
        playlist.remove_element(playlist_element)
        db.session.delete(playlist_element)
        db.session.commit()

        return ok(and_squack=True)

    except CantDeleteError, exception:
        return error_message("cant_delete", exception.message)


@celery.task()
def move_element_inside_playlist(playlist_element_id, position, playlist_id):
    playlist_element = PlaylistElement.query.get(playlist_element_id)
    playlist = Playlist.query.get(playlist_id)

    if not playlist_element or not isinstance(playlist_element, PlaylistElement) \
            or not isinstance(playlist, Playlist) or not isinstance(position, int):
        return error_message("bad_argument")

    try:
        playlist.move_element(playlist_element, position)
        db.session.commit()

        return ok()

    except CantMoveError, exception:
        return error_message("cant_move", exception.message)


@celery.task
def check_next_element(studio_id, element_id):
    db.session.expire_all()

    studio = Studio.query.get(studio_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    current_element = studio.jukebox.current_element

    if not current_element:
        return error_message("no_current_element")

    if current_element.id != element_id:
        return error_message("probably_expired")

    pending_time = current_element.pending_time

    if pending_time > 0:
        next_element = studio.jukebox.element_by_position(studio.jukebox.curpos + 1)

        if next_element and next_element.media and next_element.status == 'ready':
            load_media(next_element.id, next_element.media, studio.jukebox_liqname)
            next_element.status = 'loaded'
            studio.jukebox.mark_as_changed()
            db.session.commit()

        logger.warning("Re-scheduling task for {} seconds...".format(pending_time))
        check_next_element.s(studio.id, current_element.id).apply_async(countdown=pending_time)
    else:
        logger.warning("Current element is done.")
        current_element.mark_as_done()
        studio.jukebox.curpos += 1
        studio.mark_as_changed()
        db.session.commit()

        play_current_element.delay(studio.id)

    return ok()


@celery.task()
def end_live(studio_id):
    studio = Studio.query.get(studio_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    flush_bed(studio)

    liq.set_var("{}.jukebox.switch".format(studio.slug), True)
    liq.set_var("{}.jukebox.volume".format(studio.slug), 1.0)
    liq.set_var("{}.plateau.volume".format(studio.slug), 0.0)

    current_element = studio.jukebox.current_element
    current_element.mark_as_done()

    studio.jukebox.curpos += 1
    studio.mark_as_changed()

    db.session.commit()

    play_current_element.delay(studio.id)

    return ok(and_squack=True)


@celery.task()
def record(element_id=None, studio_id=None, recorder=None):
    if element_id:
        current_element = PlaylistElement.query.get(element_id)

        if not current_element:
            return error_message("bad_argument")

        studio = current_element.playlist.studio
    elif studio_id:
        studio = Studio.query.get(studio_id)
    else:
        return error_message("bad_argument")

    if not isinstance(studio, Studio) or recorder not in ("gold", "show"):
        return error_message("bad_argument")

    recorder_name = "{}_recorder_{}".format(studio.slug, recorder)

    if liq.send_command("{}.status".format(recorder_name)) != "on":
        liq.send_command("{}.refresh_metadata".format(recorder_name))
        liq.send_command("{}.start".format(recorder_name))
    else:
        logger.warn("Recorder {} was already on!".format(recorder_name))

    if element_id:
        # noinspection PyUnboundLocalVariable
        current_element.mark_as_done()
        studio.jukebox.curpos += 1

    studio.mark_as_changed()
    db.session.commit()

    return ok()


@celery.task()
def end_record(element_id=None, studio_id=None, recorder=None):
    if element_id:
        current_element = PlaylistElement.query.get(element_id)

        if not current_element:
            return error_message("bad_argument")

        studio = current_element.playlist.studio
    elif studio_id:
        studio = Studio.query.get(studio_id)
    else:
        return error_message("bad_argument")

    if not isinstance(studio, Studio) or recorder not in ("gold", "show"):
        return error_message("bad_argument")

    recorder_name = "{}_recorder_{}".format(studio.slug, recorder)

    if liq.send_command("{}.status".format(recorder_name)) != "off":
        liq.send_command("{}.stop".format(recorder_name))
    else:
        logger.warn("Recorder {} was already off!".format(recorder_name))

    if element_id:
        # noinspection PyUnboundLocalVariable
        current_element.mark_as_done()
        studio.jukebox.curpos += 1

    studio.mark_as_changed()
    db.session.commit()

    return ok()


@celery.task()
def skip(studio_id, element_id):
    studio = Studio.query.get(studio_id)
    element = PlaylistElement.query.get(element_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    current_element = studio.jukebox.current_element

    if current_element != element:
        return error_message("bad_argument", "This playlist element is not the current element anymore.")

    liq.send_command("{}_jukebox_stereo.skip".format(studio.slug))
    current_element.mark_as_done(skipped=True)

    studio.jukebox.curpos += 1
    studio.jukebox.mark_as_changed()
    studio.mark_as_changed()

    db.session.commit()

    play_current_element.delay(studio.id)

    return ok()


@celery.task
def select_studio(element_id=None, studio_id=None):
    if element_id:
        current_element = PlaylistElement.query.get(element_id)

        if not current_element:
            return error_message("bad_argument")

        studio = current_element.playlist.studio
    elif studio_id:
        studio = Studio.query.get(studio_id)

        if not studio:
            return error_message("bad_argument")
    else:
        return error_message("bad_argument")

    liq.set_var("selected", studio.slug)

    # TODO: ensure all other studios are not selected anymore
    studio.selected = True
    studio.mark_as_changed()

    if element_id:
        # noinspection PyUnboundLocalVariable
        current_element.mark_as_done()
        studio.jukebox.curpos += 1

    studio.mark_as_changed()
    db.session.commit()

    play_current_element.delay(studio.id)


@celery.task()
def start_live(element_id=-1):
    playlist_element = PlaylistElement.query.get(element_id)

    if not playlist_element:
        return error_message("bad_argument")

    studio = playlist_element.playlist.studio

    liq.set_var("{}.jukebox.switch".format(studio.slug), False)
    liq.set_var("{}.plateau.volume".format(studio.slug), 1.0)

    return ok()


@celery.task()
def end_studio(element_id=-1):
    current_element = PlaylistElement.query.get(element_id)

    if not current_element:
        return error_message("bad_argument")

    studio = current_element.playlist.studio

    liq.set_var("selected", "permanent")

    studio.selected = False
    studio.mark_as_changed()

    current_element.mark_as_done()
    studio.jukebox.curpos += 1
    studio.mark_as_changed()
    db.session.commit()

    # DO NOT PLAY NEXT ELEMENT (stop here)
    liq.set_var("{}.jukebox.switch".format(studio.slug), False)

    return ok()


@celery.task()
def play_current_element(studio_id):
    studio = Studio.query.get(studio_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    current_element = studio.jukebox.current_element

    if current_element is None:
        logger.warning("Nothing to play or to do. Sleeping...")
        return ok()

    with redis_instance.lock("element_{}_play".format(current_element.id)):
        logger.debug("Refreshing current element {} (status={})".format(current_element.id, current_element.status))

        # Current element may have changed since we waited for the lock
        db.session.expire_all()
        current_element = db.session.query(PlaylistElement).get(studio.jukebox.current_element.id)

        logger.debug("Playing current element {} (status={})".format(current_element.id, current_element.status))

        if current_element.status == 'playing':
            logger.warning("Already playing (current_element={})...".format(current_element.id))
            return error_message("already_playing")

        elif current_element.status in ('ready', 'loaded'):
            if current_element.media:
                if liq.get_var("{}.jukebox.switch".format(studio.slug)) != "true":
                    logger.warn("Jukebox was not active, activating...")
                    liq.set_var("{}.jukebox.switch".format(studio.slug), True)

                if current_element.status == 'ready':
                    load_media(current_element.id, current_element.media, studio.jukebox_liqname)

            current_element.status = 'playing'
            current_element.on_air_since = datetime.datetime.now()
            studio.jukebox.mark_as_changed()
            db.session.commit()

            if current_element.media:
                timer = max(current_element.media.length - 2, 1)
                logger.warning("Scheduling task for {} seconds...".format(timer))
                check_next_element.s(studio.id, current_element.id).apply_async(countdown=timer)
            elif current_element.action:
                task_name_to_schedule = current_element.action.task
                celery.send_task(task_name_to_schedule, kwargs={"element_id": current_element.id})

    return ok()


def load_media(uid, media, liquidname):
    logger.warning(u"Loading media on {}, uid={}, mid={}, filename={}".format(liquidname, uid, media.id, media.filename))
    liq.send_command(u'{}.push annotate:dradis_uid="{}":{}'.format(liquidname, uid, media.path))


def update_element(element_id, live_content=None, comment=None):
    playlist_element = PlaylistElement.query.get(int(element_id))

    if not isinstance(playlist_element, PlaylistElement):
        return error_message("bad_argument")

    if live_content is not None:
        playlist_element.live_content = live_content
    if comment is not None:
        playlist_element.comment = comment

    if playlist_element.playlist:
        playlist_element.playlist.mark_as_changed()

    db.session.commit()

    return ok()


@celery.task()
def play_media_as_bed(studio_id, media_id):
    studio = Studio.query.get(studio_id)
    media = Media.query.get(media_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    if not isinstance(media, Media):
        return error_message("bad_argument")

    liq.set_var("{}.bed.switch".format(studio.slug), True)

    logger.debug("Setting media {} as bed on studio {}".format(media.id, studio.id))
    load_media("bed_{}".format(studio.id), media, studio.bed_liqname)

    timer = max(media.length - 2, 1)
    logger.warning("Scheduling bed looping in {} seconds...".format(timer))
    loop_bed.s(studio.id, media.id).apply_async(countdown=timer)

    studio.bed_on_air_since = datetime.datetime.now()
    studio.bed = media
    studio.mark_as_changed()
    db.session.commit()

    return ok(and_squack=True)


@celery.task()
def stop_bed(studio_id):
    studio = Studio.query.get(studio_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    studio.bed_on_air_since = None
    flush_bed(studio)

    studio.mark_as_changed()
    db.session.commit()

    return ok(and_squack=True)


@celery.task()
def set_bed_options(studio_id, repetition=None):
    studio = Studio.query.get(studio_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    if repetition is not None:
        studio.bed_repeat = repetition
        studio.mark_as_changed()

    db.session.commit()

    return ok(and_squack=True)


@celery.task()
def loop_bed(studio_id, media_id):
    studio = Studio.query.get(studio_id)

    if not isinstance(studio, Studio):
        return error_message("bad_argument")

    with redis_instance.lock("studio_{}_bed_lock".format(studio.id)):
        media = Media.query.get(studio.bed_id)

        if not isinstance(media, Media):
            return error_message("bad_argument")

        if media.id == media_id and studio.bed_on_air_since:
            last_reload_delta = (datetime.datetime.now() - studio.bed_on_air_since).total_seconds()

            if last_reload_delta < media.length - 10:
                logger.warning("Looping bed too fast! {} <= {}".format(last_reload_delta, media.length - 10))
            else:
                if studio.bed_repeat:
                    logger.debug("Looping media {} as bed on studio {}".format(media.id, studio.id))
                    load_media("bed_{}".format(studio.id), media, studio.bed_liqname)

                    timer = max((media.length - last_reload_delta) + media.length - 2, 1)
                    logger.warning("Scheduling bed looping in {} seconds...".format(timer))
                    loop_bed.s(studio.id, media.id).apply_async(countdown=timer)

                    studio.bed_on_air_since = datetime.datetime.now() + datetime.timedelta(seconds=max(0, media.length - last_reload_delta))
                else:
                    studio.bed_on_air_since = None

                studio.mark_as_changed()
                db.session.commit()

                return ok(and_squack=True)

    pass


def flush_bed(studio):
    liq.send_command(u'{}.skip'.format(studio.bed_liqname))
    # Twice: it may be already ready for looping
    liq.send_command(u'{}.skip'.format(studio.bed_liqname))

    studio.bed_on_air_since = None

    # should squack on return!


@worker_process_init.connect
def celery_worker_init_db(**_):
    db.init_app(app)
