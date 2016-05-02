#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
import yaml
import argparse
import os
from collections import namedtuple
from flask_cors import cross_origin
from objects import LeaderInfo, CommanderInfo
from utils import json_input
from flask import Flask, jsonify, request, render_template, Blueprint
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
        squads = list(filter(
                    lambda l: soldier_id in l.subordinates,
                    self.SquadList))
        if len(squads) == 0:
            return None
        return squads[0].leader

    def get_troop_commander(self, leader_id):
        """
        指定されたLeaderの属するTroopの上官Commanderを返す
        :param str leader_id: 取得したいCommanderの部下のID
        :return str: CommanderのID
        """
        troops = list(filter(
                    lambda l: leader_id in l.subordinates,
                    self.TroopList))
        if len(troops) == 0:
            return None
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


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

server = Blueprint('recruiter', __name__)
_app = Recruiter()


@server.route('/department/squad/leader', methods=['GET'])
def get_squad_leader():
    """
    Leader's info, top of a squad
    ---
    parameters:
      - name: soldier_id
        description: A soldier's ID who is under the requested leader
        in: query
        required: true
        type: string
    responses:
      200:
        description: ok
        schema:
          properties:
            leader:
              $ref: '#/definitions/LeaderInfo'
      400:
        description: Query-param soldier_id is required.
      404:
        description: Specified soldier does not exist on database.
      500:
        description: LeaderID is found, but the instance is not resolved.
    """
    msgs = {
        400: "Query param: soldier_id is required.",
        404: "Specified soldier does not exist on database.",
        500: "LeaderID is found, but the instance is not resolved."
    }
    try:
        soldier_id = request.args.get('soldier_id', type=str)
    except ValueError:
        return jsonify(msg=msgs[400]), 400

    leader_id = _app.get_squad_leader(soldier_id)
    if leader_id is None:
        return jsonify(msg=msgs[404]), 404

    info = _app.resolve_leader(leader_id)
    if info is None:
        return jsonify(msg=msgs[500]), 500

    return jsonify(leader=info)


@server.route('/department/squad/soldiers', methods=['GET'])
def get_squad_soldiers():
    """
    [NIY] A list of soldiers who are in a squad
    ---
    parameters:
      - name: leader_id
        description: A leader's ID who is top of the requested squad
        in: query
        required: true
        type: string
    responses:
      200:
        description: ok
        schema:
          properties:
            soldiers:
              type: array
              items:
                $ref: '#/definitions/SoldierInfo'
      400:
        description: Query-param leader_id is required.
      404:
        description: Specified leader does not exist on database.
    """
    msgs = {
        400: "Query param: leader_id is required.",
        404: "Specified leader does not exist on database.",
    }
    try:
        leader_id = request.args.get('leader_id', type=str)
    except ValueError:
        return jsonify(msg=msgs[400]), 400

    return jsonify(msg='this function is not implemented yet.'), 500


@server.route('/department/troop/commander', methods=['GET'])
def get_troop_commander():
    """
    Commander's info, top of a troop
    ---
    parameters:
      - name: leader_id
        description: A leader's ID who is under the requested commander
        in: query
        required: true
        type: string
    responses:
      200:
        description: ok
        schema:
          properties:
            leader:
              $ref: '#/definitions/CommanderInfo'
      400:
        description: Query-param leader_id is required.
      404:
        description: Specified leader does not exist on database.
      500:
        description: CommanderID is found, but the instance is not resolved.
    """
    msgs = {
        400: "Query param: leader_id is required.",
        404: "Specified leader does not exist on database.",
        500: "Commander is found, but the instance is not registered."
    }
    try:
        leader_id = request.args.get('leader_id', type=str)
    except ValueError:
        return jsonify(msg=msgs[400]), 400

    commander_id = _app.get_squad_leader(leader_id)
    if commander_id is None:
        return jsonify(msg=msgs[404]), 404

    info = _app.resolve_leader(commander_id)
    if info is None:
        return jsonify(msg=msgs[500]), 500

    return jsonify(leader=info)


@server.route('/department/troop/leaders', methods=['GET'])
def get_troop_leaders():
    """
    [NIY] A list of leaders who are in a troop
    ---
    parameters:
      - name: commander_id
        description: A commander's ID who is top of the requested troop
        in: query
        required: true
        type: string
    responses:
      200:
        description: ok
        schema:
          properties:
            leaders:
              type: array
              items:
                $ref: '#/definitions/LeaderInfo'
      400:
        description: Query-param commander_id is required.
      404:
        description: Specified commander does not exist on database.
    """
    msgs = {
        400: "Query param: commander_id is required.",
        404: "Specified commander does not exist on database.",
    }
    try:
        commander_id = request.args.get('commander_id', type=str)
    except ValueError:
        return jsonify(msg=msgs[400]), 400

    return jsonify(msg='this function is not implemented yet.'), 500


@server.route('/commander', methods=['GET'])
@json_input
def get_commanders():
    """
    [NIY] Commanders info who are registered
    ---
    parameters: []
    responses:
      200:
        description: ok
        schema:
          properties:
            commanders:
              type: array
              items:
                $ref: '#/definitions/CommanderInfo'
    """
    return jsonify(msg='this function is not implemented yet.'), 500


@server.route('/commander', methods=['POST'])
@json_input
def add_commander():
    """
    Add a commander for actual troop-info
    ---
    parameters:
      - name: commander
        in: body
        required: true
        schema:
          $ref: '#/definitions/CommanderInfo'
    responses:
      200:
        description: ok
        schema:
          properties:
            commander:
              $ref: '#/definitions/CommanderInfo'
    """
    com = CommanderInfo(**request.json)
    _app.CommanderList[com.id] = com
    return jsonify(commander=com._asdict())


@server.route('/error/squad', methods=['POST'])
@json_input
def add_squad_error():
    # TODO
    return jsonify(msg='this function is not implemented yet.'), 500


@server.route('/error/troop', methods=['POST'])
@json_input
def add_troop_error():
    # TODO
    return jsonify(msg='this function is not implemented yet.'), 500


def set_params(config_path):
    _app.load_config(config_path)
