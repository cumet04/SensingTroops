import requests
import traceback
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger("utils")
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def get(url, params=None, etag=None, **kwargs):
    if etag is not None:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['If-None-Match'] = etag
    try:
        res = requests.get(url, params=params, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(traceback.format_exc())
        return None, e
    return _rest_check_response(res)


def post(url, data=None, json=None, etag=None, **kwargs):
    if etag is not None:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['If-None-Match'] = etag
    try:
        res = requests.post(url, data=data, json=json, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(traceback.format_exc())
        return None, e
    return _rest_check_response(res)


def put(url, data=None, json=None, etag=None, **kwargs):
    from json import dumps
    if etag is not None:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['If-None-Match'] = etag
    try:
        # requestsのputにはjsonオプションが無いので手動で設定する
        if json is not None:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Content-Type'] = 'application/json'
            res = requests.put(url, dumps(json), **kwargs)
        else:
            res = requests.put(url, data=data, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(traceback.format_exc())
        return None, e
    return _rest_check_response(res)


def _rest_check_response(res: requests.Response):
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
        logger.error(traceback.format_exc())
        return res, e

    # check whether request is success
    if not res_dict['_status']['success']:
        msg = res_dict['_status']['msg']
        logger.error(errmsg + msg)
        return res, msg

    return res, None
