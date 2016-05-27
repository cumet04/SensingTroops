#!/usr/bin/python3
# -*- coding: utf-8 -*-

from functools import wraps
from objects import LeaderInfo, SoldierInfo, Work, Mission, ResponseStatus
from utils import json_input, asdict
from flask import jsonify, request, Blueprint
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

    def generate_info(self):
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


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

server = Blueprint('leader', __name__)
_app = None  # type: Leader


def initialize_app(leader_id, leader_name, endpoint):
    global _app
    _app = Leader()
    _app.id = leader_id
    _app.name = leader_name
    _app.endpoint = endpoint


@server.route('/', methods=['GET'])
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
    info = asdict(_app.generate_info())
    return jsonify(_status=ResponseStatus.Success, info=info), 200


@server.route('/missions', methods=['GET'])
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
    missions_raw = _app.missions
    missions_dicts = [asdict(m) for m in missions_raw]
    return jsonify(_status=ResponseStatus.Success,
                   missions=missions_dicts), 200


@server.route('/missions', methods=['POST'])
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
    accepted = asdict(_app.accept_mission(mission))
    if accepted is None:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success, accepted=accepted), 200


@server.route('/subordinates', methods=['GET'])
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
    subs_raw = _app.subordinates
    subs_dicts = [asdict(sub) for sub in subs_raw.values()]
    return jsonify(_status=ResponseStatus.Success, subordinates=subs_dicts)


@server.route('/subordinates', methods=['POST'])
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
    if _app.accept_subordinate(soldier) == False:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success,
                   accepted=asdict(soldier)), 200


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # TODO: utilsに吸収
    # commanderのものと全く同一
    @wraps(f)
    def check_subordinate(sub_id, *args, **kwargs):
        if not _app.check_subordinate(sub_id):
            return jsonify(_status=ResponseStatus.make_error(
                "The subordinate is not found"
            )), 404
        return f(sub_id, *args, **kwargs)

    return check_subordinate


@server.route('/subordinates/<sub_id>', methods=['GET'])
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
    res = _app.get_sub_info(sub_id)
    return jsonify(_status=ResponseStatus.Success, info=asdict(res))


@server.route('/subordinates/<sub_id>/work', methods=['POST'])
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
    input = Work(**request.json)
    _app.accept_work(sub_id, input)
    return jsonify(_status=ResponseStatus.Success, accepted=asdict(input))
