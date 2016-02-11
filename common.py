#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import hashlib
from flask import jsonify, request
from collections import namedtuple

PrivateInfo = namedtuple('PrivateInfo', ['id', 'name', 'addr', 'port', 'sensors'])
SergeantInfo = namedtuple('SergeantInfo', ['id', 'name', 'addr', 'port'])
CaptainInfo = namedtuple('CaptainInfo', ['id', 'name', 'addr', 'port'])


def generate_info(cls, **kwargs):
    """
    namedtupleをid以外のパラメータ指定で生成する
    :param cls: 生成するnamedtupleのクラス
    :param kwargs: 初期化パラメータ
    :return: ID付きで生成されたインスタンス
    """
    no_id = cls(id=None, **kwargs)
    m = hashlib.md5()
    m.update(str(no_id).encode())
    new_id = m.hexdigest()
    return no_id._replace(id=new_id)


def get_dict():
    '''
    [Flask.routeに登録された関数内で利用]
    json形式のリクエストボディからdict形式のオブジェクトを取得する
    :return: リクエストボディ(dict)
    '''
    # request.jsonを使うとエラー処理ができない; content-typeなのかデータが悪いのかが不明

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
