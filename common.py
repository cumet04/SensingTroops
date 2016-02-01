#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
from flask import jsonify, request

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
