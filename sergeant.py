from wsgiref.simple_server import make_server
from urllib.request import urlopen
import urllib.error
import datetime
import json
import threading
import sys
import os
import re
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import WebApiServer
from webapi import Request


class Sergeant(object):
    
    def __init__(self):
        self.value_cache = []
        self.function_list = {r'/pvt/join': self.joinMember,
                              r'/pvt/(\d)/put':  self.putValue,
                              r'/pvt/(\d)/order':self.askOrder,
                              r'/dev/cache':self.outputCache}

        self.job_functions = {'setinterval': self.setInterval}
        self.request = Request(conf.cptaddr, conf.cptport, 'SensorArmy/Captain')
        self.pvt_num = 0

        # join
        response = self.request.executeGet('sgt/join')
        if response == None: return
        self.soldier_id = response['id']
        self.submit_interval = response['interval']
        self.beat_interval = response['heartbeat']
        # job
        self.askJob()
        # submit
        self.submitReport()

    def askJob(self):
        uri = 'sgt/{0}/job'.format(self.soldier_id)
        response = self.request.executeGet(uri)
        if response == None: return

        for (key, value) in response.items():
            if key == 'interval':
                self.submit_interval = value
            elif key == 'heartbeat':
                self.beat_interval = value

        self.ask_thread = threading.Timer(self.beat_interval, self.askJob)
        self.ask_thread.start()

    def submitReport(self):
        value = json.dumps(self.value_cache)
        uri = 'sgt/{0}/report'.format(self.soldier_id)
        response = self.request.executePost(uri, value.encode('utf-8'))
        if response == None: return
        self.value_cache.clear()

        self.submit_thread = threading.Timer(self.submit_interval, self.submitReport)
        self.submit_thread.start()

    def setInterval(self, values):
        self.submit_interval = values['value']

    def stop(self):
        try:
            self.ask_thread.cancel()
            self.submit_thread.cancel()
        except:
            pass

    # WebAPI functions
    def putValue(self, query_string, environ, m):
        pvt_id = m[0]

        # generate value from input
        wsgi_input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        value_raw = wsgi_input.read(content_length).decode('utf-8')
        value_dict = json.loads(value_raw)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = (pvt_id ,timestamp, value_dict)
        self.value_cache.append(item)
        result = {"put": item}
        return result

    def joinMember(self, query_string, environ, m):
        result = {"id" : self.pvt_num, "interval": 4, "heartbeat" : 3}
        self.pvt_num += 1
        return result

    def askOrder(self, query_string, environ, m):
        result = {}
        return result

    def outputCache(self, query_string, environ, m):
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

    input('')
    app.stop()
    server.stopServer()
