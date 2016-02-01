#!/usr/bin/python3
# -*- coding: utf-8 -*-

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

import os
import sys
import threading
from common import get_dict
from flask import Flask, jsonify

class Sergeant(object):
    def __init__(self):
        self.cache = []
        self.pvt_list = {}

    def working(self):
        # ask job
        # submit report
        pass

    def join(self):
        pass

    def accept_work(self, id, work):
        if id not in self.pvt_list:
            raise KeyError
        self.cache.append({'pvt_id':id, 'work':work})
        logger.info('accept work from pvt: {0}'.format(id))

    def accept_pvt(self, info):
        new_id = str(id(info))
        name = info['name']

        self.pvt_list[new_id] = info
        logger.info('accept a new private: {0}, {1}'.format(name, new_id))
        return {'name': name, 'id': new_id}

    def get_pvt_info(self, id):
        info = self.pvt_list[id]
        info['id'] = id
        return info



# REST interface ---------------------------------------------------------------

app = Sergeant()
server = Flask(__name__)


@server.route('/pvt/join', methods=['POST'])
def pvt_join():
    input = get_dict()
    if input[1] != 200: return input

    res = app.accept_pvt(input[0])
    return jsonify(res)

@server.route('/pvt/<id>/work', methods=['POST'])
def pvt_work(id):
    input = get_dict()
    if input[1] != 200: return input

    try:
        app.accept_work(id, input[0])
    except KeyError:
        return jsonify(msg='the pvt is not my soldier'), 404
    return jsonify(result='success')

@server.route('/pvt/<id>/info', methods=['GET'])
def pvt_info(id):
    try:
        res = app.get_pvt_info(id)
    except KeyError:
        return jsonify(msg='the pvt is not my soldier'), 404
    return jsonify(res)

@server.route('/dev/cache', methods=['GET'])
def dev_cache():
    return jsonify(app.cache)


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 5000
    server.run(port=port, debug=True)


