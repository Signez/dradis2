from flask import request, jsonify
from sqlalchemy import or_
from dradis.main import app
from dradis.common.helpers import JSONSerializer, sanitize, squack

# Models
from dradis.models.antenna import Antenna
from dradis.models.action import Action
from dradis.models.episode import Episode
from dradis.models.media import Media
from dradis.models.playlist import Playlist
from dradis.models.playlist_element import PlaylistElement
from dradis.models.studio import Studio
from dradis.models.show import Show


@app.route('/api/playlist_elements')
def list_playlist_element():
    playlist_element_serializer = JSONSerializer(PlaylistElement)
    query = PlaylistElement.query.limit(request.args.get('limit'))
    return jsonify(sanitize(playlist_element_serializer.serialize(query)))

@app.route('/api/media')
def list_medias():
    media_serializer = JSONSerializer(Media)
    query = Media.query

    if request.args.get('fulltext'):
        fulltext = request.args.get('fulltext')
        wrapped_fulltext = u'%{}%'.format(fulltext)
        query = query.filter(or_(Media.title.ilike(wrapped_fulltext), Media.artist.ilike(wrapped_fulltext),
                                 Media.album.ilike(wrapped_fulltext), Media.filename.ilike(wrapped_fulltext)))

    sort = request.args.get('sort', 'title')
    desc = sort[0] == "-"
    sort = sort.lstrip('-')

    column = getattr(Media, sort, None)

    if column:
        if desc:
            query = query.order_by(column.desc().nullslast())
        else:
            query = query.order_by(column.asc().nullslast())
    else:
        return jsonify({"error": "bad_argument"}), 400

    if request.args.get('limit'):
        query = query.limit(int(request.args.get('limit')))
    else:
        query = query.limit(10)

    if request.args.get('offset'):
        query = query.offset(int(request.args.get('offset')))

    return jsonify(sanitize(media_serializer.serialize(query)))


@app.route('/api/media/<int:media_id>')
def show_medias(media_id):
    media_serializer = JSONSerializer(Media)
    media = Media.query.get(media_id)

    if media:
        return jsonify(sanitize(media_serializer.serialize(media)))
    else:
        return jsonify({"error": "not_found"}), 404


@app.route('/api/actions')
def list_actions():
    action_serializer = JSONSerializer(Action)
    query = Action.query.limit(request.args.get('limit'))

    return jsonify(sanitize(action_serializer.serialize(query)))


@app.route('/api/actions/<int:action_id>')
def show_actions(action_id):
    action_serializer = JSONSerializer(Action)
    action = Action.query.get(action_id)

    if action:
        return jsonify(sanitize(action_serializer.serialize(action)))
    else:
        return jsonify({"error": "not_found"}), 404


@app.route('/api/studios')
def list_studios():
    studio_serializer = JSONSerializer(Studio)
    query = Studio.query.limit(request.args.get('limit')).order_by(Studio.slug)

    squack()

    return jsonify(sanitize(studio_serializer.serialize(query)))


@app.route('/api/studios/<int:studio_id>')
def show_studio(studio_id):
    studio_serializer = JSONSerializer(Studio)
    studio = Studio.query.get(studio_id)

    if studio:
        return jsonify(sanitize(studio_serializer.serialize(studio)))
    else:
        return jsonify({"error": "not_found"}), 404


@app.route('/api/playlists')
def list_playlists():
    playlist_serializer = JSONSerializer(Playlist)
    query = Playlist.query.limit(request.args.get('limit'))
    return jsonify(sanitize(playlist_serializer.serialize(query, include=[])))


@app.route('/api/playlists/<int:playlist_id>')
def show_playlist(playlist_id):
    playlist_serializer = JSONSerializer(Playlist)
    playlist = Playlist.query.get(playlist_id)

    if playlist is not None:
        sideloaded = ["elements", "elements.media", "elements.action"]
        return jsonify(sanitize(playlist_serializer.serialize(playlist, include=sideloaded)))
    else:
        return jsonify({"error": "not_found"}), 404
