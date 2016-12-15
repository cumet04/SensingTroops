import argparse
import asyncio
import xmlrpc.client as xmlrpc_client
from time import sleep
from logging import getLogger, StreamHandler, DEBUG
from utils.utils import trace_error, run_rpc

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

LOOP = asyncio.get_event_loop()


class LeaderBase(object):

    def __init__(self):
        self.id = ''
        self.name = ''
        self.place = ''
        self.endpoint = ''
        self.operations = {}
        self.subordinates = {}
        self.superior = None

    @trace_error
    def show_info(self):
        """show_info() => {leader info}"""
        return {
            'type': 'Leader',
            'id': self.id,
            'name': self.name,
            'place': self.place,
            'endpoint': self.endpoint,
            'operations': self.operations
        }

    @trace_error
    def get_subordinates(self):
        subs = {}
        for k, v in self.subordinates.items():
            subs[k] = v['rpcc'].show_info()
        return subs

    @trace_error
    def add_operation(self, op):
        """add_operation(op: {operation}) => None"""
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

    @trace_error
    def add_subordinate(self, info):
        """add_subordinate(info: {soldier info}) => None"""
        info['rpcc'] = xmlrpc_client.ServerProxy(info["endpoint"])
        self.subordinates[info['id']] = info

        for op in self.operations.values():
            # TODO: 必要に応じてdelete opすべき
            self.add_operation(op)

    @trace_error
    def accept_data(self, data):
        """accept_data(data: {collected data}) => None"""
        self.superior['rpcc'].accept_data(data)


def get_self_info(recruiter_ep, self_id, retry_count):
    recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
    resolved = None
    retry_sleep = 2
    for i in range(retry_count):
        try:
            resolved = recruiter.get_leader(self_id)
        except ConnectionRefusedError:
            logger.info(
                "failed to connect to recruiter. retry %d sec after", retry_sleep)
            sleep(retry_sleep)
            retry_sleep = retry_sleep * 2
            continue
        break
    if retry_sleep == 2 * (2 ** retry_count):
        return "Couldn't connect to recruiter"

    if resolved is None:
        return "Leader not found: ID = %s" % self_id
    if resolved['superior_ep'] == '':
        return "The superior's instance don't exist"
    return resolved


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
    if not run_rpc(ip, port, leader):
        return 'Address already in use'

    info = get_self_info(recruiter_ep, self_id, 3)
    if isinstance(info, str):
        return info
    leader.id = info['id']
    leader.name = info['name']
    leader.place = info['place']
    leader.endpoint = endpoint

    # join
    client = xmlrpc_client.ServerProxy(info['superior_ep'])
    client.add_subordinate(leader.show_info())
    leader.superior = {
        'rpcc': client
    }

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    res = main()
    if res is not None:
        logger.error(res)
