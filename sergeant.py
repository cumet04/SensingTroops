#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import threading
import requests
from common import get_dict
from flask import Flask, jsonify
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Sergeant(object):
    def __init__(self):
        self.cache = []
        self.pvt_list = {}
        self.superior_ep = ''
        self.id = ''
        self.report_timer = None
        self.report_interval = 0

# soldier functions

    def join(self, addr, port):
        self.superior_ep = addr + ':' + port
        logger.info('join into the captain: {0}'.format(self.superior_ep))

        info = {'name': "sgt-skel"}
        path = 'http://{0}/sgt/join'.format(self.superior_ep)
        res = requests.post(path, json=info).json()

        self.id = res['id']
        logger.info('get my sgt-id: {0}'.format(self.id))

    def report(self):
        if self.report_interval == 0:
            return
        if self.report_timer is not None:
            self.report_timer.cancel()

        t = threading.Timer(self.report_interval, self.report)
        t.start()
        self.report_timer = t

        path = 'http://{0}/sgt/{1}/report'.format(self.superior_ep, self.id)
        return requests.post(path, json=self.cache)

# superior functions

    def accept_work(self, pvt_id, work):
        if pvt_id not in self.pvt_list:
            raise KeyError
        self.cache.append({'pvt_id': pvt_id, 'work': work})
        logger.info('accept work from pvt: {0}'.format(pvt_id))

    def accept_pvt(self, info):
        new_id = str(id(info))
        name = info['name']

        self.pvt_list[new_id] = info
        logger.info('accept a new private: {0}, {1}'.format(name, new_id))
        return {'name': name, 'id': new_id}

    def get_pvt_info(self, pvt_id):
        info = self.pvt_list[pvt_id]
        info['id'] = pvt_id
        return info


# REST interface ---------------------------------------------------------------

server = Flask(__name__)


@server.route('/pvt/join', methods=['POST'])
def pvt_join():
    value = get_dict()
    if value[1] != 200:
        return value

    res = app.accept_pvt(value[0])
    return jsonify(res)


@server.route('/pvt/<pvt_id>/work', methods=['POST'])
def pvt_work(pvt_id):
    value = get_dict()
    if value[1] != 200:
        return value

    try:
        app.accept_work(pvt_id, value[0])
    except KeyError:
        return jsonify(msg='the pvt is not my soldier'), 404
    return jsonify(result='success')


@server.route('/pvt/<pvt_id>/info', methods=['GET'])
def pvt_info(pvt_id):
    try:
        res = app.get_pvt_info(pvt_id)
    except KeyError:
        return jsonify(msg='the pvt is not my soldier'), 404
    return jsonify(res)


@server.route('/dev/cache', methods=['GET'])
def dev_cache():
    return jsonify(app.cache)


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 4:
        self_port = int(sys.argv[1])
        su_addr = sys.argv[2]
        su_port = sys.argv[3]
    else:
        logger.error('superior addr/port required')
        sys.exit()
    app = Sergeant()
    app.join(su_addr, su_port)
    server.run(port=self_port, debug=True)
