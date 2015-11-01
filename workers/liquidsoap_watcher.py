import socket
import time
import redis

redis_instance = redis.StrictRedis()
liquidsoap_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_liquidsoap():
    global liquidsoap_connection

    try:
        liquidsoap_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        liquidsoap_connection.connect(('127.0.0.1', 1234))
        return True
    except socket.error, details:
        print str(details)
        return False


def run():
    retry_delay = 0.2

    while True:
        connection_available = connect_to_liquidsoap()

        if not connection_available:
            print "Waiting for {} seconds before retry...".format(retry_delay)
            time.sleep(retry_delay)
            retry_delay *= 2
            retry_delay = min(retry_delay, 30)

        while connection_available:
            retry_delay = 0.2

            try:
                liquidsoap_connection.send("json_status\r\n")
                data = ""

                while "\r\nEND\r\n" not in data:
                    last_received = liquidsoap_connection.recv(1024)

                    if len(last_received):
                        data += last_received
                    else:
                        connection_available = False
                        print "Liquidsoap closed the connection."
                        break

                data = data.replace("\r\nEND\r\n", '').lstrip().rstrip()

                cached_data = redis_instance.get("liquidsoap_json_status")

                if cached_data != data:
                    redis_instance.set("liquidsoap_json_status", data)
                    redis_instance.publish('agency', 'json_status_update')

                redis_instance.set("liquidsoap_json_updated_at", round(time.time() * 1000))

                time.sleep(0.2)
            except socket.error, details:
                print str(details)
                connection_available = False


if __name__ == '__main__':
    run()
