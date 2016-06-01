#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
from typing import List
from functools import wraps
from objects import LeaderInfo, SoldierInfo, Work, Mission, ResponseStatus,\
    definitions
from utils import json_input, asdict, RestClient
from flask import Flask, jsonify, request, Blueprint, render_template
from flask_cors import cross_origin
from flask_swagger import swagger
from recruiter import RecruiterClient
from commander import CommanderClient
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Leader(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.endpoint = ''
        self.subordinates = {}
        self.missions = []
        self.work_cache = []

    def awake(self, rec_client):
        # 上官を解決する
        superior, err = rec_client.get_department_troop_commander(self.id)
        if superior is None and err is None:
            return False
        if err is not None:
            logger.error("in Leader awake")
            logger.error("[GET]recruiter/department/troop/commander" +
                         " failed: {0}".format(err))
            return False
        logger.info("superior was resolved: id={0}".format(superior.id))

        # 部隊に加入する
        com_client = CommanderClient.gen_rest_client(superior.endpoint)
        res, err = com_client.post_subordinates(self.generate_info())
        if res is None and err is None:
            return False
        if err is not None:
            logger.error("in Leader awake")
            logger.error("[POST]commander/subordinates failed: {0}".format(err))
            return False
        logger.info("joined to troop")

        # missionを取得する
        # TODO: job assignが実装され次第

    def generate_info(self) -> LeaderInfo:
        """
        自身のパラメータ群からLeaderInfoオブジェクトを生成する
        :return LeaderInfo: 生成したLeaderInfo
        """
        return LeaderInfo(
            id=self.id,
            name=self.name,
            endpoint=self.endpoint,
            subordinates=list(self.subordinates.keys()),
            missions=self.missions)

    def check_subordinate(self, sub_id):
        """
        指定された兵隊が部下に存在するかを確認する
        :param str sub_id: 確認したい部下のID
        :return bool: 存在すればTrue
        """
        return sub_id in self.subordinates

    def accept_mission(self, mission):
        self.missions.append(mission)
        return mission

    def get_sub_info(self, sub_id):
        return self.subordinates[sub_id]

    def accept_subordinate(self, sub_info):
        """
        部下の入隊を受け入れる
        :param SoldierInfo sub_info: 受け入れるLeaderの情報
        :return bool:
        """
        logger.debug('In accept_subordinate:')
        logger.debug('> sub_info:{0}'.format(sub_info))
        if self.check_subordinate(sub_info.id):
            return False
        self.subordinates[sub_info.id] = sub_info
        return True

    def accept_work(self, sub_id, work):
        if self.check_subordinate(sub_id):
            return False
        self.work_cache.append(work)
        return True


class LeaderClient(object):
    def __init__(self, client: RestClient):
        self.client = client

    # それぞれの実体メソッドを呼び出す
    # APIドキュメントとAPIヘルパーの実装をコード的に近くに実装するための措置
    def get_root(self) -> (LeaderInfo, str):
        try:
            return _get_root(self.client)
        except Exception as e:
            logger.error("in LeaderClient.get_root")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_missions(self) -> (List[Mission], str):
        try:
            return _get_missions(self.client)
        except Exception as e:
            logger.error("in LeaderClient.get_missions")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_missions(self, obj: Mission) -> (Mission, str):
        try:
            return _post_missions(self.client, obj)
        except Exception as e:
            logger.error("in LeaderClient.post_missions")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_subordinates(self) -> (List[SoldierInfo], str):
        try:
            return _get_subordinates(self.client)
        except Exception as e:
            logger.error("in LeaderClient.get_subordinates")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_subordinates(self, obj: SoldierInfo) -> (SoldierInfo, str):
        try:
            return _post_subordinates(self.client, obj)
        except Exception as e:
            logger.error("in LeaderClient.post_subordinates")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_subordinates_spec(self, sub_id: str) -> (SoldierInfo, str):
        try:
            return _get_subordinates_spec(self.client, sub_id)
        except Exception as e:
            logger.error("in LeaderClient.get_subordinates_spec")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_work(self, sub_id: str, obj: Work) -> (Work, str):
        try:
            return _post_work(self.client, sub_id, obj)
        except Exception as e:
            logger.error("in LeaderClient.post_work")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

server = None  # type: Flask
app = Blueprint('leader', __name__)
_leader = None  # type: Leader
url_prefix = '/leader'


def initialize_app(leader_id, leader_name, endpoint):
    global _leader
    _leader = Leader()
    _leader.id = leader_id
    _leader.name = leader_name
    _leader.endpoint = endpoint


@app.route('/', methods=['GET'])
def get_info():
    """
    Information of this leader
    このLeaderの情報をjson形式で返す
    ---
    parameters: []
    responses:
      200:
        description: Leader's information
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            info:
              description: Leader's information
              $ref: '#/definitions/LeaderInfo'
    """
    info = asdict(_leader.generate_info())
    return jsonify(_status=ResponseStatus.Success, info=info), 200


def _get_root(c):
    st, res = c.get('')
    if st != 200:
        return None, res['status']['msg']
    return LeaderInfo(**res['info']), None


@app.route('/missions', methods=['GET'])
def get_missions():
    """
    Accepted missions
    ---
    parameters: []
    responses:
      200:
        description: A list of missions that is accepted by the leader
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            missions:
              type: array
              items:
                $ref: '#/definitions/Mission'
    """
    missions_raw = _leader.missions
    missions_dicts = [asdict(m) for m in missions_raw]
    return jsonify(_status=ResponseStatus.Success,
                   missions=missions_dicts), 200


def _get_missions(c):
    st, res = c.get('missions')
    if st != 200:
        return None, res['status']['msg']
    return [Mission(**m) for m in res['missions']], None


@app.route('/missions', methods=['POST'])
def accept_missions():
    """
    Add new missions
    ---
    parameters:
      - name: mission
        description: A mission to be accepted
        in: body
        required: true
        schema:
          $ref: '#/definitions/Mission'
    responses:
      200:
        description: The mission is accepted
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            accepted:
              description: The accepted mission
              $ref: '#/definitions/Mission'
    """
    mission = Mission(**request.json)
    accepted = asdict(_leader.accept_mission(mission))
    if accepted is None:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success, accepted=accepted), 200


def _post_missions(c, obj):
    st, res = c.post('missions', asdict(obj))
    if st != 200:
        return None, res['status']['msg']
    return Mission(**res['accepted']), None


@app.route('/subordinates', methods=['GET'])
@json_input
def get_subordinates():
    """
    All subordinates of this leader
    ---
    parameters: []
    responses:
      200:
        description: The subordinate is found
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            subordinates:
              description: Information object of the subordinate
              type: array
              items:
                $ref: '#/definitions/SoldierInfo'
    """
    subs_raw = _leader.subordinates
    subs_dicts = [asdict(sub) for sub in subs_raw.values()]
    return jsonify(_status=ResponseStatus.Success, subordinates=subs_dicts)


def _get_subordinates(c):
    st, res = c.get('subordinates')
    if st != 200:
        return None, res['status']['msg']
    return [SoldierInfo(**sol) for sol in res['subordinates']], None


@app.route('/subordinates', methods=['POST'])
@json_input
def accept_subordinate():
    """
    Add new soldier
    ---
    parameters:
      - name: subordinate
        description: Information of a soldier who is to join
        in: body
        required: true
        schema:
          $ref: '#/definitions/SoldierInfo'
    responses:
      200:
        description: The soldier is accepted
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            accepted:
              description: Information object of the subordinate
              $ref: '#/definitions/SoldierInfo'
    """
    soldier = SoldierInfo(**request.json)
    if not _leader.accept_subordinate(soldier):
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success,
                   accepted=asdict(soldier)), 200


def _post_subordinates(c, obj):
    st, res = c.post('subordinates', asdict(obj))
    if st != 200:
        return None, res['status']['msg']
    return SoldierInfo(**res['accepted']), None


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # TODO: utilsに吸収
    # commanderのものと全く同一
    @wraps(f)
    def check_subordinate(sub_id, *args, **kwargs):
        if not _leader.check_subordinate(sub_id):
            return jsonify(_status=ResponseStatus.make_error(
                "The subordinate is not found"
            )), 404
        return f(sub_id, *args, **kwargs)

    return check_subordinate


@app.route('/subordinates/<sub_id>', methods=['GET'])
@access_subordinate
def get_sub_info(sub_id):
    """
    Information of a subordinate
    ---
    parameters:
      - name: sub_id
        description: ID of a requested subordinate
        in: path
        type: string
    responses:
      200:
        description: The subordinate is found
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/SoldierInfo'
    """
    res = _leader.get_sub_info(sub_id)
    return jsonify(_status=ResponseStatus.Success, info=asdict(res))


def _get_subordinates_spec(c, sub_id):
    st, res = c.get('subordinates/' + sub_id)
    if st != 200:
        return None, res['status']['msg']
    return SoldierInfo(**res['info']), None


@app.route('/subordinates/<sub_id>/work', methods=['POST'])
@access_subordinate
@json_input
def accept_work(sub_id):
    """
    Accept new work
    ---
    parameters:
      - name: sub_id
        description: The work's author-id
        in: path
        type: string
      - name: work
        description: A work to be accepted
        in: body
        required: true
        schema:
          $ref: '#/definitions/Work'
    responses:
      200:
        description: The work is accepted
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            accepted:
              description: The accepted work
              $ref: '#/definitions/Work'
    """
    work = Work(**request.json)
    _leader.accept_work(sub_id, work)
    return jsonify(_status=ResponseStatus.Success, accepted=asdict(work))


def _post_work(c, sub_id, obj):
    st, res = c.post('subordinates/' + sub_id, obj)
    if st != 200:
        return None, res['status']['msg']
    return Work(**res['accepted']), None


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    parser.add_argument(
        '-P', '--port', type=int, default=50002, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/leader', help='url prefix')
    params = parser.parse_args()
    url_prefix = params.prefix

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        ep = 'http://localhost:{0}{1}/'.format(params.port, url_prefix)
        initialize_app(params.id, params.name, ep)
        _leader.awake(RecruiterClient.gen_rest_client(
            'http://localhost:50000/recruiter/'))

    server = Flask(__name__)
    server.debug = True
    server.register_blueprint(app, url_prefix=url_prefix)
    server.run(host='0.0.0.0', port=params.port)
