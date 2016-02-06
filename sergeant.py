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
    def __init__(self, name):
        self._id = ''
        self._name = name
        self._addr = None
        self._port = 0
        self._superior_ep = ''

        self._cache = []
        self._pvt_list = {}
        self.report_timer = None
        self.report_interval = 0

# soldier functions

    def join(self, addr, port):
        """
        指定された上官に入隊申請を行う
        :param str addr: 上官のIPアドレス
        :param str port: 上官のポート番号
        :rtype: str
        :return: id
        """
        self._superior_ep = addr + ':' + port
        logger.info('join into the captain: {0}'.format(self._superior_ep))

        path = 'http://{0}/sgt/join'.format(self._superior_ep)
        res = requests.post(path, json=self.get_info()).json()

        self._id = res['id']
        logger.info('get my sgt-id: {0}'.format(self._id))
        return self._id

    def get_info(self):
        logger.info('get self info')
        info = {
            'id': self._id,
            'name': self._name,
            'addr': self._addr,
            'port': self._port,
        }
        return info

    def report(self):
        if self.report_interval == 0:
            return
        if self.report_timer is not None:
            self.report_timer.cancel()

        t = threading.Timer(self.report_interval, self.report)
        t.start()
        self.report_timer = t

        path = 'http://{0}/sgt/{1}/report'.format(self._superior_ep, self._id)
        return requests.post(path, json=self._cache)

    def set_job(self, job_list):
        """
        この兵士に割り当てられている任務を置き換える
        :param job_list: 新規任務のリスト
        :return: 受理した命令
        """
        accepted = []
        for item in job_list:
            if item['subject'] != 'report':
                continue
            self.report_interval = item['interval']
            self.report()
            accepted.append(item)

        logger.info('accepted new jobs')
        logger.debug('new jobs: {0}'.format(str(accepted)))
        return accepted

# superior functions

    def accept_work(self, pvt_id, work):
        if pvt_id not in self._pvt_list:
            raise KeyError
        self._cache.append({'pvt_id': pvt_id, 'work': work})
        logger.info('accept work from pvt: {0}'.format(pvt_id))

    def accept_pvt(self, info):
        new_id = str(id(info))
        name = info['name']

        self._pvt_list[new_id] = info
        logger.info('accept a new private: {0}, {1}'.format(name, new_id))
        return {'name': name, 'id': new_id}

    def get_pvt_info(self, pvt_id):
        info = self._pvt_list[pvt_id]
        info['id'] = pvt_id
        return info

    def get_pvt_list(self):
        return list(self._pvt_list.keys())


# REST interface ---------------------------------------------------------------

app = Sergeant('sgt-http')
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


@server.route('/pvt/list', methods=['GET'])
def pvt_list():
    res = app.get_pvt_list()
    return jsonify({'pvt_list': res})


@server.route('/pvt/<pvt_id>/info', methods=['GET'])
def pvt_info(pvt_id):
    try:
        res = app.get_pvt_info(pvt_id)
    except KeyError:
        return jsonify(msg='the pvt is not my soldier'), 404
    return jsonify(res)


@server.route('/sgt/job', methods=['PUT'])
def get_order():
    value = get_dict()
    if value[1] != 200:
        return value

    accepted = app.set_job(value[0])
    return jsonify(result='success', accepted=accepted), 200


# 自身の情報を返す
@server.route('/info', methods=['GET'])
def get_info():
    value = get_dict()
    if value[1] != 200:
        return value

    info = app.get_info()
    return jsonify(result='success', info=info), 200


@server.route('/dev/cache', methods=['GET'])
def dev_cache():
    return jsonify(cache=app._cache)


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 4:
        self_port = int(sys.argv[1])
        su_addr = sys.argv[2]
        su_port = sys.argv[3]
    else:
        logger.error('superior addr/port required')
        sys.exit()
    app.join(su_addr, su_port)
    # server.debug = True
    server.run(port=self_port)
