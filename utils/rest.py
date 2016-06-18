import requests
import flask
from json import dumps
from functools import wraps
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger("utils")
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def _set_etag(f):
    @wraps(f)
    def set_etag(*args, **kwargs):
        kwargs['headers'] = kwargs.get('headers', {})
        if "etag" in kwargs:
            kwargs['headers']['If-None-Match'] = kwargs["etag"]
        return f(*args, **kwargs)
    return set_etag


@_set_etag
def get(url, params=None, etag=None, **kwargs):
    try:
        res = requests.get(url, params=params, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(">> [GET] {0} failed with exception: {1}".format(url, e))
        return None, e
    return _rest_check_response(res)


@_set_etag
def post(url, data=None, json=None, etag=None, **kwargs):
    try:
        res = requests.post(url, data=data, json=json, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(">> [POST] {0} failed with exception: {1}".format(url, e))
        return None, e
    return _rest_check_response(res)


@_set_etag
def put(url, data=None, json=None, etag=None, **kwargs):
    try:
        # requestsのputにはjsonオプションが無いので手動で設定する
        if json is not None:
            kwargs['headers']['Content-Type'] = 'application/json'
            res = requests.put(url, dumps(json), **kwargs)
        else:
            res = requests.put(url, data=data, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(">> [PUT] {0} failed with exception: {1}".format(url, e))
        return None, e
    return _rest_check_response(res)


def _rest_check_response(res):
    import json
    # check whether resource is not modified
    if res.status_code == 304:
        return res, None

    errmsg = ">> [{0}] {1} failed with code {2}: ". \
        format(res.request.method, res.url, res.status_code)

    # check whether response is json
    try:
        res_dict = res.json()
        if res_dict is None:
            logger.error(errmsg + "response.json() returns None")
            return res, "response.json() returns None"
            # requestsのjsonがNoneになる状況は不明．ドキュメントには失敗したらNone
            # とあるが，テストしたらHTMLレスポンスにJSONDecodeErrorを返した．
    except json.JSONDecodeError as e:
        logger.error(errmsg + "got no-json response with code {0}".
                     format(res.status_code))
        return res, e

    # check whether request is success
    if not res_dict['_status']['success']:
        msg = res_dict['_status']['msg']
        logger.error(errmsg + msg)
        return res, msg

    return res, None


class ResponseEx(flask.Response):
    """
    FlaskClientの返すflask.Responseをrequests.Responseの
    代わりに使うためのラッパークラス
    """
    def __init__(self, base, method, url):
        from unittest.mock import MagicMock
        super().__init__()
        for attr_name in base.__dict__:
            setattr(self, attr_name, getattr(base, attr_name))
        self.request = MagicMock(method=method)
        self.url = url

    def json(self):
        import json
        return json.loads(self.data.decode("utf-8"))


def test_client(clients):
    """
    restラッパーをflask.test_client利用のものに差し替える
    """
    from unittest import mock
    from json import dumps
    from functools import wraps

    def select_client(url):
        import re
        m = re.match(r"test://(.*?)/(.*)", url)
        if m is None:
            logger.error("rest_wrapper is called without test protocol")
            return None, None
        key = m.group(1)
        path = m.group(2)
        return clients[key], path

    @_set_etag
    def test_get(url, etag=None, **kwargs):
        c, path = select_client(url)
        # paramsはFlaskClientのgetには無いのでひとまず握りつぶす
        res = c.get(path, **kwargs)
        res = ResponseEx(res, "GET", url)
        return _rest_check_response(res)

    @_set_etag
    def test_post(url, data=None, json=None, etag=None, **kwargs):
        c, path = select_client(url)
        if json is not None:
            res = c.post(path, data=dumps(json),
                         content_type='application/json', **kwargs)
        else:
            res = c.post(path, data=data, **kwargs)
        res = ResponseEx(res, "GET", url)
        return _rest_check_response(res)

    @_set_etag
    def test_put(url, data=None, json=None, etag=None, **kwargs):
        c, path = select_client(url)
        if json is not None:
            res = c.put(path, data=dumps(json),
                        content_type='application/json', **kwargs)
        else:
            res = c.put(path, data=data, **kwargs)
        res = ResponseEx(res, "GET", url)
        return _rest_check_response(res)

    def _test_client(f):
        @wraps(f)
        def patch_rest(*args, **kwargs):
            with mock.patch("utils.rest.get", side_effect=test_get), \
                 mock.patch("utils.rest.post", side_effect=test_post), \
                 mock.patch("utils.rest.put", side_effect=test_put):
                return f(*args, **kwargs)
        return patch_rest
    return _test_client
