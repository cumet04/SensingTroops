from functools import wraps
from utils.objects import LeaderInfo, SoldierInfo, Work, Mission, \
    ResponseStatus,definitions
from utils.helpers import json_input, asdict
from flask import jsonify, request, Blueprint, render_template
from flask_cors import cross_origin
from flask_swagger import swagger
from logging import getLogger, StreamHandler, DEBUG
from model import Leader


logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


server = Blueprint('leader', __name__)
leader = None  # type: Leader


def initialize_app(leader_id, leader_name, endpoint):
    global leader
    leader = Leader()
    leader.id = leader_id
    leader.name = leader_name
    leader.endpoint = endpoint


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
    info = asdict(leader.generate_info())
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
    missions_raw = leader.missions
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
    accepted = asdict(leader.accept_mission(mission))
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
    subs_raw = leader.subordinates
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
    if not leader.accept_subordinate(soldier):
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
        if not leader.check_subordinate(sub_id):
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
    res = leader.get_sub_info(sub_id)
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
    work = Work(**request.json)
    leader.accept_work(sub_id, work)
    return jsonify(_status=ResponseStatus.Success, accepted=asdict(work))

