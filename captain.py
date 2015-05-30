from wsgiref.simple_server import make_server
import datetime
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import WebApiServer


class Captain(object):
    
    def __init__(self):
        self.function_list = {'/sgt/join':  self.joinMember,
                              '/sgt/job':   self.giveJob,
                              '/sgt/report':self.receiveReport}

    def receiveReport(self, query_string, environ, m):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wsgi_input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        print(wsgi_input.read(content_length).decode('utf-8'))

        item = (timestamp, query_string)
        print(item)
# push item to DB
#
        result = {"receive": item}
        return result

    def joinMember(self, query_string, environ, m):
        result = {"id" : 1}
        return result

    def giveJob(self, query_string, environ, m):
        result = {"job" : "setinterval", "value" : 10}
        sys.stdout.flush()
        return result


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
    server = WebApiServer(app.function_list, conf.cptport, conf.url_prefix)
    server.startServer()
