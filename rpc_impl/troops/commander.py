import argparse
import asyncio
import copy
from time import sleep
import xmlrpc.client as xmlrpc_client
from logging import getLogger, StreamHandler, DEBUG
from utils.utils import trace_error, run_rpc

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

LOOP = asyncio.get_event_loop()


class CommanderBase(object):

    def __init__(self):
        self.id = ''
        self.name = ''
        self.place = ''
        self.endpoint = ''
        self.missions = {}
        self.subordinates = {}

    @trace_error
    def show_info(self):
        """show_info() => {commander info}"""
        return {
            'type': 'Commander',
            'id': self.id,
            'name': self.name,
            'place': self.place,
            'endpoint': self.endpoint,
            'missions': self.missions
        }

    @trace_error
    def retrieve_troop_info(self):
        """retrieve_troop_info() => {troop info}"""
        leaders = self.get_subordinates()
        for k, v in leaders.items():
            subs = self.subordinates[k]['rpcc'].get_subordinates()
            v['subs'] = subs
        hierarchy = self.show_info()
        hierarchy['subs'] = leaders
        return hierarchy

    @trace_error
    def get_subordinates(self):
        subs = {}
        for k, v in self.subordinates.items():
            subs[k] = v['rpcc'].show_info()
        return subs

    @trace_error
    def add_mission(self, mission):
        """add_mission(mission: {mission}) => None"""
        print('got mission: {0}'.format(mission))
        if 'mongo' not in mission:
            mission['mongo'] = MongoPush(mission['destination'])
        self.missions[mission['purpose']] = mission

        target_subs = {}
        if mission['place'] == "All":
            target_subs = self.subordinates
        for sub in target_subs.values():
            sub['rpcc'].add_operation({
                'place': mission['place'],
                'requirements': mission['requirements'],
                'trigger': mission['trigger'],
                'purpose': mission['purpose']
            })

    @trace_error
    def add_subordinate(self, info):
        """add_subordinate(info: {leader info}) => None"""
        info['rpcc'] = xmlrpc_client.ServerProxy(info["endpoint"])
        self.subordinates[info['id']] = info

        for m in self.missions.values():
            # TODO: 必要に応じてdelete opすべき
            self.add_mission(m)

    @trace_error
    def get_subordinate(self, sub_id):
        """get_subordinate(sub_id: str) => {leader info}"""
        if sub_id not in self.subordinates:
            return None
        # rpc clientはRPCのレスポンスで返せないので消してから返す
        res = copy.copy(self.subordinates[sub_id])
        res.pop('rpcc', None)
        return res

    @trace_error
    def accept_data(self, data):
        """accept_data(data: {collected data}) => None"""
        push_data = [{
            'purpose': data['purpose'],
            'place': data['place'],
            'time': data['time'],
            'data': v
        } for v in data['values']]
        self.missions[data['purpose']]['mongo'].push_values(push_data)

        import json
        print('push data: %s' % json.dumps(push_data))

    def _identify(self, recruiter_ep, self_id, retry_count):
        recruiter = xmlrpc_client.ServerProxy(recruiter_ep)
        resolved = None
        retry_sleep = 2
        for i in range(retry_count):
            try:
                resolved = recruiter.get_commander(self_id)
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
            return "Commander not found: ID = %s" % self_id
        if not recruiter.register_commander(self_id, self.endpoint):
            return "Failed to register commander info"

        self.id = resolved['id']
        self.name = resolved['name']
        self.place = resolved['place']

        return True


class MongoPush(object):

    def __init__(self, uri):
        import pymongo
        import re
        match_result = re.match(r"mongodb://(.*?)/(.*?)/(.*)", uri)
        if match_result is None:
            logger.error("uri is not mongodb-uri: %s", uri)
            return
        host = match_result.group(1)
        db_name = match_result.group(2)
        col_name = match_result.group(3)
        client = pymongo.MongoClient(host)
        try:
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            logger.error("failed to connect to mongodb: %s", uri)
        self.col = client[db_name][col_name]

    def push_values(self, values):
        import dateutil.parser
        if len(values) == 0:
            return

        # time変換とinsert_manyがvaluesの影響をメソッド外に波及しないように
        vals = copy.deepcopy(values)

        # timeの値を文字列からdatetime型に変換する
        [v.update({"time": dateutil.parser.parse(v["time"])}) for v in vals]

        self.col.insert_many(vals)
        # FIXME: DB接続できてなかったり落ちてたら再接続するとかキャッシュするとか
        # 必要だとは思う


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-P', '--port', type=int, default=51000, help="rpc-server's port num")
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/")
    params = parser.parse_args()

    port = params.port
    self_id = params.id
    if self_id == '':
        self_id = 'C_' + str(port)
    ip = '127.0.0.1'
    endpoint = 'http://{0}:{1}'.format(ip, port)
    recruiter_ep = params.rec_addr

    commander = CommanderBase()
    if not run_rpc(ip, port, commander):
        return "Address already in use"

    commander.endpoint = endpoint
    ris_identified = commander._identify(recruiter_ep, self_id, 3)
    if ris_identified != True:
        return ris_identified

    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass
    return None

if __name__ == "__main__":
    r = main()
    if r is not None:
        logger.error('commander failed: ' + r)
