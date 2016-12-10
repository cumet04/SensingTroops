import asyncio
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


class LeaderBase(object):

    def __init__(self):
        self.operations = {}
        self.subordinates = {}
        self.superior = None

    def add_operation(self, op):
        print('got operation: {0}'.format(op))
        self.operations[op['purpose']] = op

        target_subs = {}
        if op['place'] == "All":
            target_subs = self.subordinates
        for sub in target_subs.values():
            m_req = op['requirements']
            reqs = list(set(m_req).intersection(sub['weapons']))
            sub['rpcc'].add_order({
                'requirements': reqs,
                'trigger': op['trigger'],
                'purpose': op['purpose']
            })

    def add_subordinate(self, info):
        info['rpcc'] = xmlrpc_client.ServerProxy(info["endpoint"])
        self.subordinates[info['id']] = info

        for op in self.operations.values():
            # TODO: 必要に応じてdelete opすべき
            self.add_operation(op)

    def accept_data(self, data):
        print('got data: {0}'.format(data))
        self.superior['rpcc'].accept_data(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-P', '--port', type=int, default=52000, help="rpc-server's port num")
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/")
    params = parser.parse_args()

    port = params.port
    self_id = params.id
    if self_id == '':
        self_id = 'L_' + str(port)
    ip = '127.0.0.1'
    endpoint = 'http://{0}:{1}'.format(ip, port)
    recruiter_ep = params.rec_addr

    leader = LeaderBase()
    server = xmlrpc_server.SimpleXMLRPCServer(
        (ip, port), allow_none=True, logRequests=False)
    server.register_instance(leader)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # get self info
    recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
    resolved = recruiter.get_leader(self_id)
    if resolved is None:
        logger.info("Leader not found: ID = %d", self_id)
        return
    superior_ep = resolved['superior_ep']
    if superior_ep == '':
        logger.info("The superior's instance don't exist")
        return
    info = {
        'id': resolved['id'],  # same as self_id
        'name': resolved['name'],
        'place': resolved['place'],
        'endpoint': endpoint
    }

    # join
    client = xmlrpc_client.ServerProxy(superior_ep)
    client.add_subordinate(info)
    leader.superior = {
        'rpcc': client
    }

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
