import asyncio
import signal
import xmlrpc.server as xmlrpc_server
import xmlrpc.client as xmlrpc_client
import threading

LOOP = asyncio.get_event_loop()


class LeaderBase(object):

    def __init__(self):
        self.operations = {}
        self.subordinates = []

    def add_operation(self, op):
        print('got operation: {0}'.format(op))
        self.operations[op['purpose']] = op

        target_subs = []
        if op['place'] == "All":
            target_subs = self.subordinates
        for sub in target_subs:
            m_req = op['requirements']
            reqs = list(set(m_req).intersection(sub['weapons']))
            sub['rpcc'].add_order({
                'requirements': reqs,
                'trigger': op['trigger'],
                'purpose': op['purpose']
            })

    def add_subordinate(self, info):
        sub = {
            "name": info["name"],
            "rpcc": xmlrpc_client.ServerProxy(info["endpoint"])
        }
        sub['weapons'] = sub['rpcc'].list_weapons()
        self.subordinates.append(sub)

        for op in self.operations.values():
            # TODO: 必要に応じてdelete opすべき
            self.add_operation(op)

    def accept_data(self, data):
        print('got data: {0}'.format(data))


def main():
    leader = LeaderBase()
    leader.add_operation({
        'place': 'All',
        'requirements': ['zero', 'random'],
        'trigger': 2,
        'purpose': 'purp'
    })

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
