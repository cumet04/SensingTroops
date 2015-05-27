from wsgiref.simple_server import make_server
import datetime
import json
import sys
import signal
import threading

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

application = Captain()

if __name__ == '__main__':
    server = make_server('', 80, application)
    signal.signal(signal.SIGINT, lambda n,f : server.shutdown())
    t = threading.Thread(target=server.serve_forever)
    t.start()