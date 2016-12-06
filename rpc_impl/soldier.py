import random
import signal
import asyncio
import xmlrpc.server as xmlrpc_server
import xmlrpc.client as xmlrpc_client
import threading

LOOP = asyncio.get_event_loop()


class SoldierBase(object):

    def __init__(self):
        self.orders = []
        self.weapons = {
            "zero": lambda: 0,
            "random": random.random
        }
        self.superior = None

    def list_weapons(self):
        return list(self.weapons.keys())

    def add_order(self, order):
        self.orders.append(order)
        asyncio.ensure_future(self.working(
            order["requirements"], order["trigger"]), loop=LOOP)

    async def working(self, reqs, interval):
        while True:
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

    async def join():
        await asyncio.sleep(0.1)
        client = xmlrpc_client.ServerProxy('http://127.0.0.1:3001')
        client.add_subordinate({
            'name': 'soldier01',
            'endpoint': 'http://127.0.0.1:3000'
        })
        soldier.superior = {
            'rpcc': client
        }
    asyncio.ensure_future(join(), loop=LOOP)

    # webサーバのループとasyncioのループをうまく共存させる方法がわからないため
    # スレッドを立てる方法でなんとかしている。
    # もっとスッキリできるといいのだが...
    server = xmlrpc_server.SimpleXMLRPCServer(
        ('127.0.0.1', 3000), allow_none=True)
    server.register_instance(soldier)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
