from urllib.request import urlopen
import json
import threading
import signal
import os
import configfile


class Private(object):

    def __init__(self):
        self.order_functions = {'setinterval': self.setInterval}
        self.beat_interval = 2
        self.put_interval = 1

        # join
        response = self.getJson(conf.sgtaddr, conf.stgport, 'pvt/join')
        self.soldier_id = response['id']
        # order
        self.askOrder()
        # put
        self.putValue()

    def askOrder(self):
        response = self.getJson(conf.sgtaddr, conf.stgport, 'pvt/order')
        order = response['order']
        if order in self.order_functions:
            result = self.order_functions[order](response)

        t = threading.Timer(self.beat_interval, self.askOrder)
        t.start()

    def putValue(self):
        value = "test_value"
        self.getJson(conf.sgtaddr, conf.sgtport, 'pvt/put?' + value)

        t = threading.Timer(self.put_interval, self.putValue)
        t.start()

    # order functions ----------------------------------------------------------
    def setInterval(self, values):
        self.put_interval = values['value']


    def getJson(self, host, port, api):
        res_raw = urlopen("http://${0}:${1}/${2}".format(host, port, api))
        res_str = res_raw.read().decode('utf-8')
        return json.loads(res_str)

# if __name__ == '__main__':
conf = configfile.Config()

if __name__ == '__main__':
    # set config-file name
    conf_name = ''
    if len(sys.argv) == 2:
        conf_name = sys.argv[1]
    else:
        script_path = os.path.abspath(os.path.dirname(__file__))
        conf_name = script_path + '/conf/private.conf'

    # load and check config
    conf.loadfile(conf_name)
    if conf.loadconfig(conf_name) == False: quit(1)
    if hasattr(conf, 'sgtaddr') and \
       hasattr(conf, 'sgtport'): pass
    else:
        print("error: load config file failed; lack of parameter.")
        quit(1)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    pvt = Private()
