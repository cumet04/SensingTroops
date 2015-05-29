from wsgiref.simple_server import make_server
from urllib.request import urlopen
import urllib.error
import datetime
import json
import threading
import sys
import signal
import os
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


class Sergeant(object):
    
    def __init__(self):
        self.value_cache = []
        self.path_functions = {'/pvt/join': self.joinMember,
                               '/pvt/put':  self.putValue,
                               '/pvt/order':self.askOrder,
                               '/pvt/cache':self.outputCache}

        self.job_functions = {'setinterval': self.setInterval}
        self.beat_interval = 2
        self.submit_interval = 1

        # join
        response = self.requestAPI_get(conf.cptaddr, conf.cptport, 'sgt/join')
        if response == None: return
        self.soldier_id = response['id']
        # job
        self.askJob()
        # submit
        self.submitReport()

    def askJob(self):
        response = self.requestAPI_get(conf.cptaddr, conf.cptport, 'sgt/job')
        if response == None: return
        job = response['job']
        if job in self.job_functions:
            result = self.job_functions[job](response)

        t = threading.Timer(self.beat_interval, self.askJob)
        t.start()

    def submitReport(self):
        value = json.dumps(self.value_cache)
        response = self.requestAPI_post(
            conf.cptaddr, conf.cptport, 'sgt/job', value.encode('utf-8'))
        if response == None: return
        self.value_cache.clear()

        t = threading.Timer(self.submit_interval, self.submitReport)
        t.start()

    def setInterval(self, values):
        self.submit_interval = values['value']

    # HTTP server entry point
    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']
        headers = [('Content-type', 'application/json; charset=utf-8')]

        if path in self.path_functions:
            start_response('200 OK', headers)
            result = self.path_functions[path](query)
            return [result.encode('utf-8')]
        else:
            start_response('404 Not found', headers)
            return ['404 Not found'.encode("utf-8")]

    # WebAPI functions
    def putValue(self, query_string):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = (timestamp, query_string)
        self.value_cache.append(item)
        result = {"put": item}
        return json.dumps(result)

    def joinMember(self, query_string):
        result = {"id" : 1}
        return json.dumps(result)

    def askOrder(self, query_string):
        result = {"order" : "setinterval", "value" : 3}
        return json.dumps(result)

    def outputCache(self, query_string):
        return json.dumps(self.value_cache)

    # other functions
    def requestAPI_get(self, host, port, api):
        request_url = "http://{0}:{1}/{2}".format(host, port, api)
        logger.debug('requestAPI_get url=%s', request_url)
        try:
            res_raw = urlopen(request_url)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error("requestAPI_post failed : " + str(e.reason))
            return None
        return json.loads(res_str)

    def requestAPI_post(self, host, port, api, data):
        request_url = "http://{0}:{1}/{2}".format(host, port, api)
        logger.debug('requestAPI_get url=%s', request_url)
        try:
            res_raw = urlopen(request_url, data)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error("requestAPI_post failed : " + str(e.reason))
            return None
        return json.loads(res_str)


# entry point ------------------------------------------------------------------

conf = configfile.Config()
logger = Logger(__name__, DEBUG)

if __name__ == '__main__':
    # set config-file name
    conf_name = ''
    if len(sys.argv) == 2:
        conf_name = sys.argv[1]
    else:
        script_path = os.path.abspath(os.path.dirname(__file__))
        conf_name = script_path + '/conf/sergeant.conf'

    # load and check config
    if conf.loadfile(conf_name) == False: quit(1)
    if hasattr(conf, 'cptaddr') and \
       hasattr(conf, 'cptport') and \
       hasattr(conf, 'sgtport'): pass
    else:
        print("error: load config file failed; lack of parameter.")
        quit(1)

    # start server
    application = Sergeant()
    logger.debug('start server: port=' + str(conf.sgtport))
    server = make_server('', conf.sgtport, application)
    signal.signal(signal.SIGINT, lambda n,f : server.shutdown())
    t = threading.Thread(target=server.serve_forever)
    t.start()
