from wsgiref.simple_server import make_server
from urllib.request import urlopen
import datetime
import json
import threading
import sys
import signal
import os
import configfile

from logging import getLogger,StreamHandler,DEBUG,NOTSET
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

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

        # # join
        # response = self.getJson(conf.cptaddr, conf.cptport, 'sgt/join')
        # self.soldier_id = response['id']
        # # job
        # self.askJob()
        # # submit
        # self.submitReport()

    def askJob(self):
        response = self.getJson(conf.cptaddr, conf.cptport, 'sgt/job')
        job = response['job']
        if job in self.job_functions:
            result = self.job_functions[job](response)

        t = threading.Timer(self.beat_interval, self.askJob)
        t.start()

    def submitReport(self):
        value = json.dumps(self.value_cache)
        res_raw = urlopen(superior_address + 'sgt/report', value.encode('utf-8'))
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
    def getJson(self, host, port, api):
        res_raw = urlopen("http://{0}:{1}/{2}".format(host, port, api))
        res_str = res_raw.read().decode('utf-8')
        return json.loads(res_str)


# entry point ------------------------------------------------------------------

conf = configfile.Config()

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
    logger.debug('a')
    server = make_server('', conf.sgtport, application)
    logger.debug('b')
    signal.signal(signal.SIGINT, lambda n,f : server.shutdown())
    t = threading.Thread(target=server.serve_forever)
    t.start()
