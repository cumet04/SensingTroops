import random
import traceback
import sys
import argparse
import datetime
import asyncio
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


class SoldierBase(object):

    def __init__(self):
        self.orders = {}
        self.weapons = {
            "zero": lambda: 0,
            "random": random.random
        }
        self.superior = None

    @trace_error
    def add_order(self, order):
        print('got order: {0}'.format(order))
        if order['purpose'] in self.orders:
            self.orders[order['purpose']]['event'].set()
            del self.orders[order['purpose']]

        event = asyncio.Event(loop=LOOP)
        asyncio.ensure_future(self.working(
            event, order['requirements'], order['trigger']), loop=LOOP)
        order['event'] = event
        self.orders[order['purpose']] = order

    async def working(self, event, reqs, interval):
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-P', '--port', type=int, default=53000, help="rpc-server's port num")
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/")
    params = parser.parse_args()

    port = params.port
    self_id = params.id
    if self_id == '':
        self_id = 'S_' + str(port)
    ip = '127.0.0.1'
    endpoint = 'http://{0}:{1}'.format(ip, port)
    recruiter_ep = params.rec_addr

    soldier = SoldierBase()

    # webサーバのループとasyncioのループをうまく共存させる方法がわからないため
    # スレッドを立てる方法でなんとかしている。
    # もっとスッキリできるといいのだが...
    server = xmlrpc_server.SimpleXMLRPCServer(
        (ip, port), allow_none=True, logRequests=False)
    server.register_instance(soldier)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # get self info
    recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
    resolved = recruiter.get_soldier(self_id)
    if resolved is None:
        logger.info("Soldier not found: ID = %s", self_id)
        return
    superior_ep = resolved['superior_ep']
    if superior_ep == '':
        logger.info("The superior's instance don't exist")
        return
    info = {
        'id': resolved['id'],  # same as self_id
        'name': resolved['name'],
        'place': resolved['place'],
        'weapons': list(soldier.weapons.keys()),
        'endpoint': endpoint
    }
    soldier.id = info['id']
    soldier.name = info['name']

    # join
    client = xmlrpc_client.ServerProxy(superior_ep)
    client.add_subordinate(info)
    soldier.superior = {
        'rpcc': client
    }

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
