import json
import redis
from dradis.common import status
from dradis.main import app
from dradis.models import db
from time import gmtime, strftime, time

db.init_app(app)
redis_instance = redis.StrictRedis()


def formatted_now():
    return strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


def start_journalism():
    newsfeed = redis_instance.pubsub(ignore_subscribe_messages=True)

    newsfeed.subscribe('agency')

    for message in newsfeed.listen():
        liquidsoap_json_status = redis_instance.get('liquidsoap_json_status')
        liquidsoap_json_updated_at = redis_instance.get('liquidsoap_json_updated_at')
        current_status = status.system_status(liquidsoap_json_status, liquidsoap_json_updated_at)

        json_status = json.dumps(current_status)
        redis_instance.publish('broadcaster', json_status)

        redis_instance.set("agency_json_status", json_status)
        redis_instance.set('agency_updated_at', round(time() * 1000))


if __name__ == '__main__':
    print "Starting agency at {}...".format(formatted_now())
    start_journalism()
