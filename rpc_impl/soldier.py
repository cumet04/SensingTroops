import random
import asyncio
import xmlrpc.server as xmlrpc_server
import threading


class SoldierBase(object):

    def __init__(self):
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)
        asyncio.ensure_future(self.working(
            order["requirements"], order["trigger"]))

    async def working(self, reqs, interval):
        while True:
            vals = []
            for k in reqs:
                vals.append({
                    "type": k,
                    "value": getattr(self, "getvalue_" + k)()
                })
            print(vals)
            await asyncio.sleep(interval)

    def getvalue_zero(self):
        return 0

    def getvalue_random(self):
        return random.random()


def main():
    loop = asyncio.get_event_loop()
    soldier = SoldierBase()
    # soldier.add_order({
    #     "requirements": ["zero", "random"],
    #     "trigger": 2
    # })
    # print(soldier.orders)

    server = xmlrpc_server.SimpleXMLRPCServer(('127.0.0.1', 3000))
    server.register_instance(soldier)
    # webサーバのループとasyncioのループをうまく共存させる方法がわからないため
    # スレッドを立てる方法でなんとかしている。
    # もっとスッキリできるといいのだが...
    threading.Thread(target=server.serve_forever).start()
    loop.run_forever()

if __name__ == "__main__":
    main()
