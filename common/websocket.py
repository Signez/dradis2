from collections import Mapping
from flask import json
import time


def diffed(original, challenger):
    result = challenger.copy()
    for k in challenger:
        if k in original:
            if isinstance(challenger[k], Mapping):
                result[k] = diffed(original[k], challenger[k])
                if not len(result[k]):
                    del result[k]
            else:
                if original[k] == challenger[k]:
                    del result[k]
    return result


class WebsocketBroadcaster():
    def __init__(self, client, pubsub):
        self.api_key = ""
        self.cache = {}
        self.throttler = 0
        self.client = client
        self.pubsub = pubsub
        self.pubsub.subscribe('broadcaster')

    def send_message(self, message):
        self.client.send(message)

    def send_ping(self):
        self.client.send(json.dumps({"type": "ping", "serverTime": int(time.time())}))

    def smart_send(self, message):
        if self.throttler % 10:
            diff = diffed(self.cache, message)
            diff["type"] = "diff_status"
            self.send_message(json.dumps(diff).strip('\n').encode('utf-8'))
        else:
            self.send_message(json.dumps(message).strip('\n').encode('utf-8'))

        self.cache = message

        self.throttler += 1

    def run(self, initial_data=None):
        try:
            if initial_data:
                self.smart_send(json.loads(initial_data))

            i = 0

            while True:
                message = self.pubsub.get_message()
                self.client.recv_nb()  # flush
                if message:
                    self.smart_send(json.loads(message["data"]))
                    i = 0
                else:
                    if i > 50:
                        self.send_ping()
                        self.client.recv_nb()  # flush
                        i = 0
                    else:
                        i += 1
                time.sleep(0.02)
        except IOError:
            return
