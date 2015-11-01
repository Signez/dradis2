import json
import redis
from dradis.common.websocket import WebsocketBroadcaster
from dradis.main import app, ws

redis_instance = redis.StrictRedis()

@ws.route('/ws/broadcast')
def ws_broadcast(client):
    with app.app_context():
        msg = client.receive()
        if msg != 'LOGIN={}'.format(app.config["DRADIS_API_KEY"]):
            print "Recevied {}, disconnecting.".format(msg)
            client.send(json.dumps({"error": "Wrong API Key, aborting now !", "error_code": 403}))
            return

        pubsub = redis_instance.pubsub(ignore_subscribe_messages=True)
        ws_broadcaster = WebsocketBroadcaster(client, pubsub)
        ws_broadcaster.run(initial_data=redis_instance.get('agency_json_status'))
