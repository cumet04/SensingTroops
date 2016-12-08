import random
import asyncio
import xmlrpc.server as xmlrpc_server
import xmlrpc.client as xmlrpc_client
import threading

LOOP = asyncio.get_event_loop()


class SoldierBase(object):

    def __init__(self):
        self.orders = {}
        self.weapons = {
            "zero": lambda: 0,
            "random": random.random
        }
        self.superior = None

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
                vals.append({
                    "type": k,
                    "value": self.weapons[k]()
                })
            self.superior['rpcc'].accept_data(vals)
            await asyncio.sleep(interval, loop=LOOP)


def main():
    port = 53000
    self_id = 'S_' + str(port)
    ip = '127.0.0.1'
    endpoint = 'http://{0}:{1}'.format(ip, port)

    soldier = SoldierBase()

    # webサーバのループとasyncioのループをうまく共存させる方法がわからないため
    # スレッドを立てる方法でなんとかしている。
    # もっとスッキリできるといいのだが...
    server = xmlrpc_server.SimpleXMLRPCServer(
        (ip, port), allow_none=True, logRequests=False)
    server.register_instance(soldier)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # get self info
    recruiter = xmlrpc_client.ServerProxy('http://127.0.0.1:50000')
    resolved = recruiter.get_soldier(self_id)
    superior_ep = resolved['superior_ep']
    info = {
        'id': resolved['id'],  # same as self_id
        'name': resolved['name'],
        'place': resolved['place'],
        'weapons': list(soldier.weapons.keys()),
        'endpoint': endpoint
    }

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
