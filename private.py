#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import threading
import time
import requests
import random
from common import get_dict
from flask import Flask, jsonify, request, url_for, abort, Response


class Private(object):
    def __init__(self):
        # self.config = None
        self.__weapons = {}
        self.__weapons['random'] = Sensor(random.random, 0)
        self.__weapons['zero'] = Sensor(lambda :0, 0)

    def join(self, addr, port):
        self.superior_ep = addr + ':' + port

        path = 'http://{0}/pvt/join'.format(self.superior_ep)
        res = requests.post(path, json={'sensor': "pvt-skel"}).json()

        self.id = res['id']
        # TODO: logging
        print(self.id)

    def set_order(self, order):
        '''
        この兵士に割り当てられている命令を置き換える
        :param order: 新規命令のリスト
        :return: 受理した命令
        '''
        submitted = []
        for item in order:
            sensor = item['sensor']
            interval = item['interval']
            if sensor not in self.__weapons: continue

            self.__weapons[sensor].interval = interval
            self.__working(sensor)
            submitted.append({'sensor': sensor, 'interval': interval})

        print('get order' + str(submitted))
        return submitted

    def __working(self, sensor):
        '''
        指定されたセンサー種別のセンサ値を送信するスレッド
        :param sensor: センサー種別
        '''
        value = self.__weapons[sensor].func()
        interval = self.__weapons[sensor].interval
        timer = self.__weapons[sensor].timer

        if timer is not None: timer.cancel()
        t = threading.Timer(interval, self.__working, args=(sensor, ))
        t.start()
        self.__weapons[sensor].timer = t

        path = 'http://{0}/pvt/{1}/work'.format(self.superior_ep, self.id)
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
    result = get_dict()
    if result[1] != 200: return result

    accepted = app.set_order(result[0])
    return jsonify(result='success', accepted=accepted), 200


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 4:
        self_port = sys.argv[1]
        su_addr = sys.argv[2]
        su_port = sys.argv[3]
    else:
        print('superior addr/port required')
        sys.exit()
    app = Private()
    app.join(su_addr, su_port)

    server.debug = True
    server.run(port=int(self_port))
