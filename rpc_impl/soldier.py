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

    def list_weapons(self):
        return list(self.weapons.keys())

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
    soldier = SoldierBase()

    # webサーバのループとasyncioのループをうまく共存させる方法がわからないため
    # スレッドを立てる方法でなんとかしている。
    # もっとスッキリできるといいのだが...
    server = xmlrpc_server.SimpleXMLRPCServer(
        ('127.0.0.1', 3000), allow_none=True)
    server.register_instance(soldier)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # join
    client = xmlrpc_client.ServerProxy('http://127.0.0.1:3001')
    client.add_subordinate({
        'name': 'soldier01',
        'endpoint': 'http://127.0.0.1:3000'
    })
    soldier.superior = {
        'rpcc': client
    }

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
