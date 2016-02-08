#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import threading
import requests
from common import get_dict
from flask import Flask, jsonify, request
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Sergeant(object):
    def __init__(self, name, addr, port):
        self._id = ''
        self._name = name
        self._addr = addr
        self._port = port
        self._superior_ep = ''

        self._cache = []
        self._pvt_list = {}
        self.job_list = {
            'report': None,
            'command': [],
        }
        self.job_wait_events = {
            'report': None,
            'command': [],
        }

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

    def set_report(self, report):
        # 既存のreportスレッドを消す
        if self.job_wait_events['report'] is not None:
            self.job_wait_events['report'].set()
        self.job_wait_events['report'] = None

        # TODO: reportが受理可能なものであるかのチェック
        event = threading.Event()
        t = threading.Thread(target = self._report_thread, args = (report, event))
        t.start()
        self.job_wait_events['report'] = event
        self.job_list['report'] = report

        logger.info('accepted new job: report')
        logger.debug('new job: {0}'.format(str(report)))
        return report

    def set_commands(self, command_list):
        if not isinstance(command_list, list):
            command_list = [command_list]

        # 既存のcommandスレッドを消す
        map(lambda w: w.set(), self.job_wait_events['command'])
        self.job_wait_events['command'] = []

        accepted = []
        for command in command_list:
            # TODO: commandが受理可能なものであるかのチェック
            event = threading.Event()
            t = threading.Thread(target = self._command_thread, args = (command, event))
            t.start()
            self.job_wait_events['command'].append(event)
            accepted.append(command)

        logger.info('accepted new jobs: command')
        logger.debug('new jobs: {0}'.format(str(accepted)))
        self.job_list['command'] = accepted
        return accepted

    def _command_thread(self, command, event):
        # oneshotなcommandのみ暫定実装. eventはスルー
        target = []
        if command['target'] == 'all':
            target = self.get_pvt_list()
        order = command['order']

        for pvt in [self._pvt_list[id] for id in target]:
            path = 'http://{0}:{1}/order'.format(pvt['addr'], pvt['port'])
            requests.put(path, json={'orders': order})

    def _report_thread(self, command, event):
        interval = command['interval']
        # filter = command['filter']
        # encoding = command['encoding']

        # if event is set, exit the loop
        while not event.wait(timeout = interval):
            path = 'http://{0}/sgt/{1}/report'.format(self._superior_ep, self._id)
            requests.post(path, json=self._cache)
            self._cache = []

# superior functions

    def accept_work(self, pvt_id, work):
        if pvt_id not in self._pvt_list:
            raise KeyError
        self._cache.append({'pvt_id': pvt_id, 'work': work})
        logger.info('accept work from pvt: {0}'.format(pvt_id))

    def accept_pvt(self, info):
        new_id = str(id(info))
        name = info['name']
        info['id'] = new_id

        self._pvt_list[new_id] = info
        logger.info('accept a new private: {0}, {1}'.format(name, new_id))
        return info

    def get_pvt_info(self, pvt_id):
        return self._pvt_list[pvt_id]

    def get_pvt_list(self):
        return list(self._pvt_list.keys())


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


@server.route('/sgt/job/report', methods=['GET', 'PUT'])
def setjob_report():
    report = None
    if request.method == 'GET':
        report = app.job_list['report']
    elif request.method == 'PUT':
        value = get_dict()
        if value[1] != 200:
            return value
        input = value[0]['report_job']
        report = app.set_report(input)

    return jsonify(result='success', report=report), 200


@server.route('/sgt/job/command', methods=['GET', 'PUT'])
def setjob_command():
    commands = []
    if request.method == 'GET':
        commands = app.job_list['command']
    elif request.method == 'PUT':
        value = get_dict()
        if value[1] != 200:
            return value
        input = value[0]['command_jobs']
        commands = app.set_commands(input)

    return jsonify(result='success', commands=commands), 200


# 自身の情報を返す
@server.route('/info', methods=['GET'])
def get_info():
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
    app = Sergeant('sgt-http', 'localhost', self_port)
    app.join(su_addr, su_port)
    server.debug = True
    server.run(port=self_port)
