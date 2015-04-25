from wsgiref.simple_server import make_server
import datetime

class Sergeant(object):
    
    def __init__(self):
        self.interval = 3
        self.value_cache = []
        self.path_functions = {'/pvt/join': self.joinMember,
                               '/pvt/put':  self.putValue,
                               '/pvt/order':self.askOrder,
                               '/pvt/cache':self.outputCache}

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        query = environ['QUERY_STRING']
        headers = [('Content-type', 'text/plain; charset=utf-8')]

        if path in self.path_functions:
            start_response('200 OK', headers)
            result = self.path_functions[path](query)
            return [result.encode('utf-8')]
        else:
            start_response('404 Not found', headers)
            return ['404 Not found'.encode("utf-8")]

    def putValue(self, query_string):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = (timestamp, query_string)
        self.value_cache.append(item)
        return ""

    def joinMember(self, query_string):
        return "{id:1}"

    def askOrder(self, query_string):
        return "{order:setinterval, value:3}"

    def outputCache(self, query_string):
        return str(self.value_cache)

# entry point ------------------------------------------------------------------

application = Sergeant()

if __name__ == '__main__':

    server = make_server('', 80, application)
    server.serve_forever()
