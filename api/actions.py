from flask import request, jsonify
from dradis.main import app
from dradis.common import tasks
from dradis.common.helpers import handle_errors, error_message, ok

# Models
from dradis.models.action import Action
from dradis.models.playlist import Playlist
from dradis.models.playlist_element import PlaylistElement
from dradis.models.studio import Studio


@app.route('/api/playlists/<int:playlist_id>/add', methods=['POST'])
def add_to_playlist(playlist_id):
    media_id = request.args.get('media_id')
    action_id = request.args.get('action_id')
    action_slug = request.args.get('action_slug')
    position = request.args.get('position')

    if position:
        position = int(position)

    if media_id:
        return handle_errors(tasks.add_content_to_playlist("media", int(media_id), int(playlist_id), position))

    elif action_id:
        return handle_errors(tasks.add_content_to_playlist("action", int(action_id), int(playlist_id), position))

    elif action_slug:
        action = Action.query.filter_by(slug=action_slug).first()

        if action:
            return handle_errors(tasks.add_content_to_playlist("action", action.id, int(playlist_id), position))
        else:
            return jsonify(error_message("bad_argument")), 400

    else:
        return jsonify(error_message("missing_parameters")), 400


@app.route('/api/playlists/<int:playlist_id>/remove', methods=['POST'])
def remove_from_playlist(playlist_id):
    playlist = Playlist.query.get(int(playlist_id))

    if playlist is None:
        return jsonify(error_message("unknown_playlist")), 400

    if request.args.get('element_id'):
        playlist_element = PlaylistElement.query.get(int(request.args.get('element_id')))

        if not playlist_element:
            return jsonify(error_message("unknown_element")), 400

        return handle_errors(tasks.remove_element_from_playlist(playlist_element.id, playlist.id))

    else:
        return jsonify(error_message("missing_parameters")), 400


@app.route('/api/elements/<int:element_id>/update', methods=['POST'])
def update_element(element_id):
    playlist_element = PlaylistElement.query.get(int(element_id))

    if playlist_element is None:
        return jsonify(error_message("unknown_element")), 400

    return handle_errors(tasks.update_element(playlist_element.id,
                                              live_content=request.form.get('live_content'),
                                              comment=request.form.get('comment')))


@app.route('/api/playlists/<int:playlist_id>/move', methods=['POST'])
def move_inside_playlist(playlist_id):
    playlist = Playlist.query.get(int(playlist_id))

    if playlist is None:
        return jsonify(error_message("unknown_playlist")), 400

    if request.args.get('element_id') and request.args.get('position') is not None:
        playlist_element = PlaylistElement.query.get(int(request.args.get('element_id')))
        position = int(request.args.get('position'))

        if not playlist_element:
            return jsonify(error_message("unknown_element")), 400

        return handle_errors(tasks.move_element_inside_playlist(playlist_element.id, position, playlist.id))

    else:
        return jsonify(error_message("missing_parameters")), 400


@app.route('/api/studios/<int:studio_id>/run', methods=['POST'])
def run_studio(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.play_current_element.delay(studio.id)

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/select_run', methods=['POST'])
def select_and_run_studio(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.select_studio.delay(studio_id=studio.id)

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/end_live', methods=['POST'])
def end_live(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.end_live.delay(studio.id)

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/record_show', methods=['POST'])
def record_show(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.record.delay(studio_id=studio.id, recorder="show")

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/record_gold', methods=['POST'])
def record_gold(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.record.delay(studio_id=studio.id, recorder="gold")

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/stop_record_show', methods=['POST'])
def stop_record_show(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.end_record.delay(studio_id=studio.id, recorder="show")

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/stop_record_gold', methods=['POST'])
def stop_record_gold(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.end_record.delay(studio_id=studio.id, recorder="gold")

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/skip', methods=['POST'])
def skip(studio_id):
    studio = Studio.query.get(int(studio_id))
    element_id = request.args.get('element_id')

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.skip.delay(studio.id, element_id)

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/start_bed', methods=['POST'])
def start_bed(studio_id):
    studio = Studio.query.get(int(studio_id))
    media_id = request.args.get('media_id')

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.play_media_as_bed.delay(studio.id, media_id)

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/stop_bed', methods=['POST'])
def stop_bed(studio_id):
    studio = Studio.query.get(int(studio_id))

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.stop_bed.delay(studio.id)

    return handle_errors(ok())


@app.route('/api/studios/<int:studio_id>/bed_options', methods=['POST'])
def set_bed_options(studio_id):
    studio = Studio.query.get(int(studio_id))
    repetition = request.args.get('repetition', None)
    if repetition is not None:
        repetition = repetition == "true"

    if studio is None:
        return jsonify(error_message("unknown_studio")), 400

    tasks.set_bed_options.delay(studio.id, repetition=repetition)

    return handle_errors(ok())
