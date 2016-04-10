#!/usr/bin/python3
# -*- coding: utf-8 -*-

from objects import definitions
from functools import wraps
from flask import jsonify, request
from flask_swagger import swagger
from werkzeug.exceptions import BadRequest


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
                    return jsonify(result='failed',
                                   msg='application/json required'), 406
            except BadRequest:
                return jsonify(result='failed',
                               msg="param couldn't decode to json"), 400
        return f(*args, **kwargs)
    return check_json


def gen_spec(app_name, server):
    """
    swagger-specのdictを生成する
    :param str app_name: specのtitleに設定されるアプリケーション名
    :param server: flaskオブジェクト
    :return dict: swagger-specのjsonになるdict
    """
    spec_dict = swagger(server, template={'definitions': definitions})
    spec_dict['info']['title'] = 'SensingTroops - ' + app_name
    return spec_dict
