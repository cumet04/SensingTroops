from urllib.request import urlopen
import urllib.error
import json
import threading
import signal
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import Request


class Private(object):

    def __init__(self):
        self.order_functions = {'setinterval': self.setInterval}
        self.beat_interval = 2
        self.put_interval = 1

        self.request = Request(conf.sgtaddr, conf.sgtport)

        # join
        response = self.request.executeGet('SensorArmy/Sergeant/' + 'pvt/join')
        if response == None: return
        self.soldier_id = response['id']
        self.askOrder()
        self.putValue()

    def askOrder(self):
        response = self.request.executeGet('SensorArmy/Sergeant/'+ 'pvt/order')
        if response == None: return
        order = response['order']
        if order in self.order_functions:
            result = self.order_functions[order](response)

        t = threading.Timer(self.beat_interval, self.askOrder)
        t.start()

    def putValue(self):
        value = "test_value"
        response = self.request.executeGet('SensorArmy/Sergeant/' + 'pvt/put?' + value)
        if response == None: return

        t = threading.Timer(self.put_interval, self.putValue)
        t.start()

    # order functions ----------------------------------------------------------
    def setInterval(self, values):
        self.put_interval = values['value']


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
    config_params = ('sgtaddr', 'sgtport')
    if conf.loadfile(conf_name, config_params) == False: quit(1)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    pvt = Private()
