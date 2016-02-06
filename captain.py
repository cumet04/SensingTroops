#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

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
    
    def __init__(self, name):
        self._id = None
        self._name = name
        self._addr = None
        self._port = 0
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
        name = info['name']

        self._sgt_list[new_id] = info
        logger.info('accept a new sergeant: {0}, {1}'.format(name, new_id))
        return {'name': name, 'id': new_id}

    def get_sgt_info(self, sgt_id):
        info = self._sgt_list[sgt_id]  # this may raise KeyError
        info['id'] = sgt_id
        return info

    def get_sgt_list(self):
        return list(self._sgt_list.keys())


# REST interface ---------------------------------------------------------------

app = Captain('cpt-http')
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
    sgt_list = []
    for sgt_id in app.get_sgt_list():
        pvt_list =[{'id': 'test-pvt-id1'}, {'id': 'test-pvt-id2'}]
        sgt = {'id': sgt_id, 'pvt_list': pvt_list}
        sgt_list.append(sgt)
    cpt = {
        'id': 'cpt-id',
        'sgt_list': sgt_list
    }
    return render_template("captain_ui.html", cpt = cpt)


# 自身の情報を返す
@server.route('/info', methods=['GET'])
def get_info():
    value = get_dict()
    if value[1] != 200:
        return value

    info = app.get_info()
    return jsonify(result='success', info=info), 200


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 5100
    app.info['port'] = port
    app.info['addr'] = 'localhost'
    server.debug = True
    server.run(port=port)
