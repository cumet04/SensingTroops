import asyncio
import signal
import xmlrpc.server as xmlrpc_server
import xmlrpc.client as xmlrpc_client
import threading

LOOP = asyncio.get_event_loop()


class LeaderBase(object):

    def __init__(self):
        self.operations = []
        self.subordinates = []

    def add_operation(self, ops):
        self.operations.append(ops)

    def add_subordinate(self, info):
        sub = {
            "name": info["name"],
            "rpcc": xmlrpc_client.ServerProxy(info["endpoint"])
        }
        self.subordinates.append(sub)

        # FIXME: 暫定コード
        sub["rpcc"].add_order({
            "requirements": ["zero", "random"],
            "trigger": 2
        })

    def accept_data(self, data):
        print('got data: {0}'.format(data))


def main():
    leader = LeaderBase()

    server = xmlrpc_server.SimpleXMLRPCServer(
        ('127.0.0.1', 3001), allow_none=True)
    server.register_instance(leader)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
