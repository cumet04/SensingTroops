#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import hashlib
from functools import wraps
from collections import namedtuple
from flask import jsonify, request
from werkzeug.exceptions import BadRequest

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


def json_input(f):
    """
    PUT/POSTでjsonを受け取るAPI用のデコレータ
    Content-Typeのチェックとjsonのデコードチェックを行う
    """
    @wraps(f)
    def check_json(*args, **kwargs):
        if request.method == 'PUT' or request.method == 'POST':
            # request.json
            #   - bad content-type -> return None
            #   - can't decode -> raise BadRequest
            try:
                print(request.data.decode('utf-8'))
                if request.json is None:
                    return jsonify(result='failed', msg='application/json required'), 406
            except BadRequest as e:
                return jsonify(result='failed', msg="param couldn't decode to json"), 400
        return f(*args, **kwargs)
    return check_json

