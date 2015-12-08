import json
import time
import os
import sys
import datetime
import threading

from flask import Flask, jsonify, request, url_for, abort, Response

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
from webapi import Request
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


class Sergeant():
    def __init__(self):
        # self.request = Request('192.168.1.142', '8080', 'sensor')
        self.request = Request('127.0.0.1', '5001', 'sensor')
        self.value_cache = []

        self.threads = {}
        self.sensing = { \
                'brightness': {'interval': 2}, \
                'temprature': {'interval': 1} \
        }

        # create sensing threads
        for sensor, params in self.sensing.items():
            th = threading.Timer(0, self.get_value, args=(sensor,))
            th.daemon = True
            th.start()
            self.threads[sensor] = th

        self.sender = threading.Timer(0, self.send_values, args=('', 10))
        self.sender.daemon = True
        self.sender.start()

    def get_value(self, sensor):
        response = self.request.executeGet(sensor)
        if response == None: return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response["timestamp"] = timestamp

        self.value_cache.append(response)
        logger.info('get: ' + str(response))

        interval = self.sensing[sensor]['interval']
        th = threading.Timer(interval, self.get_value, args=(sensor,))
        th.daemon = True
        th.start()
        self.threads[sensor] = th

    def send_values(self, dest, interval):
        # send
        # aaa(value_cache)
        logger.info('send: ' + str(self.value_cache))
        self.value_cache.clear()

        th = threading.Timer(interval, self.send_values, args=(dest, interval))
        th.daemon = True
        th.start()

    # server functions
    def set_config(self, config):
        logger.info(config)
        for sensor, params in config.items():
            if sensor in self.sensing:
                logger.info('exist')
                self.sensing[sensor] = params
            else:
                logger.info('new')
                self.sensing[sensor] = params
                th = threading.Timer(0, self.get_value, args=(sensor,))
                th.daemon = True
                th.start()
        return self.sensing



logger = Logger(__name__, INFO)
flask = Flask(__name__)
sergeant = Sergeant()

# Web API functions ------------------------------------------------------------

@flask.route('/intervals', methods=['GET', 'POST'])
def intervals():
    # load param
# TODO: implement POST
    config = request.args.get('config')
    if config == None: config = '{}'
    config = json.loads(config)

    # generate and return response
    response = jsonify(sergeant.set_config(config))
    response.status_code = 200
    return response


if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 5000
    flask.run(port=port)
