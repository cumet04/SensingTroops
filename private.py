from urllib.request import urlopen
import urllib.error
import json
import threading
import signal
import os
import sys
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


class Private(object):

    def __init__(self):
        self.order_functions = {'setinterval': self.setInterval}
        self.beat_interval = 2
        self.put_interval = 1

        # join
        response = self.requestAPI_get(conf.sgtaddr, conf.sgtport, 'pvt/join')
        if response == None: return
        self.soldier_id = response['id']
        # order
        self.askOrder()
        # put
        self.putValue()

    def askOrder(self):
        response = self.requestAPI_get(conf.sgtaddr, conf.sgtport, 'pvt/order')
        if response == None: return
        order = response['order']
        if order in self.order_functions:
            result = self.order_functions[order](response)

        t = threading.Timer(self.beat_interval, self.askOrder)
        t.start()

    def putValue(self):
        value = "test_value"
        response = self.requestAPI_get(conf.sgtaddr, conf.sgtport, 'pvt/put?' + value)
        if response == None: return

        t = threading.Timer(self.put_interval, self.putValue)
        t.start()

    # order functions ----------------------------------------------------------
    def setInterval(self, values):
        self.put_interval = values['value']

    def requestAPI_get(self, host, port, api):
        request_url = "http://{0}:{1}/{2}".format(host, port, api)
        logger.debug('requestAPI_get url=%s', request_url)
        try:
            res_raw = urlopen(request_url)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error("requestAPI_post failed : " + str(e.reason))
            return None
        return json.loads(res_str)

    def requestAPI_post(self, host, port, api, data):
        request_url = "http://{0}:{1}/{2}".format(host, port, api)
        logger.debug('requestAPI_get url=%s', request_url)
        try:
            res_raw = urlopen(request_url, data)
            res_str = res_raw.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error("requestAPI_post failed : " + str(e.reason))
            return None
        return json.loads(res_str)


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
        conf_name = script_path + '/conf/private.conf'

    # load and check config
    if conf.loadfile(conf_name) == False: quit(1)
    if hasattr(conf, 'sgtaddr') and \
       hasattr(conf, 'sgtport'): pass
    else:
        print("error: load config file failed; lack of parameter.")
        quit(1)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    pvt = Private()
