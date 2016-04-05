#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import yaml
from collections import namedtuple
from flask_cors import cross_origin
from common import json_input, LeaderInfo, CommanderInfo
from flask import Flask, jsonify, request
from flask_swagger import swagger
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


Squad = namedtuple('Squad', ['leader', 'subordinates'])
Troop = namedtuple('Troop', ['commander', 'subordinates'])


class Recruiter(object):
    
    def __init__(self):
        self.SquadList = []
        self.TroopList = []
        self.CommanderList = {}
        self.leader_cache = {}
        self.commander_cache = {}
        self.load_config('recruit.yml')

    def load_config(self, filename):
        """
        人事情報のconfigファイルを読み込んでパラメータセットする
        :param str filename: yaml形式で書かれた設定ファイルのファイル名
        """
        file = open(filename, 'r')
        data = yaml.load(file)
        file.close()

        for tr in data['troops']:
            troop = Troop(commander=tr['commander'],
                          subordinates=tr['subordinates'])
            self.TroopList.append(troop)

        for sq in data['squads']:
            squad = Squad(leader=sq['leader'],
                          subordinates=sq['subordinates'])
            self.SquadList.append(squad)

        logger.info('load_config done')
        logger.info('Troops: {0}'.format(self.TroopList))
        logger.info('Squads: {0}'.format(self.SquadList))

    def get_squad_leader(self, soldier_id):
        """
        指定されたSoldierの属するSquadの上官Leaderを返す
        :param str soldier_id: 取得したいLeaderの部下のID
        :return str: LeaderのID
        """
        squads = filter(lambda l: soldier_id in l.subordinates, self.SquadList)
        return squads[0].leader

    def get_troop_commander(self, leader_id):
        """
        指定されたLeaderの属するTroopの上官Commanderを返す
        :param str leader_id: 取得したいCommanderの部下のID
        :return str: CommanderのID
        """
        troops = filter(lambda l: leader_id in l.subordinates, self.TroopList)
        return troops[0].commander

    def resolve_leader(self, leader_id, force_retrieve=False):
        """
        Leaderの情報を上官Commanderから取得する
        :param str leader_id: 取得したいLeaderのID
        :param bool force_retrieve: キャッシュを無視して問い合わせるかどうか
        """
        if force_retrieve or (leader_id not in self.leader_cache):
            com_id = self.get_troop_commander(leader_id)
            com = self.commander_cache[com_id]

            path = 'http://{0}/subordinates/{1}'.format(com.endpoint, leader_id)
            res = requests.post(path, json=self.info._asdict()).json()

            leader = LeaderInfo(**res)
            self.leader_cache[leader.id] = leader

        return self.leader_cache[leader_id]

    def resolve_commander(self, commander_id):
        """
        CommanderのInfoを返す
        :param str commander_id: 取得したいCommanderのID
        """
        return self.commander_cache[commander_id]


# REST interface ---------------------------------------------------------------

server = Flask(__name__)
url_prefix = '/recruiter'


@server.route(url_prefix + '/department/squad/<soldier_id>', methods=['GET'])
def get_squad_superior(soldier_id):
    """
    指定されたsoldierが所属する分隊のLeaderのInfoを返す
    :param str soldier_id: 上官を調べたいSoldierのID
    """
    leader_id = app.get_squad_leader(soldier_id)
    info = app.resolve_leader(leader_id)
    if info is None:
        return jsonify(msg='LeaderID is found,' +
                           ' but the instance is not resolved.'), 500
    return jsonify(leader=info)


@server.route(url_prefix + '/department/troop/<leader_id>', methods=['GET'])
def get_troop_superior(leader_id):
    """
    指定されたleaderが所属する部隊のCommanderのInfoを返す
    :param str leader_id: 上官を調べたいLeaderのID
    """
    commander_id = app.get_troop_commander(leader_id)
    info = app.resolve_commander(commander_id)
    if info is None:
        return jsonify(msg='CommanderID is found,' +
                           ' but the instance is not registered.'), 500
    return jsonify(commander=info)


@server.route(url_prefix + '/error/squad', methods=['POST'])
@json_input
def add_squad_error():
    # TODO
    pass


@server.route(url_prefix + '/error/troop', methods=['POST'])
@json_input
def add_troop_error():
    # TODO
    pass


@server.route(url_prefix + '/commander', methods=['POST'])
@json_input
def add_commander():
    com = CommanderInfo(**request.json)
    app.CommanderList[com.id] = com
    return jsonify(msg='accepted', commander=com._asdict())


@server.route(url_prefix + '/spec', methods=['GET'])
@cross_origin()
def spec():
    return jsonify(swagger(server))

# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        self_port = int(sys.argv[1])
    else:
        self_port = 52000

    app = Recruiter()
    server.debug = True
    server.run(host='0.0.0.0', port=self_port,
               use_debugger=True, use_reloader=False)
