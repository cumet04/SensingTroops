from urllib.request import urlopen
from wsgiref.simple_server import make_server
import urllib.error
import json
import signal
import threading

import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
logger = Logger(__name__, DEBUG)


class Request(object):
    def __init__(self, host, port_num):
        self.host = host
        self.port_num = port_num

    def executeGet(self, api):
        request_url = "http://{0}:{1}/{2}".format(self.host, self.port_num, api)
        logger.debug('executeGet url=%s', request_url)
        try:
            res_raw = urlopen(request_url)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error('executeGet failed : ' + str(e.reason))
            return None
        return json.loads(res_str)

    def executePost(self, api, data):
        request_url = "http://{0}:{1}/{2}".format(self.host, self.port_num, api)
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

        if path in ('', '/', '/help'):
            return [self.showHelp().getValue().encode('utf-8')]
        elif path in self.function_list:
            start_response('200 OK', headers)
            result = self.function_list[path](query, environ)
            return [json.dumps(result).encode('utf-8')]
        else:
            start_response('404 Not found', headers)
            return ['404 Not found'.encode("utf-8")]

    def showHelp(self, query_param):
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
        signal.signal(signal.SIGINT, lambda n,f : server.shutdown())
        self.t = threading.Thread(target=server.serve_forever)
        self.t.start()
