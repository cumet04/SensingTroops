from urllib.request import urlopen
import json
import threading

sergeant_address = 'http://172.17.0.89/'

class Private(object):

    def __init__(self):
        self.order_functions = {'setinterval': self.setInterval}
        self.beat_interval = 2
        self.put_interval = 1

        # join
        response = self.getJson(sergeant_address + 'pvt/join')
        self.soldier_id = response['id']
        # order
        self.askOrder()
        # put
        self.putValue()

    def askOrder(self):
        response = self.getJson(sergeant_address + 'pvt/order')
        order = response['order']
        if order in self.order_functions:
            result = self.order_functions[order](response)

        t = threading.Timer(self.beat_interval, self.askOrder)
        t.start()

    def putValue(self):
        value = "test_value"
        self.getJson(sergeant_address + 'pvt/put?' + value)

        t = threading.Timer(self.put_interval, self.putValue)
        t.start()

    # order functions ----------------------------------------------------------
    def setInterval(self, values):
        self.put_interval = values['value']


    def getJson(self, url):
        res_raw = urlopen(url)
        res_str = res_raw.read().decode('utf-8')
        return json.loads(res_str)


if __name__ == '__main__':
    pvt = Private()
