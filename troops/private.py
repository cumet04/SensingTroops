#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import threading
import requests
import random
import socket
from collections import namedtuple
from common import json_input, generate_info, PrivateInfo
from flask import Flask, jsonify, request
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


Sensor = namedtuple('Sensor', ['name', 'func', 'unit'])

# Sergeantでの利用の具合によっては、event指定せずの__init__や
# eventを排除する_asdictをクラス内に実装したほうがよいかもしれない
Order = namedtuple('Order', ['sensor', 'interval', 'event'])


class Private(object):
    def __init__(self, name, addr, port):
        self._sensors = {
            'random': Sensor(name='random', func=random.random, unit='-'),
            'zero': Sensor(name='zero', func=lambda: 0, unit='-'),
        }
        self.orders = []
        self.info = generate_info(PrivateInfo, name=name, addr=addr, port=port,
                                  sensors=list(self._sensors.keys()))
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

        path = 'http://{0}/sergeant/soldiers'.format(self._superior_ep)
        requests.post(path, json=self.info._asdict()).json()
        return True

    def set_order(self, input_orders):
        """
        この兵士に割り当てられている命令を置き換える
        :param input_orders: 新規命令のリスト
        """

        # 既存の命令を消去
        [order.event.set() for order in self.orders]
        self.orders.clear()

        # 新しい命令を受理
        for order in input_orders:
            if order.sensor not in self._sensors:
                continue

            t = threading.Thread(target=self._sensing_thread, args=(order, ))
            t.start()
            self.orders.append(order)

        logger.info('accepted new order')
        logger.debug('new order: {0}'.format(str(self.orders)))

    def _sensing_thread(self, order):
        sensor = order.sensor
        interval = order.interval
        event = order.event

        # if event is set, exit the loop
        while not event.wait(timeout=interval):
            path = 'http://{0}/sergeant/soldiers/{1}/work'.\
                    format(self._superior_ep, self.info.id)
            value = self._sensors[sensor].func()
            requests.post(path, json={'sensor': sensor, 'value': value})


# REST interface ---------------------------------------------------------------

server = Flask(__name__)
url_prefix = '/private'


# 自身の情報を返す
@server.route(url_prefix, methods=['GET'])
def get_info():
    return jsonify(result='success', info=app.info._asdict()), 200


# 新しい命令を受理する
@server.route(url_prefix + '/order', methods=['GET', 'PUT'])
@json_input
def get_order():
    if request.method == 'PUT':
        orders = request.json['orders']
        if not isinstance(orders, list):
            orders = [orders]
        app.set_order([Order(**o, event=threading.Event()) for o in orders])

    elif request.method == 'GET':
        pass

    # Orderオブジェクトをdictに変換
    orders = [order._asdict() for order in app.orders]
    [order.pop('event') for order in orders]
    return jsonify(result='success', orders=orders), 200




# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 4:
        self_port = int(sys.argv[1])
        su_addr = sys.argv[2]
        su_port = sys.argv[3]
    else:
        logger.error('superior addr/port required')
        sys.exit()

    # FIXME: この方法だと環境によっては'127.0.0.1'が取得されるらしい
    addr = socket.gethostbyname(socket.gethostname())

    app = Private('pvt-http', addr, self_port)
    app.join(su_addr, su_port)
    server.debug = True
    server.run(host='0.0.0.0', port=self_port, 
                use_debugger=True, use_reloader=False)
