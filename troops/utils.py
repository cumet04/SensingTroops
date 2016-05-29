#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import json
from objects import definitions
from functools import wraps
from flask import jsonify, request
from werkzeug.exceptions import BadRequest
from logging import getLogger, StreamHandler, DEBUG, FileHandler

logger = getLogger(__name__)
handler = FileHandler('/tmp/troops/commander_test.log')
# handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class RestClient(object):
    def __init__(self):
        pass

    def get(self, url):
        pass

    def post(self, url, obj):
        pass

    def put(self, url, obj):
        pass


class RestTestClient(RestClient):
    def __init__(self, test_client):
        self.c = test_client

    def _split_response(self, response):
        if response.content_type == 'application/json':
            response_obj = json.loads(response.data.decode('utf-8'))
        else:
            response_obj = None
        return (response.status_code, response_obj)

    def get(self, url):
        response = self.c.get(url, follow_redirects=True)
        return self._split_response(response)

    def post(self, url, request_obj):
        response = self.c.post(url, data=json.dumps(request_obj),
                               content_type='application/json')
        return self._split_response(response)

    def put(self, url, request_obj):
        response = self.c.post(url, data=json.dumps(request_obj),
                               content_type='application/json')
        return self._split_response(response)


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
                logger.info(request.data.decode('utf-8'))
                if request.json is None:
                    return jsonify(result='failed',
                                   msg='application/json required'), 406
            except BadRequest:
                return jsonify(result='failed',
                               msg="param couldn't decode to json"), 400
        return f(*args, **kwargs)
    return check_json

def asdict(n_tuple):
    """
    namedtupleをdictに変換する
    :param n_tuple: namedtupleのインスタンス
    :return: dictに変換したもの
    """
    # ただの_asdictではOrderedDictになりdictにならないことと
    # アンダースコア付きの関数利用でlintに引っかかりIDEがうるさい
    return dict(n_tuple._asdict())
