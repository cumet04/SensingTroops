import json
import threading
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
import configfile
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from webapi import Request


class Private(object):

    def __init__(self):
        self.request = Request(conf.sgtaddr, conf.sgtport, 'SensorArmy/Sergeant')
        self.thread_list = []

        # join
        response = self.request.executeGet('pvt/join')
        if response is None: return
        self.soldier_id = response['id']
        self.put_interval = response['interval']
        self.beat_interval = response['heartbeat']

        # start beat/put thread
        beat_thread = threading.Thread(target=self.askOrder, daemon=True)
        self.thread_list.append(beat_thread)
        beat_thread.start()

        put_thread = threading.Thread(target=self.putValue, daemon=True)
        self.thread_list.append(put_thread)
        put_thread.start()

    def askOrder(self):
        # This function must be executed as a thread
        while True:
            uri = 'pvt/{0}/order'.format(self.soldier_id)
            response = self.request.executeGet(uri)
            if response == None: return

            for (key, value) in response.items():
                if key == 'interval':
                    self.put_interval = value
                elif key == 'heartbeat':
                    self.beat_interval = value

            time.sleep(self.beat_interval)

    def putValue(self):
        # This function must be executed as a thread
        while True:
            uri = 'pvt/{0}/put?{1}'.format(self.soldier_id, "test")
            response = self.request.executeGet(uri)
            if response == None: return

            time.sleep(self.put_interval)

    def shutdown(self):
        for t in self.thread_list:
            t.shutdown()

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

    # run main loop
    pvt = Private()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
