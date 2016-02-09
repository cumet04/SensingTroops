#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
import copy
from common import get_dict
from flask import Flask, jsonify, render_template
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

# client = pymongo.MongoClient(host='192.168.0.21', port=27017)
# self.coll = client.test.tmp
# self.coll.insert_many(data)


class Captain(object):
    
    def __init__(self, name, addr, port):
        self._id = None
        self._name = name
        self._addr = addr
        self._port = port
        self._cache = []
        self._sgt_list = {}

    def get_info(self):
        logger.info('get self info')
        info = {
            'id': self._id,
            'name': self._name,
            'addr': self._addr,
            'port': self._port,
        }
        return info

    def accept_report(self, sgt_id, report):
        if sgt_id not in self._sgt_list:
            raise KeyError
        self._cache.append({'sgt_id': sgt_id, 'report': report})
        logger.info('accept work from pvt: {0}'.format(sgt_id))

    def accept_sgt(self, info):
        new_id = str(id(info))
        info['id'] = new_id

        self._sgt_list[new_id] = info
        logger.info('accept a new sergeant: {0}, {1}'.format(info['name'], new_id))
        return info

    def get_sgt_info(self, sgt_id):
        info = self._sgt_list[sgt_id]  # this may raise KeyError
        info['id'] = sgt_id
        return info

    def get_sgt_list(self):
        return list(self._sgt_list.keys())

    def generate_troops_info(self):
        cpt = self.get_info()

        # generate sgt list
        sgt_list = []
        for sgt in self._sgt_list.values():
            # get pvt id list
            ep = 'http://{0}:{1}/pvt/list'.format(sgt['addr'], sgt['port'])
            id_list = requests.get(ep).json()['pvt_list']

            # get pvt detail
            pvt_list = []
            for pvt_id in id_list:
                ep = 'http://{0}:{1}/pvt/{2}/info'.format(sgt['addr'], sgt['port'], pvt_id)
                pvt_info = requests.get(ep).json()
                pvt_list.append(pvt_info)

            # get sgt's cache
            ep = 'http://{0}:{1}/dev/cache'.format(sgt['addr'], sgt['port'])
            cache_list = [str(c) for c in requests.get(ep).json()['cache']]
            cache_text = json.dumps(cache_list, indent=4, separators=(',', ': '))

            # append sgt info
            sgt['pvt_list'] = pvt_list
            sgt['cache_text'] = cache_text
            sgt_list.append(sgt.copy())
        cpt['sgt_list'] = sgt_list

        # generate cpt's cache
        cache_list = copy.deepcopy(self._cache)
        for report in cache_list:
            report['report'] = [str(work) for work in report['report']]
        cpt['cache_text'] = json.dumps(cache_list, indent=4, separators=(',', ': '))
        return cpt


# REST interface ---------------------------------------------------------------

server = Flask(__name__)


@server.route('/sgt/join', methods=['POST'])
def sgt_join():
    value = get_dict()
    if value[1] != 200:
        return value

    res = app.accept_sgt(value[0])
    return jsonify(res)


@server.route('/sgt/<sgt_id>/report', methods=['POST'])
def sgt_report(sgt_id):
    value = get_dict()
    if value[1] != 200:
        return value

    try:
        app.accept_report(sgt_id, value[0])
    except KeyError:
        return jsonify(msg='the sgt is not my soldier'), 404
    return jsonify(result='success')


@server.route('/sgt/list', methods=['GET'])
def pvt_list():
    res = app.get_sgt_list()
    return jsonify({'sgt_list': res})


@server.route('/sgt/<sgt_id>/info', methods=['GET'])
def sgt_info(sgt_id):
    try:
        res = app.get_sgt_info(sgt_id)
    except KeyError:
        return jsonify(msg='the pvt is not my soldier'), 404
    return jsonify(res)


@server.route('/dev/cache', methods=['GET'])
def dev_cache():
    return jsonify(cache=app._cache)


@server.route('/web/status', methods=['GET'])
def show_status():
    return render_template("captain_ui.html", cpt = app.generate_troops_info())


# 自身の情報を返す
@server.route('/info', methods=['GET'])
def get_info():
    info = app.get_info()
    return jsonify(result='success', info=info), 200


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        self_port = int(sys.argv[1])
    else:
        self_port = 52000

    app = Captain('cpt-http', 'localhost', self_port)
    server.debug = True
    server.run(port=self_port, use_debugger = True, use_reloader = False)
