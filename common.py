#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from flask import jsonify, request


def get_dict():
    '''
    [Flask.routeに登録された関数内で利用]
    json形式のリクエストボディからdict形式のオブジェクトを取得する
    :return: リクエストボディ(dict)
    '''
    # request.jsonを使うとエラー処理ができない; content-typeなのかデータが悪いのかが不明

    # content-type check
    if request.headers['Content-Type'] != 'application/json':
        return jsonify(result='failed', msg='application/json required'), 406

    # json parse
    try:
        param_str = request.data.decode('utf-8')
        param_dict = json.loads(param_str)
    except json.JSONDecodeError:
        return jsonify(result='failed', msg="param couldn't decode to json"), 400

    return param_dict, 200
