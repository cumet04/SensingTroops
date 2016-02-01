#!/usr/bin/python3
# -*- coding: utf-8 -*-

from logging import getLogger,StreamHandler,DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

import json
import os
import sys
import threading
import time
import logging
import hashlib
from common import get_dict
from flask import Flask, jsonify, request, url_for, abort, Response

class Sergeant(object):
    def __init__(self):
        self.cache = []
        self.pvt_list = {}
        self.config = None

    def working(self):
        # ask job
        # submit report
        pass

    def join(self):
        pass

    def accept_work(self, id, work):
        if id not in self.pvt_list:
            return jsonify(msg='the pvt is not my soldier'), 404

        self.cache.append({'pvt_id':id, 'work':work})
        logger.info('accept work from pvt: {0}'.format(id))
        return jsonify(result='success')

    def accept_pvt(self, info):
        new_id = str(id(info))
        self.pvt_list[new_id] = {'info':info}
        logger.info('accept a new private: {0}, {1}'.format(info['name'], id))
        return jsonify(result='success', name=info['name'], id=new_id)

    def get_pvt_info(self, id):
        if id not in self.pvt_list:
            return jsonify(msg='the pvt is not my soldier'), 404
        info = self.pvt_list[id]
        info['id'] = id
        return jsonify(info)

    def show_cache(self):
        return jsonify(cache = self.cache)




# REST interface ---------------------------------------------------------------

app = Sergeant()
server = Flask(__name__)


@server.route('/pvt/join', methods=['POST'])
def pvt_join():
    input = get_dict()
    if input[1] != 200: return input

    res = app.accept_pvt(input[0])
    return res

@server.route('/pvt/<id>/work', methods=['POST'])
def pvt_work(id):
    input = get_dict()
    if input[1] != 200: return input

    res = app.accept_work(id, input[0])
    return res

@server.route('/pvt/<id>/info', methods=['GET'])
def pvt_info(id):
    res = app.get_pvt_info(id)
    return res

@server.route('/dev/cache', methods=['GET'])
def dev_cache():
    return app.show_cache()


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 5000
    server.run(port=port, debug=True)


