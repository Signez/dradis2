import os
import logging
import magic
import json

from flask import request, jsonify
from dradis.main import app
from dradis.common import utilities
from dradis.common.helpers import error_message, squack


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ['ogg', 'mp3', 'oga']


def allowed_file_type(filepath):
    human_readable_type = magic.from_file(filepath)

    if "audio" not in human_readable_type.lower():
        logging.warn("Received dubious '{}' file type".format(human_readable_type))
        return False
    else:
        return True


def decorate_filename(filename, kind, username):
    return "{username}__{kind}__{filename}".format(
        filename=filename,
        kind=kind,
        username=username
    )


@app.route('/api/upload', methods=['POST'])
def upload_media():
    kind = request.args.get('kind')
    username = 'nobody'  # FIXME: Add account support
    uploaded_file = request.files['file']

    if uploaded_file:
        filename = utilities.secure_filename(uploaded_file.filename)
        filename = decorate_filename(filename, kind, username)
        new_path = os.path.join(app.config['MEDIA_ROOT'], 'uploads', filename)
        uploaded_file.save(new_path)

        if not allowed_file(uploaded_file.filename) or not allowed_file_type(new_path):
            os.remove(new_path)
            return jsonify(error_message("not_allowed"))

        squack()

        return jsonify({
            "status": "done",
            "result": new_path.replace(app.config['MEDIA_ROOT'], app.config['MEDIA_URL'])
        })
    else:
        return jsonify(error_message("not_received_file"))


@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    filename = request.args.get('filename')

    uploads_dir = os.path.join(app.config.get('MEDIA_ROOT'), "uploads")

    if filename not in os.listdir(uploads_dir):
        return jsonify(error_message("not_allowed"))

    filepath = os.path.join(uploads_dir, filename)

    tags = utilities.tags_for_file(filepath)

    return jsonify(dict({
        "status": "done",
    }.items() + tags.items()))


@app.route('/api/library/add', methods=['POST'])
def add_to_library():
    filename = request.args.get('filename')
    tags = request.form['tags']

    uploads_dir = os.path.join(app.config.get('MEDIA_ROOT'), "uploads")

    if filename not in os.listdir(uploads_dir):
        return jsonify(error_message("not_allowed"))

    try:
        tags = json.loads(tags)
    except ValueError:
        return jsonify(error_message("bad_request"))

    # FIXME: Filter allowed tags
    tags["ORIGINALFILENAME"] = filename.split('__', 2)[2]

    filepath = os.path.join(uploads_dir, filename)

    utilities.write_tags(filepath, tags)

    new_path = utilities.generate_new_path(filepath)

    if not os.path.isdir(os.path.dirname(new_path)):
        os.makedirs(os.path.dirname(new_path))

    os.rename(filepath, new_path)

    utilities.rescan()

    return jsonify({
        "status": "done"
    })
