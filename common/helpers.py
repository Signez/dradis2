import redis
from flask import jsonify
from datetime import datetime
from dradis.sqlalchemy_jsonapi import JSONAPI
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)
redis_instance = redis.StrictRedis()


def error_message(message, details=None):
    payload = {
        "type": "error",
        "error_message": message
    }

    if details:
        payload["details"] = details

    logger.error("Returning error: {}.".format(message))

    return payload


def ok(and_squack=True):
    if and_squack:
        squack()

    return {
        "type": "result",
        "message": "ok"
    }


def squack():
    """
    Send a new status message to every client.
    :return:
    """
    redis_instance.publish("agency", "squack")


def handle_errors(payload):
    if payload is None:
        return jsonify(error_message("internal_server_error")), 500
    elif "type" in payload and payload["type"] == "error":
        return jsonify(payload), 400
    else:
        return jsonify(payload), 200


def iso8601(milliseconds):
    milliseconds = float(milliseconds)

    return datetime.fromtimestamp(milliseconds / 1000.0).strftime("%Y-%m-%dT%H:%M:%S")


class JSONSerializer(JSONAPI):
    converters = {
        'unicode': unicode,
        'datetime': lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")
    }


def forge_url(model, id):
    if model in ["jukebox"]:
        return "/api/playlists/{}".format(id)

    elif model in ["elements"]:
        return [int(each_id) for each_id in id]

    else:
        if id:
            return id
        else:
            return None


# It is so ugly, omg. Should patch SQLAlchemy-JSONAPI instead!
def add_url_to_links(payload):
    if isinstance(payload, dict):
        for key in payload.keys():
            if key == "links":
                ids = payload[key]
                links = {}
                for model in ids.keys():
                    url = forge_url(model, ids[model])

                    if isinstance(url, str):
                        links[model] = url
                    else:
                        payload[model] = url
                payload[key] = links
            elif isinstance(payload[key], list) or isinstance(payload[key], dict):
                payload[key] = add_url_to_links(payload[key])
        return payload
    elif isinstance(payload, list):
        return [add_url_to_links(element) for element in payload]
    else:
        return payload


def sanitize(json_api_dict):
    if "linked" in json_api_dict.keys():
        for key in json_api_dict["linked"]:
            json_api_dict[key] = json_api_dict["linked"][key]
        json_api_dict.pop("linked")

    return add_url_to_links(json_api_dict)
