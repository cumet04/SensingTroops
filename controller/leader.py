from functools import wraps
from model import SoldierInfo, Work
from model.leader import Leader
from utils.helpers import json_input, ResponseStatus
from flask import jsonify, request, Blueprint, make_response
from controller import logger


server = Blueprint('leader', __name__)
leader = None  # type: Leader


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
    info = leader.generate_info().to_dict()
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
    missions_dicts = [m.to_dict() for m in missions_raw.values()]
    return jsonify(_status=ResponseStatus.Success,
                   missions=missions_dicts), 200


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
    subs_dicts = [sub.to_dict() for sub in subs_raw.values()]
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
    soldier = SoldierInfo.make(request.json)
    if not leader.accept_subordinate(soldier):
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success,
                   accepted=soldier.to_dict()), 200


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
    info = leader.get_sub_info(sub_id)
    etag = info.hash()
    if_none_match = str(request.if_none_match)[1:-1]  # ダブルクォートを削除
    if etag == if_none_match:
        return make_response(), 304

    response = jsonify(_status=ResponseStatus.Success, info=info.to_dict())
    response.set_etag(etag)
    return response


@server.route('/subordinates/<sid>', methods=['DELETE'])
def delete_commander_info(sid):
    """
    Remove a registered subordinate info
    ---
    parameters:
      - name: sid
        description: ID of a requested soldier
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
      404:
        description: "[NT] Specified Soldier ID is not found"
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    if leader.remove_subordinate(sid):
        return jsonify(_status=ResponseStatus.Success)
    else:
        return jsonify(_status=ResponseStatus.NotFound), 404


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
    work = Work.make(request.json)
    leader.accept_work(sub_id, work)
    return jsonify(_status=ResponseStatus.Success, accepted=work.to_dict())
