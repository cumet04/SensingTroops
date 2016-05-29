#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
import yaml
import argparse
import os
import utils
from collections import namedtuple
from flask_cors import cross_origin
from objects import LeaderInfo, CommanderInfo, ResponseStatus, definitions
from utils import json_input, asdict, RestClient
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
        if force_retrieve or (leader_id not in self.leader_cache):
            com_id = self.get_troop_commander(leader_id)
            com = self.commander_cache[com_id]

            path = 'http://{0}/subordinates/{1}'.format(com.endpoint, leader_id)
            res = requests.post(path, json=asdict(self.info)).json()

            leader = LeaderInfo(**res)
            self.leader_cache[leader.id] = leader

        return self.leader_cache[leader_id]

    def resolve_commander(self, commander_id):
        """
        CommanderのInfoを返す
        :param str commander_id: 取得したいCommanderのID
        """
        if commander_id not in self.commander_cache:
            return None
        return self.commander_cache[commander_id]


class RecruiterClient(object):
    def __init__(self, client: RestClient):
        self.client = client

        # リストに挙げられているメソッドをインスタンスメソッド化する
        # APIドキュメントとAPIヘルパーの実装をコード的に近くに実装するための措置
        method_list = [_get_commanders,
                       _get_commanders_spec,
                       _put_commanders_spec,
                       _get_department_squad_leader,
                       _get_department_troop_commander,
                       ]
        for method in method_list:
            setattr(self.__class__, method.__name__[1:], method)

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


def _get_commanders(self):
    st, res = self.client.get('commanders')
    if res is None:
        return None
    if st != 200:
        return (res['_status'], None)
    return (res['_status'], res['commanders'])


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


def _get_commanders_spec(self, com_id):
    st, res = self.client.get('commanders/' + com_id)
    if res is None:
        return None
    if st != 200:
        return (res['_status'], None)
    return (res['_status'], CommanderInfo(**res['commander']))


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

    com = None
    try:
        com = CommanderInfo(**request.json)
    except TypeError:
        return jsonify(_status=ResponseStatus.make_error(msgs[400]),
                       input=request.json)
    if com.id != com_id:
        return jsonify(_status=ResponseStatus.make_error(msgs[400]),
                       input=request.json)

    _recruiter.commander_cache[com_id] = com
    return jsonify(_status=ResponseStatus.Success, commander=asdict(com))


def _put_commanders_spec(self, com_id, obj):
    st, res = self.client.put('commanders/' + com_id, asdict(obj))
    if res is None:
        return None
    if st != 200:
        return (res['_status'], None)
    return (res['_status'], CommanderInfo(**res['commander']))


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


def _get_department_squad_leader(self, soldier_id):
    st, res = self.client.get('department/squad/leader?soldier_id='
                              + soldier_id)
    if res is None:
        return None
    if st != 200:
        return (res['_status'], None)
    return (res['_status'], LeaderInfo(**res['leader']))


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


def _get_department_troop_commander(self, leader_id):
    st, res = self.client.get('department/troop/commander?leader_id='
                              + leader_id)
    if res is None:
        return None
    if st != 200:
        return (res['_status'], None)
    return (res['_status'], CommanderInfo(**res['commander']))


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
    spec_dict = swagger(app, template={'definitions': definitions})
    spec_dict['info']['title'] = 'SensingTroops'
    return jsonify(spec_dict)


@app.route('/spec.html')
def spec_html():
    return render_template('swagger_ui.html',
                           spec_url=url_prefix + '/spec.json')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-P', '--port', type=int, default=50000, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/recruiter', help='url prefix')
    args = parser.parse_args()
    url_prefix = args.prefix

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        config_path = '{0}/recruit.yml'.format(os.path.dirname(__file__))
        initialize_app(config_path)

    server = Flask(__name__)
    server.debug = True
    server.register_blueprint(app, url_prefix=url_prefix)
    server.run(host='0.0.0.0', port=args.port)
