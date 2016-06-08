import yaml
from model import CommanderInfo, LeaderInfo
from utils.commander_client import CommanderClient
from collections import namedtuple
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

Squad = namedtuple('Squad', ['leader', 'subordinates'])
Troop = namedtuple('Troop', ['commander', 'subordinates'])


class Recruiter(object):
    def __init__(self, config_name):
        self.SquadList = {}
        self.TroopList = {}
        self.leader_cache = {}
        self.commander_cache = {}
        self.load_config(config_name)

    def load_config(self, filename):
        """
        人事情報のconfigファイルを読み込んでパラメータセットする
        :param str filename: yaml形式で書かれた設定ファイルのファイル名
        """
        file = open(filename, 'r')
        data = yaml.load(file)
        file.close()

        for tr in data['troops']:
            com_id = tr['commander']
            subs = tr['subordinates']
            self.TroopList[com_id] = subs

        for sq in data['squads']:
            lea_id = sq['leader']
            subs = sq['subordinates']
            self.SquadList[lea_id] = subs

        logger.info('load_config done')
        logger.info('Troops: {0}'.format(self.TroopList))
        logger.info('Squads: {0}'.format(self.SquadList))

    def get_squad_leader(self, soldier_id):
        """
        指定されたSoldierの属するSquadの上官Leaderを返す
        :param str soldier_id: 取得したいLeaderの部下のID
        :return str: LeaderのID
        """
        for leader_id, subordinates in self.SquadList.items():
            if soldier_id in subordinates:
                return leader_id
        return None

    def get_troop_commander(self, leader_id):
        """
        指定されたLeaderの属するTroopの上官Commanderを返す
        :param str leader_id: 取得したいCommanderの部下のID
        :return str: CommanderのID
        """
        for commander_id, subordinates in self.TroopList.items():
            if leader_id in subordinates:
                return commander_id
        return None

    def resolve_leader(self, leader_id, force_retrieve=False) -> LeaderInfo:
        """
        Leaderの情報を上官Commanderから取得する
        :param str leader_id: 取得したいLeaderのID
        :param bool force_retrieve: キャッシュを無視して問い合わせるかどうか
        """
        # TODO: エラー処理
        com_id = self.get_troop_commander(leader_id)
        com_info = self.commander_cache[com_id]
        com_client = CommanderClient.gen_rest_client(com_info.endpoint)
        lea_info, err = com_client.get_subordinates_spec(leader_id)

        return lea_info
        # TODO: キャッシュまわり

    def resolve_commander(self, commander_id) -> CommanderInfo:
        """
        CommanderのInfoを返す
        :param str commander_id: 取得したいCommanderのID
        """
        if commander_id not in self.commander_cache:
            return None
        return self.commander_cache[commander_id]
