from wsgiref.simple_server import make_server
from urllib.request import urlopen
import urllib.error
import datetime
import json
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import WebApiServer
from webapi import Request


class Sergeant(object):
    
    def __init__(self):
        self.value_cache = []
        self.function_list = {'/pvt/join': self.joinMember,
                              '/pvt/put':  self.putValue,
                              '/pvt/order':self.askOrder,
                              '/pvt/cache':self.outputCache}

        self.job_functions = {'setinterval': self.setInterval}
        self.beat_interval = 2
        self.submit_interval = 1
        self.request = Request(conf.cptaddr, conf.cptport)

        # join
        response = self.request.executeGet('sgt/join')
        if response == None: return
        self.soldier_id = response['id']
        # job
        self.askJob()
        # submit
        self.submitReport()

    def askJob(self):
        response = self.request.executeGet('sgt/job')
        if response == None: return
        job = response['job']
        if job in self.job_functions:
            result = self.job_functions[job](response)

        t = threading.Timer(self.beat_interval, self.askJob)
        t.start()

    def submitReport(self):
        value = json.dumps(self.value_cache)
        response = self.request.executePost('sgt/report', value.encode('utf-8'))
        if response == None: return
        self.value_cache.clear()

        t = threading.Timer(self.submit_interval, self.submitReport)
        t.start()

    def setInterval(self, values):
        self.submit_interval = values['value']

    # WebAPI functions
    def putValue(self, query_string, environ):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = (timestamp, query_string)
        self.value_cache.append(item)
        result = {"put": item}
        return result

    def joinMember(self, query_string, environ):
        result = {"id" : 1}
        return result

    def askOrder(self, query_string, environ):
        result = {"order" : "setinterval", "value" : 3}
        return result

    def outputCache(self, query_string, environ):
        return self.value_cache


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
    config_params = ('cptaddr', 'cptport', 'sgtport', 'url_prefix')
    if conf.loadfile(conf_name, config_params) == False: quit(1)

    # start server
    app = Sergeant()
    server = WebApiServer(app.function_list, conf.sgtport, conf.url_prefix)
    server.startServer()
