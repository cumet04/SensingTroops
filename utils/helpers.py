import logging
from utils import logger
from functools import wraps
from flask import jsonify, request
from werkzeug.exceptions import BadRequest


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
    NotModified = {
        'success': False,  # ヘルパー周りの実装の関係上ここはFalseのが都合良い
        'msg': "resource is not modified"
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
                # logger.info(request.data.decode('utf-8'))
                if request.json is None:
                    return jsonify(result='failed',
                                   msg='application/json required'), 406
            except BadRequest:
                return jsonify(result='failed',
                               msg="param couldn't decode to json"), 400
        return f(*args, **kwargs)
    return check_json


class DelegateHandler(logging.Handler):
    def __init__(self, func):
        super(DelegateHandler, self).__init__()
        self.func = func


    def emit(self, record):
        self.func(record.message)


def get_ip():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip


def get_mac():
    import netifaces
    if_name = netifaces.interfaces()[1]  # loopbackの次のやつを取得
    return netifaces.ifaddresses(if_name).get(netifaces.AF_LINK)[0]["addr"]
