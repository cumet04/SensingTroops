#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from functools import wraps
from flask import jsonify, request
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
                    return jsonify(result='failed', msg='application/json required'), 406
            except BadRequest as e:
                return jsonify(result='failed', msg="param couldn't decode to json"), 400
        return f(*args, **kwargs)
    return check_json

