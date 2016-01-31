#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import threading
import time
import requests
import random
from flask import Flask, jsonify, request, url_for, abort, Response


class Private(object):
    def __init__(self):
        self.config = None
        self.__weapons = {}
        self.__weapons['random'] = Sensor(random.random, 0)
        self.__weapons['zero'] = Sensor(lambda :0, 0)

    def start_work(self):
        work_thread = threading.Thread(target=self.__working, daemon=True)
        work_thread.start()


    def join(self, addr, port):
        self.superior_ep = addr + ':' + port

        value = {"name": "pvt"}
        res_dict = post_data(self.superior_ep, '/pvt/join', value).json()

        self.id = res_dict['id']
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

        post_data(self.superior_ep, '/pvt/' + self.id + '/work', value)




class Sensor(object):
    __slots__ = ['func', 'timer', 'interval']

    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.timer = None


def post_data(addr, path, value):
    '''
    指定endpointにdict形式のデータをpostする
    :param addr: 送信先アドレス
    :param path: 送信先URIのパス
    :param value: 送信するデータ(dict)
    :return: Response object
    '''
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(value)
    path = 'http://{0}{1}'.format(addr, path)
    return requests.post(path, data=data, headers=headers)

# REST interface ---------------------------------------------------------------

app = Private()
server = Flask(__name__)


# json形式のリクエストボディからdict形式のオブジェクトを取得する
def get_dict():
    # content-type check
    if request.headers['Content-Type'] != 'application/json':
        return jsonify(res='application/json required'), 406

    # json parse
    try:
        param_str = request.data.decode('utf-8')
        param_dict = json.loads(param_str)
    except json.JSONDecodeError:
        return jsonify(error="param couldn't decode to json"), 400

    return param_dict, 200


# 新しい命令を受理する
@server.route('/order', methods=['POST'])
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
