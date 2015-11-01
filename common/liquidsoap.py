import socket
import threading
import time
import telnetlib

from celery.utils.log import get_task_logger
import redis

logger = get_task_logger(__name__)

redis_instance = redis.StrictRedis()


class LiquidsoapConnection:
    def __init__(self):
        self.lock = threading.Lock()
        self.shared_connection = None
        pass
    
    def create_connection(self, retries=0):
        return telnetlib.Telnet('127.0.0.1', 1234)

    def send_command(self, thecommand):
        with redis_instance.lock("liquidsoap_lock", timeout=10, blocking_timeout=10):
            telnet = self.create_connection()

            telnet.write(thecommand.encode('utf-8') + '\r\n')

            try:
                data = telnet.read_until("END", 2)
                telnet.write("exit\n")
            except EOFError:
                logger.error("Got EOF while reading Liquidsoap! Command was {}".format(thecommand))
                return None

            result = data.lstrip().rstrip()

            if result == "":
                return "0.0"
            else:
                return result

    @staticmethod
    def parse_metadatas(metadatas):
        try:
            return dict([(el[0], el[1][1:-1]) for el in [el.split('=') for el in metadatas.split('\n')]])
        except IndexError:
            retour = {}
            for el in metadatas.split('\n'):
                if '=' in el:
                    sp = el.split('=')
                    retour[sp[0]] = "=".join(el[1:])[1:-1]
            return retour

    @staticmethod
    def parse_date(liqdate):
        try:
            return time.mktime(time.strptime(liqdate, '%Y/%m/%d %H:%M:%S'))
        except ValueError:
            return None

    @staticmethod
    def format_value(value):
        if type(value) is bool:
            if value:
                return '"true"'
            else:
                return '"false"'

        elif type(value) is int:
            return float(value)

        elif type(value) is float:
            return repr(value)

        elif type(value) is str or type(value) is unicode:
            return '"{}"'.format(value)

        else:
            return ""

    def set_var(self, variable_name, value):
        formatted_value = self.format_value(value)

        logger.info("Setting {} to {}".format(variable_name, formatted_value))

        return self.send_command("var.set %s = %s" % (variable_name, formatted_value))

    def get_var(self, variable_name):
        value = self.send_command("var.get %s" % variable_name)
        if value is None:
            return None
        elif value.strip().endswith("is not defined."):
            logger.error("Liquidsoap returned an error. {}".format(value))
            return None
        elif type(value) is str or type(value) is unicode:
            return value.strip('"')
        else:
            return value
