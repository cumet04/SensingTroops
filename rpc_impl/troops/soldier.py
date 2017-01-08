import argparse
import asyncio
import copy
import datetime
import random
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


class SoldierBase(object):

    def __init__(self):
        self.id = ''
        self.name = ''
        self.place = ''
        self.endpoint = ''
        self.orders = {}
        self.superior = None
        self.superior_ep = None

        async def get_zero():
            return (0, '-')
        async def get_random():
            return (random.random(), '-')

        self.weapons = {
            "zero": get_zero,
            "random": get_random
        }

    @trace_error
    def show_info(self):
        """show_info() => {soldier info}"""
        info = {
            'type': 'Soldier',
            'id': self.id,
            'name': self.name,
            'place': self.place,
            'endpoint': self.endpoint,
            'weapons': list(self.weapons.keys()),
            'orders': self.get_orders()
        }
        return info

    @trace_error
    def get_orders(self):
        res = copy.copy(self.orders)
        for o in res.values():
            if 'event' in o:
                o.pop('event')
        return res

    @trace_error
    def add_order(self, order):
        """add_order(order: {order}) => None"""
        print('got order: {0}'.format(order))
        if order['purpose'] in self.orders:
            self.orders[order['purpose']]['event'].set()
            del self.orders[order['purpose']]

        event = asyncio.Event(loop=LOOP)
        asyncio.ensure_future(self._working(order), loop=LOOP)
        order['event'] = event
        self.orders[order['purpose']] = order

    def _identify(self, recruiter_ep, self_id, retry_count):
        recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
        resolved = None
        retry_sleep = 2
        for i in range(retry_count):
            try:
                resolved = recruiter.get_soldier(self_id)
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
            return "Soldier not found: ID = %s" % self_id
        if resolved['superior_ep'] == '':
            return "The superior's instance don't exist"

        self.id = resolved['id']
        self.name = resolved['name']
        self.place = resolved['place']
        self.superior_ep = resolved['superior_ep']

        return True

    def _join(self):
        client = xmlrpc_client.ServerProxy(self.superior_ep)
        retry_sleep = 2
        for i in range(5):
            try:
                client.add_subordinate(self.show_info())
            except ConnectionRefusedError:
                logger.info(
                    "failed to connect to superior. retry %d sec after", retry_sleep)
                sleep(retry_sleep)
                retry_sleep = retry_sleep * 2
                continue
            break
        if retry_sleep == 2 * (2 ** 5):
            return "Couldn't connect to commander"

        self.superior = {
            'rpcc': client
        }
        return True

    async def _working(self, order):
        while not order['event'].is_set():
            tasks = [asyncio.ensure_future(self.weapons[k](), loop=LOOP)
                     for k in order['requirements']]
            await asyncio.wait(tasks, loop=LOOP)

            time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            self.superior['rpcc'].accept_data({
                'purpose': order['purpose'],
                'id': self.id,
                'place': self.place,
                'time': time,
                'values': [{
                    'type': order['requirements'][i],
                    'value': tasks[i].result()[0],
                    'unit': tasks[i].result()[1]
                } for i in range(len(tasks))]
            })
            await asyncio.sleep(order['trigger'], loop=LOOP)


def main(soldier):
    # read args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-P', '--port', type=int, default=53000, help="rpc-server's port num")
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/")
    params = parser.parse_args()

    # set params
    port = params.port
    self_id = params.id
    if self_id == '':
        self_id = 'S_' + str(port)
    ip = '127.0.0.1'
    endpoint = 'http://{0}:{1}'.format(ip, port)
    recruiter_ep = params.rec_addr

    if not run_rpc(ip, port, soldier):
        return "Address already in use"

    is_identified = soldier._identify(recruiter_ep, self_id, 3)
    if is_identified != True:
        return is_identified
    soldier.endpoint = endpoint

    is_joined = soldier._join()
    if is_joined != True:
        return is_joined

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass
    return None


if __name__ == "__main__":
    s = SoldierBase()
    r = main(s)
    if r is not None:
        logger.error(r)
