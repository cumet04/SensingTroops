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

        self.request = Request(conf.sgtaddr, conf.sgtport, 'SensorArmy/Sergeant')

        # join
        response = self.request.executeGet('pvt/join')
        if response == None: return
        self.soldier_id = response['id']
        self.put_interval = response['interval']
        self.beat_interval = response['heartbeat']

        self.askOrder()
        self.putValue()

    def askOrder(self):
        uri = 'pvt/{0}/order'.format(self.soldier_id)
        response = self.request.executeGet(uri)
        if response == None: return

        for (key, value) in response.items():
            if key == 'interval':
                self.put_interval = value
            elif key == 'heartbeat':
                self.beat_interval = value

        t = threading.Timer(self.beat_interval, self.askOrder)
        t.start()

    def putValue(self):
        uri = 'pvt/{0}/put?{1}'.format(self.soldier_id, "test")
        response = self.request.executeGet(uri)
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
