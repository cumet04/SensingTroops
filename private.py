#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import threading
import requests
import random
from common import get_dict
from flask import Flask, jsonify
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Private(object):
    def __init__(self):
        self.info = {
            'id': '',
            'name': 'pvt-http',
            'port': 0
        }
        self.superior_ep = ''
        self.__sensors = {
            'random': Sensor(random.random, 0),
            'zero': Sensor(lambda: 0, 0)
        }

    def join(self, addr, port):
        self.superior_ep = addr + ':' + port
        logger.info('join into the sergeant: {0}'.format(self.superior_ep))

        info = self.info
        info['sensors'] = list(self.__sensors.keys())
        path = 'http://{0}/pvt/join'.format(self.superior_ep)
        res = requests.post(path, json=info).json()

        self.info['id'] = res['id']
        logger.info('get my pvt-id: {0}'.format(self.info['id']))

    def get_info(self):
        logger.info('get self info')
        return self.info

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
            if sensor not in self.__sensors:
                continue

            self.__sensors[sensor].interval = interval
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
        value = self.__sensors[sensor].func()
        interval = self.__sensors[sensor].interval
        timer = self.__sensors[sensor].timer

        if timer is not None:
            timer.cancel()
        t = threading.Timer(interval, self.__working, args=(sensor, ))
        t.start()
        self.__sensors[sensor].timer = t

        path = 'http://{0}/pvt/{1}/work'.format(self.superior_ep, self.info['id'])
        return requests.post(path, json={'sensor': sensor, 'value': value})


class Sensor(object):
    __slots__ = ['func', 'timer', 'interval']

    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.timer = None


# REST interface ---------------------------------------------------------------

app = Private()
server = Flask(__name__)


# 新しい命令を受理する
@server.route('/order', methods=['PUT'])
def get_order():
    value = get_dict()
    if value[1] != 200:
        return value

    accepted = app.set_order(value[0])
    return jsonify(result='success', accepted=accepted), 200


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
    if len(sys.argv) == 4:
        self_port = sys.argv[1]
        su_addr = sys.argv[2]
        su_port = sys.argv[3]
    else:
        logger.error('superior addr/port required')
        sys.exit()
    app.info['port'] = self_port
    app.join(su_addr, su_port)

    # server.debug = True
    server.run(port=int(self_port))
