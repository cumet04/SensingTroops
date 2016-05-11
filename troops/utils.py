#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
