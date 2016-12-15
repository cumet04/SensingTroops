import argparse
import asyncio
import copy
import datetime
import random
import sys
import xmlrpc.client as xmlrpc_client
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
        self.weapons = {
            "zero": lambda: 0,
            "random": random.random
        }
        self.superior = None

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
        asyncio.ensure_future(self._working(
            event, order['requirements'], order['trigger']), loop=LOOP)
        order['event'] = event
        self.orders[order['purpose']] = order

    async def _working(self, event, reqs, interval):
        while not event.is_set():
            vals = []
            for k in reqs:
                time = datetime.datetime.now(datetime.timezone.utc).isoformat()
                vals.append({
                    'id': self.id,
                    'type': k,
                    'value': self.weapons[k](),
                    'time': time
                })
            self.superior['rpcc'].accept_data(vals)
            await asyncio.sleep(interval, loop=LOOP)


def main():
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

    soldier = SoldierBase()
    if not run_rpc(ip, port, soldier):
        logger.info('Address already in use')
        return

    # get self info
    recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
    resolved = recruiter.get_soldier(self_id)
    if resolved is None:
        logger.info("Soldier not found: ID = %s", self_id)
        return
    superior_ep = resolved['superior_ep']
    if superior_ep == '':
        logger.info("The superior's instance don't exist")  # TODO:
        return
    soldier.id = resolved['id']
    soldier.name = resolved['name']
    soldier.place = resolved['place']
    soldier.endpoint = endpoint

    # join
    client = xmlrpc_client.ServerProxy(superior_ep)
    client.add_subordinate(soldier.show_info())
    soldier.superior = {
        'rpcc': client
    }

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
