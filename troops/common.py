#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import hashlib
from functools import wraps
from collections import namedtuple
from flask import jsonify, request
from werkzeug.exceptions import BadRequest

SoldierInfo = namedtuple('SoldierInfo', [
        'id',
        'name',
        'endpoint',
        'weapons',
        'orders'
    ])
LeaderInfo = namedtuple('LeaderInfo', [
        'id',
        'name',
        'endpoint',
        'subordinates',
        'missions'
    ])
CommanderInfo = namedtuple('CommanderInfo', [
        'id',
        'name',
        'endpoint',
        'subordinates',
        'campaigns'
    ])

Campaign = namedtuple('Campaign', [
        'author',
        'requirements',
        'trigger',
        'place',
        'purpose',
        'destination'
    ])

Mission = namedtuple('Mission', [
        'author',
        'requirements',
        'trigger',
        'place',
        'purpose',
        'destination'
    ])

Order = namedtuple('Order', [
        'author',
        'requirements',
        'trigger',
        'place',
        'purpose',
        'destination'
    ])

Report = namedtuple('Report', [
        'time',
        'purpose',
        'values'
    ])

Work = namedtuple('Work', [
    'time',
    'purpose',
    'value'
])


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
            except BadRequest as e:
                return jsonify(result='failed',
                               msg="param couldn't decode to json"), 400
        return f(*args, **kwargs)
    return check_json

