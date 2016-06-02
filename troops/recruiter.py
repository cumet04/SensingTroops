#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import argparse
import os
from utils.commander_client import CommanderClient
from utils.objects import CommanderInfo, ResponseStatus, definitions
from utils.helpers import json_input, asdict
from collections import namedtuple
from flask_cors import cross_origin
from flask import Flask, jsonify, request, render_template, Blueprint
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
        self.SquadList = {}
        self.TroopList = {}
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

    def resolve_leader(self, leader_id, force_retrieve=False):
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

    def resolve_commander(self, commander_id):
        """
        CommanderのInfoを返す
        :param str commander_id: 取得したいCommanderのID
        """
        if commander_id not in self.commander_cache:
            return None
        return self.commander_cache[commander_id]


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

app = Blueprint('recruiter', __name__)
_recruiter = None  # type:Recruiter
url_prefix = '/recruiter'


def initialize_app(config_path):
    global _recruiter
    _recruiter = Recruiter()
    _recruiter.load_config(config_path)


@app.route('/commanders', methods=['GET'])
@json_input
def get_commanders():
    """
    A list of Commander's ID, that is registered in config
    ---
    parameters: []
    responses:
      200:
        description: ok
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            commanders:
              type: array
              items:
                type: string
    """
    id_list = list(_recruiter.TroopList.keys())
    return jsonify(_status=ResponseStatus.Success, commanders=id_list)


@app.route('/commanders/<com_id>', methods=['GET'])
@json_input
def get_commander_info(com_id):
    """
    Registered actual commander's info
    指定されたIDに対応するCommanderInfoを返す
    configには存在するが実体が未登録のIDを指定した場合は空オブジェクトを返す
    ---
    parameters:
      - name: com_id
        description: ID of a requested commander
        in: path
        type: string
    responses:
      200:
        description: ok
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            commander:
              $ref: '#/definitions/CommanderInfo'
      404:
        description: Specified Commander ID is not found on DB
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    if com_id not in _recruiter.TroopList:
        return jsonify(_status=ResponseStatus.NotFound), 404

    info = _recruiter.resolve_commander(com_id)
    if info is None:
        return jsonify(_status=ResponseStatus.Success, commander={})
    return jsonify(_status=ResponseStatus.Success, commander=asdict(info))


@app.route('/commanders/<com_id>', methods=['PUT'])
@json_input
def register_commanders(com_id):
    """
    Register a commander
    ---
    parameters:
      - name: com_id
        description: ID of a requested commander
        in: path
        type: string
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
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            commander:
              $ref: '#/definitions/CommanderInfo'
      400:
        description: '[NT] invalid input'
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            input:
              $ref: '#/definitions/CommanderInfo'
    """
    msgs = {
        400: "Input parameter is invalid",
    }

    try:
        com = CommanderInfo(**request.json)
    except TypeError:
        return jsonify(_status=ResponseStatus.make_error(msgs[400]),
                       input=request.json), 400
    if com.id != com_id:
        return jsonify(_status=ResponseStatus.make_error(msgs[400]),
                       input=request.json), 400

    _recruiter.commander_cache[com_id] = com
    return jsonify(_status=ResponseStatus.Success, commander=asdict(com))


@app.route('/department/squad/leader', methods=['GET'])
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
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            leader:
              $ref: '#/definitions/LeaderInfo'
      400:
        description: Query-param soldier_id is required.
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
      404:
        description: Specified soldier does not exist on database.
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
      500:
        description: "[NT] LeaderID is found, but the instance is not resolved"
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    msgs = {
        400: "Query param: soldier_id is required",
        404: "Specified soldier does not exist on database",
        500: "LeaderID was found, but the instance was not resolved"
    }
    soldier_id = request.args.get('soldier_id', type=str)
    if soldier_id is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[400])), 400

    leader_id = _recruiter.get_squad_leader(soldier_id)
    if leader_id is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[404])), 404

    info = _recruiter.resolve_leader(leader_id)
    if info is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[500])), 500

    return jsonify(_status=ResponseStatus.Success, leader=info)


@app.route('/department/troop/commander', methods=['GET'])
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
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            commander:
              $ref: '#/definitions/CommanderInfo'
      400:
        description: Query-param leader_id is required.
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
      404:
        description: Specified leader does not exist on database.
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
      500:
        description: CommanderID is found, but the instance is not resolved.
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    msgs = {
        400: "Query-param leader_id is required",
        404: "Specified leader does not exist on database",
        500: "Commander is found, but the instance is not registered"
    }
    leader_id = request.args.get('leader_id', type=str)
    if leader_id is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[400])), 400

    commander_id = _recruiter.get_troop_commander(leader_id)
    if commander_id is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[404])), 404

    info = _recruiter.resolve_commander(commander_id)
    if info is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[500])), 500

    return jsonify(_status=ResponseStatus.Success, commander=asdict(info))


@app.route('/error/squad', methods=['POST'])
@json_input
def add_squad_error():
    # TODO
    return jsonify(msg='this function is not implemented yet.'), 500


@app.route('/error/troop', methods=['POST'])
@json_input
def add_troop_error():
    # TODO
    return jsonify(msg='this function is not implemented yet.'), 500


@app.route('/spec.json')
@cross_origin()
def spec_json():
    spec_dict = swagger(server, template={'definitions': definitions})
    spec_dict['info']['title'] = 'SensingTroops'
    return jsonify(spec_dict)


@app.route('/spec.html')
def spec_html():
    return render_template('swagger_ui.html',
                           spec_url=url_prefix + '/spec.json')


# ------------------------------------------------------------------------------
# entry point ------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-P', '--port', type=int, default=50000, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/recruiter', help='url prefix')
    args = parser.parse_args()
    url_prefix = args.prefix

    config = '{0}/recruit.yml'.format(os.path.dirname(__file__))
    initialize_app(config)

    server = Flask(__name__)
    server.debug = True
    server.register_blueprint(app, url_prefix=url_prefix)
    server.run(host='0.0.0.0', port=args.port, use_reloader=False)
