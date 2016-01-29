from wsgiref.simple_server import make_server
import datetime
import json
import signal
import sys
import os
import pymongo

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import WebApiServer


class Captain(WebApiServer):
    
    def __init__(self):
        WebApiServer.__init__(self)
        self.func_list[r'/sgt/join']        = self.joinMember
        self.func_list[r'/sgt/(\d)/job']    = self.giveJob
        self.func_list[r'/sgt/(\d)/report'] = self.receiveReport
        self.sgt_num = 0

        # client = pymongo.MongoClient(host='192.168.0.21', port=27017)
        # self.coll = client.test.tmp

    def receiveReport(self, query_string, environ, m):
        """
        receiveReport
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wsgi_input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        content_json = wsgi_input.read(content_length).decode('utf-8')
        content_dict = json.loads(content_json)

        self.pushData(content_dict)
        result = {"receive": content_json}
        return result

    def joinMember(self, query_string, environ, m):
        """
        joinMember
        """
        result = {"id" : self.sgt_num, "interval": 10, "heartbeat" : 3}
        self.sgt_num += 1
        return result

    def giveJob(self, query_string, environ, m):
        """
        giveJob
        """
        result = {"interval": 10, "heartbeat" : 3}
        sys.stdout.flush()
        return result

    def pushData(self, data):
        """
        push data to DB
        """
        print(data)
        # self.coll.insert_many(data)



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
        conf_name = script_path + '/conf/captain.conf'

    # load and check config
    config_params = ('cptport', 'url_prefix')
    if conf.loadfile(conf_name, config_params) == False: quit(1)

    # start server
    app = Captain()
    # app.pushData({"testname": "aaa"})

    try:
        app.startServer(conf.cptport, conf.url_prefix)
    except KeyboardInterrupt:
        pass
