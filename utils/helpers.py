import json
import requests
from functools import wraps
from flask import jsonify, request
from werkzeug.exceptions import BadRequest
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class UnexpectedServerError(Exception):
    def __init__(self, status, response):
        self.status = status
        self.response = response

    def __str__(self):
        return "status code: {0}".format(self.status)


class ResponseStatus(object):
    Success = {
        'success': True,
        'msg': "status is ok"
    }
    NotFound = {
        'success': False,
        'msg': 'resource not found'
    }
    Failed = {
        'success': False,
        'msg': 'action is failed'
    }
    NotImplemented = {
        'success': False,
        'msg': 'this function is not implemented yet'
    }

    @staticmethod
    def make_error(msg):
        return {
            'success': False,
            'msg': msg
        }


class RestClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, url):
        response = requests.get(self.base_url + url)
        if response.headers['content-type'] != 'application/json':
            raise UnexpectedServerError(response.status_code, response)
        return response.status_code, response.json()

    def post(self, url, request_obj):
        response = requests.post(self.base_url + url,
                                 json.dumps(request_obj),
                                 headers={'Content-Type': 'application/json'})
        if response.headers['content-type'] != 'application/json':
            raise UnexpectedServerError(response.status_code, response)
        return response.status_code, response.json()

    def put(self, url, request_obj):
        response = requests.put(self.base_url + url,
                                json.dumps(request_obj),
                                headers={'Content-Type': 'application/json'})
        if response.headers['content-type'] != 'application/json':
            raise UnexpectedServerError(response.status_code, response)
        return response.status_code, response.json()


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
