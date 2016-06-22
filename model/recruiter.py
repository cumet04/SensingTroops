import yaml
import utils.rest as rest
from model import CommanderInfo, LeaderInfo
from collections import namedtuple
from model import logger

Squad = namedtuple('Squad', ['leader', 'subordinates'])
Troop = namedtuple('Troop', ['commander', 'subordinates'])


class Recruiter(object):
    def __init__(self, config_name):
        self.SquadList = {}
        self.TroopList = {}
        self.leader_cache = {}
        self.commander_cache = {}
        self.endpoints = {}
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
            self.endpoints[com_id] = tr["place"]
            subs = tr['subordinates']
            self.TroopList[com_id] = subs

        for sq in data['squads']:
            lea_id = sq['leader']
            self.endpoints[lea_id] = sq["place"]
            subs = []
            for s in sq["subordinates"]:
                subs.append(s["soldier"])
                self.endpoints[s["soldier"]] = s["place"]
            self.SquadList[lea_id] = subs

        logger.info('load_config done')
        logger.info('Troops: {0}'.format(self.TroopList))
        logger.info('Squads: {0}'.format(self.SquadList))

    def register_commander_info(self, com_info: CommanderInfo):
        if com_info.id not in self.TroopList:
            return None
        com_info.place = self.endpoints[com_info.id]
        self.commander_cache[com_info.id] = com_info
        return com_info

    def get_leader_ep(self, leader_id):
        return self.endpoints.get(leader_id, None)

    def get_soldier_ep(self, soldier_id):
        return self.endpoints.get(soldier_id, None)

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
        url = "{0}subordinates/{1}".format(com_info.endpoint, leader_id)
        res, err = rest.get(url)
        if err is not None:
            return None

        return LeaderInfo.make(res.json()["info"])
        # TODO: キャッシュまわり

    def resolve_commander(self, commander_id) -> CommanderInfo:
        """
        CommanderのInfoを返す
        :param str commander_id: 取得したいCommanderのID
        """
        if commander_id not in self.commander_cache:
            return None
        return self.commander_cache[commander_id]
