from wsgiref.simple_server import make_server
import datetime
import json
import sys
import os
import signal
import threading
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


class Captain(object):
    
    def __init__(self):
        self.path_functions = {'/sgt/join':  self.joinMember,
                               '/sgt/job':   self.giveJob,
                               '/sgt/report':self.receiveReport}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']
        headers = [('Content-type', 'application/json; charset=utf-8')]

        if path in self.path_functions:
            start_response('200 OK', headers)
            result = self.path_functions[path](query, environ)
            return [result.encode('utf-8')]
        else:
            start_response('404 Not found', headers)
            return ['404 Not found'.encode("utf-8")]

    def receiveReport(self, query_string, environ):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wsgi_input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        print(wsgi_input.read(content_length).decode('utf-8'))

        item = (timestamp, query_string)
        print(item)
# push item to DB
#
        result = {"receive": item}
        return json.dumps(result)

    def joinMember(self, query_string, environ):
        result = {"id" : 1}
        return json.dumps(result)

    def giveJob(self, query_string, environ):
        result = {"job" : "setinterval", "value" : 10}
        sys.stdout.flush()
        return json.dumps(result)


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
    if conf.loadfile(conf_name) == False: quit(1)
    if hasattr(conf, 'cptport'):pass
    else:
        print("error: load config file failed; lack of parameter.")
        quit(1)

    application = Captain()
    logger.debug('start server: port=' + str(conf.cptport))
    server = make_server('', conf.cptport, application)
    signal.signal(signal.SIGINT, lambda n,f : server.shutdown())
    t = threading.Thread(target=server.serve_forever)
    t.start()
