from wsgiref.simple_server import make_server
from urllib.request import urlopen
import urllib.error
import datetime
import json
import threading
import sys
import os
import re
import signal
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import WebApiServer
from webapi import Request


class Sergeant(WebApiServer):
    
    def __init__(self):
        self.thread_list = []
        self.value_cache = []
        WebApiServer.__init__(self)
        self.func_list[r'/pvt/join']       = self.joinMember
        self.func_list[r'/pvt/(\d)/put']   = self.putValue
        self.func_list[r'/pvt/(\d)/order'] = self.askOrder
        self.func_list[r'/dev/cache']      = self.outputCache

        self.job_functions = {'setinterval': self.setInterval}
        self.request = Request(conf.cptaddr, conf.cptport, 'SensorArmy/Captain')
        self.pvt_num = 0

        # join
        response = self.request.executeGet('sgt/join')
        if response == None: return
        self.soldier_id = response['id']
        self.submit_interval = response['interval']
        self.beat_interval = response['heartbeat']

        # start beat/submit thread
        beat_thread = threading.Thread(target=self.askJob, daemon=True)
        self.thread_list.append(beat_thread)
        beat_thread.start()

        submit_thread = threading.Thread(target=self.submitReport, daemon=True)
        self.thread_list.append(submit_thread)
        submit_thread.start()

    def askJob(self):
        while True:
            uri = 'sgt/{0}/job'.format(self.soldier_id)
            response = self.request.executeGet(uri)
            if response == None: return

            for (key, value) in response.items():
                if key == 'interval':
                    self.submit_interval = value
                elif key == 'heartbeat':
                    self.beat_interval = value

            time.sleep(self.beat_interval)

    def submitReport(self):
        while True:
            value = json.dumps(self.value_cache)
            uri = 'sgt/{0}/report'.format(self.soldier_id)
            response = self.request.executePost(uri, value.encode('utf-8'))
            if response == None: return
            self.value_cache.clear()

            time.sleep(self.submit_interval)

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
app = None

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
    try:
        app.startServer(conf.sgtport, conf.url_prefix)
    except KeyboardInterrupt:
        pass
