from urllib.request import urlopen
from wsgiref.simple_server import make_server
import urllib.error
import json
import signal
import threading
import re

import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
logger = Logger(__name__, DEBUG)


class Request(object):
    def __init__(self, host, port_num, url_prefix):
        self.url_base = "http://{0}:{1}/{2}/".format(host, port_num, url_prefix)

    def executeGet(self, api):
        request_url = self.url_base + api
        logger.debug('executeGet url=%s', request_url)
        try:
            res_raw = urlopen(request_url)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error('executeGet failed : ' + str(e.reason))
            return None
        return json.loads(res_str)

    def executePost(self, api, data):
        request_url = self.url_base + api
        logger.debug('executePost url=%s', request_url)
        try:
            res_raw = urlopen(request_url, data)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error('executePost failed : ' + str(e.reason))
            return None
        return json.loads(res_str)


class WebApiServer(object):
    def __init__(self, function_list, port_num, url_prefix):
        function_list[r"|/|/help"] = self.showHelp
        self.function_list = function_list
        self.port_num = port_num
        self.url_prefix = url_prefix

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']
        headers = [('Content-type', 'application/json; charset=utf-8')]

        # shift_path_info ?
        method = None
        # eliminate path prefix from PATH_INFO.
        if path.startswith('/' + self.url_prefix):
            method = path.partition(self.url_prefix)[2]

        for pattern in self.function_list:
            r = re.compile(pattern)
            m = r.fullmatch(method)
            if m is not None:
                start_response('200 OK', headers)
                result = self.function_list[pattern](query, environ, m.groups())
                return [json.dumps(result).encode('utf-8')]

        start_response('404 Not found', headers)
        return ['404 Not found'.encode("utf-8")]

    def showHelp(self, query_param, environ, m):
        """
        show this help message.
        """
        logger.info('WebApiServer.showHelp')
        result = io.StringIO()
        for api in self.path_functions:
            print('- ' + api, file=result, end="")
            print(textwrap.dedent(self.function_list[api].__doc__), file=result)
        return result

    def startServer(self):
        logger.debug('start server: port=' + str(self.port_num))

        server = make_server('', self.port_num, self)
        server.serve_forever()
