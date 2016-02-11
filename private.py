#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import threading
import requests
import random
from common import get_dict, SergeantInfo, PrivateInfo
from flask import Flask, jsonify, request
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Private(object):
    def __init__(self, name, addr, port):
        self._sensors = {
            'random': Sensor(random.random, 0),
            'zero': Sensor(lambda: 0, 0)
        }
        self.info = PrivateInfo.generate(name, addr, port, list(self._sensors.keys()))
        self._superior_ep = ''

    def join(self, addr, port):
        """
        指定された上官に入隊申請を行う
        :param str addr: 上官のIPアドレス
        :param str port: 上官のポート番号
        :rtype: str
        :return: id
        """
        self._superior_ep = addr + ':' + port
        logger.info('join into the sergeant: {0}'.format(self._superior_ep))

        path = 'http://{0}/pvt/join'.format(self._superior_ep)
        requests.post(path, json=self.info._asdict()).json()
        return True

    def set_order(self, order):
        """
        この兵士に割り当てられている命令を置き換える
        :param order: 新規命令のリスト
        :return: 受理した命令
        """
        # 既存の命令をリセットして上書きする仕様にすべきか
        # 更に不正な情報が含まれていた場合や命令の差出人がおかしい場合にハネる必要がありそう
        accepted = []
        for item in order:
            sensor = item['sensor']
            interval = item['interval']
            if sensor not in self._sensors:
                continue

            self._sensors[sensor].interval = interval
            self.__working(sensor)
            accepted.append({'sensor': sensor, 'interval': interval})

        logger.info('accepted new order')
        logger.debug('new order: {0}'.format(str(accepted)))
        return accepted

    def __working(self, sensor):
        """
        指定されたセンサー種別のセンサ値を送信するスレッド
        :param sensor: センサー種別
        """
        value = self._sensors[sensor].func()
        interval = self._sensors[sensor].interval
        timer = self._sensors[sensor].timer

        if timer is not None:
            timer.cancel()
        t = threading.Timer(interval, self.__working, args=(sensor,))
        t.start()
        self._sensors[sensor].timer = t

        path = 'http://{0}/pvt/{1}/work'.format(self._superior_ep, self.info.id)
        return requests.post(path, json={'sensor': sensor, 'value': value})


class Sensor(object):
    __slots__ = ['func', 'timer', 'interval']

    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.timer = None


# REST interface ---------------------------------------------------------------

server = Flask(__name__)


# 新しい命令を受理する
@server.route('/order', methods=['GET', 'PUT'])
def get_order():
    orders = []
    if request.method == 'PUT':
        value = get_dict()
        if value[1] != 200:
            return value

        orders = value[0]['orders']
        if not isinstance(orders, list):
            orders = [orders]
        orders = app.set_order(orders)
    elif request.method == 'GET':
        # TODO: impl
        orders = []
    return jsonify(result='success', orders=orders), 200


# 自身の情報を返す
@server.route('/info', methods=['GET'])
def get_info():
    info = app.info
    return jsonify(result='success', info=info), 200


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 4:
        self_port = int(sys.argv[1])
        su_addr = sys.argv[2]
        su_port = sys.argv[3]
    else:
        logger.error('superior addr/port required')
        sys.exit()

    app = Private('pvt-http', 'localhost', self_port)
    app.join(su_addr, su_port)
    server.debug = True
    server.run(port=self_port, use_debugger=True, use_reloader=False)
