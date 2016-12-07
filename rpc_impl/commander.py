import asyncio
import xmlrpc.server as xmlrpc_server
import xmlrpc.client as xmlrpc_client
import threading

LOOP = asyncio.get_event_loop()


class CommanderBase(object):

    def __init__(self):
        self.missions = {}
        self.subordinates = []

    def add_mission(self, mission):
        print('got mission: {0}'.format(mission))
        self.missions[mission['purpose']] = mission

        target_subs = []
        if mission['place'] == "All":
            target_subs = self.subordinates
        for sub in target_subs:
            sub['rpcc'].add_operation({
                'place': mission['place'],
                'requirements': mission['requirements'],
                'trigger': mission['trigger'],
                'purpose': mission['purpose']
            })

    def add_subordinate(self, info):
        sub = {
            "name": info["name"],
            "rpcc": xmlrpc_client.ServerProxy(info["endpoint"])
        }
        self.subordinates.append(sub)

        for m in self.missions.values():
            # TODO: 必要に応じてdelete opすべき
            self.add_mission(m)

    def accept_data(self, data):
        print('got data: {0}'.format(data))


def main():
    commander = CommanderBase()
    commander.add_mission({
        'destination': 'mongodb://192.168.0.21:27017/troops/test',
        'place': 'All',
        'requirements': ['zero', 'random'],
        'trigger': 2,
        'purpose': 'purp'
    })

    server = xmlrpc_server.SimpleXMLRPCServer(
        ('127.0.0.1', 3002), allow_none=True)
    server.register_instance(commander)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
