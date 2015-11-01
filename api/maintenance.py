import json
import redis
from flask import jsonify
from dradis.main import app
from dradis.common import utilities
from dradis.common.helpers import iso8601

redis_instance = redis.StrictRedis()


@app.route('/api/maintenance/bootstrap', methods=['POST'])
def maintenance_bootstrap():
    generated_studios = utilities.generate_studios()
    attached_empty_playlists = utilities.attach_empty_playlists()
    added_default_actions = utilities.add_default_actions()

    return jsonify({
        "status": "done",
        "generated_studios": generated_studios,
        "attached_empty_playlists": attached_empty_playlists,
        "added_default_actions": added_default_actions
    })


@app.route('/api/maintenance/rescan', methods=['POST'])
def maintenance_rescan():
    return jsonify({
        "status": "done",
        "result": utilities.rescan()
    })


@app.route('/api/maintenance/status')
def maintenance_status():
    liquidsoap_status = redis_instance.get("liquidsoap_json_status")

    try:
        liquidsoap_status = json.loads(liquidsoap_status)
    except (TypeError, ValueError):
        liquidsoap_status = None

    agency_status = redis_instance.get("agency_json_status")

    try:
        agency_status = json.loads(agency_status)
    except (TypeError, ValueError):
        agency_status = None

    return jsonify({
        "last_liquidsoap_update": iso8601(redis_instance.get("liquidsoap_json_updated_at")),
        "last_agency_update": iso8601(redis_instance.get("agency_updated_at")),
        "liquidsoap_status": liquidsoap_status,
        "agency_status": agency_status
    })
