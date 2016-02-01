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
            return jsonify(msg='the pvt is not my soldier'), 403

        self.cache.append({'pvt_id':id, 'work':work})
        return jsonify(res='ok')


    def add_pvt(self, info):
        new_id = str(id(info))
        self.pvt_list[new_id] = {'info':info}
        return jsonify(res='ok', id=new_id)


    def show_cache(self):
        return jsonify(cache = self.cache)




# REST interface ---------------------------------------------------------------

app = Sergeant()
server = Flask(__name__)


@server.route('/pvt/join', methods=['POST'])
def pvt_join():
    input = get_dict()
    if input[1] != 200: return input

    res = app.add_pvt(input[0])
    return res


@server.route('/pvt/<id>/work', methods=['POST'])
def pvt_work(id):
    input = get_dict()
    if input[1] != 200: return input

    return app.accept_work(id, input[0])


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


