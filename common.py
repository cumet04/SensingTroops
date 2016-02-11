#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import hashlib
from flask import jsonify, request
from collections import namedtuple

# TODO: Infoはまとめたほうがよさげ
# - パラメータの違いをどう吸収するか

class PrivateInfo(namedtuple('PrivateInfo', ['id', 'name', 'addr', 'port', 'sensors'])):
    @classmethod
    def generate(cls, name, addr, port, sensors):
        no_id = cls._make([None, name, addr, port, sensors])
        m = hashlib.md5()
        m.update(str(no_id).encode())
        new_id = m.hexdigest()
        return no_id._replace(id=new_id)


class SergeantInfo(namedtuple('SergeantInfo', ['id', 'name', 'addr', 'port'])):
    # infoとして受理可能なcommand / jobなどが必要かも
    @classmethod
    def generate(cls, name, addr, port):
        no_id = cls._make([None, name, addr, port])
        m = hashlib.md5()
        m.update(str(no_id).encode())
        new_id = m.hexdigest()
        return no_id._replace(id=new_id)


class CaptainInfo(namedtuple('CaptainInfo', ['id', 'name', 'addr', 'port'])):
    @classmethod
    def generate(cls, name, addr, port):
        no_id = cls._make([None, name, addr, port])
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
