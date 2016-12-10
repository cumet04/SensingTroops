import asyncio
import traceback
import sys
import copy
import argparse
import xmlrpc.server as xmlrpc_server
import xmlrpc.client as xmlrpc_client
from logging import getLogger, StreamHandler, DEBUG
import threading

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

LOOP = asyncio.get_event_loop()


def trace_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print(traceback.format_exc(), file=sys.stderr)
    return wrapper


class CommanderBase(object):

    def __init__(self):
        self.missions = {}
        self.subordinates = {}

    @trace_error
    def add_mission(self, mission):
        print('got mission: {0}'.format(mission))
        self.missions[mission['purpose']] = mission

        target_subs = {}
        if mission['place'] == "All":
            target_subs = self.subordinates
        for sub in target_subs.values():
            sub['rpcc'].add_operation({
                'place': mission['place'],
                'requirements': mission['requirements'],
                'trigger': mission['trigger'],
                'purpose': mission['purpose']
            })

    @trace_error
    def add_subordinate(self, info):
        info['rpcc'] = xmlrpc_client.ServerProxy(info["endpoint"])
        self.subordinates[info['id']] = info

        for m in self.missions.values():
            # TODO: 必要に応じてdelete opすべき
            self.add_mission(m)

    @trace_error
    def get_subordinate(self, sub_id):
        if sub_id not in self.subordinates:
            return None
        # rpc clientはRPCのレスポンスで返せないので消してから返す
        res = copy.copy(self.subordinates[sub_id])
        res.pop('rpcc', None)
        return res

    @trace_error
    def accept_data(self, data):
        print('got data: {0}'.format(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-P', '--port', type=int, default=51000, help="rpc-server's port num")
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/")
    params = parser.parse_args()

    port = params.port
    self_id = params.id
    if self_id == '':
        self_id = 'C_' + str(port)
    ip = '127.0.0.1'
    endpoint = 'http://{0}:{1}'.format(ip, port)
    recruiter_ep = params.rec_addr

    commander = CommanderBase()
    commander.add_mission({
        'destination': 'mongodb://192.168.0.21:27017/troops/test',
        'place': 'All',
        'requirements': ['zero', 'random'],
        'trigger': 2,
        'purpose': 'purp'
    })
    server = xmlrpc_server.SimpleXMLRPCServer(
        (ip, port), allow_none=True, logRequests=False)
    server.register_instance(commander)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # get self info
    recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
    resolved = recruiter.get_commander(self_id)
    if resolved is None:
        logger.info("Commander not found: ID = %s", self_id)
        return

    if not recruiter.register_commander(self_id, endpoint):
        logger.info("Failed to register commander info")
        return

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
