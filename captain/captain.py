from wsgiref.simple_server import make_server
import datetime
import json

class Captain(object):
    
    def __init__(self):
        self.path_functions = {'/sgt/join':  self.joinMember,
                               '/sgt/report':self.receiveReport}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']
        headers = [('Content-type', 'text/plain; charset=utf-8')]
#TODO: text/plain -> json

        if path in self.path_functions:
            start_response('200 OK', headers)
            result = self.path_functions[path](query)
            return [result.encode('utf-8')]
        else:
            start_response('404 Not found', headers)
            return ['404 Not found'.encode("utf-8")]

    def receiveReport(self, query_string):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = (timestamp, query_string)
# push item to DB
#
        result = {"receive": item}
        return json.dumps(result)

    def joinMember(self, query_string):
        result = {"id" : 1}
        return json.dumps(result)

# entry point ------------------------------------------------------------------

application = Captain()

if __name__ == '__main__':

    server = make_server('', 80, application)
    server.serve_forever()
