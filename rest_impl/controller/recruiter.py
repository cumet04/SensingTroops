from model import CommanderInfo
from model.recruiter import Recruiter
from utils.helpers import json_input, ResponseStatus
from flask import jsonify, request, Blueprint
from controller import logger


server = Blueprint('recruiter', __name__)
recruiter = None  # type:Recruiter


@server.route('/commanders', methods=['GET'])
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
    id_list = sorted(list(recruiter.TroopList.keys()))
    return jsonify(_status=ResponseStatus.Success, commanders=id_list)


@server.route('/commanders/<com_id>', methods=['GET'])
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
    if com_id not in recruiter.TroopList:
        return jsonify(_status=ResponseStatus.NotFound), 404

    info = recruiter.resolve_commander(com_id)
    if info is None:
        return jsonify(_status=ResponseStatus.Success, commander={})
    return jsonify(_status=ResponseStatus.Success, commander=info.to_dict())


@server.route('/commanders/<com_id>', methods=['PUT'])
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
        com = CommanderInfo.make(request.json)
    except TypeError:
        return jsonify(_status=ResponseStatus.make_error(msgs[400]),
                       input=request.json), 400
    if com.id != com_id:
        return jsonify(_status=ResponseStatus.make_error(msgs[400]),
                       input=request.json), 400

    accepted = recruiter.register_commander_info(com)
    if accepted is None:
        return jsonify(_status=ResponseStatus.NotFound), 404

    return jsonify(_status=ResponseStatus.Success, commander=accepted.to_dict())


@server.route('/commanders/<cid>', methods=['DELETE'])
def delete_commander_info(cid):
    """
    Remove a registered commander info
    ---
    parameters:
      - name: cid
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
      404:
        description: "[NT] Specified Commander ID is not found"
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    if recruiter.remove_commander_info(cid):
        return jsonify(_status=ResponseStatus.Success)
    else:
        return jsonify(_status=ResponseStatus.NotFound), 404


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
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            leader:
              $ref: '#/definitions/LeaderInfo'
            place:
              type: string
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

    leader_id = recruiter.get_squad_leader(soldier_id)
    if leader_id is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[404])), 404

    info = recruiter.resolve_leader(leader_id)
    if info is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[500])), 500

    return jsonify(_status=ResponseStatus.Success,
                   leader=info.to_dict(),
                   place=recruiter.get_soldier_ep(soldier_id))


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
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            commander:
              $ref: '#/definitions/CommanderInfo'
            place:
              type: string
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

    commander_id = recruiter.get_troop_commander(leader_id)
    if commander_id is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[404])), 404

    info = recruiter.resolve_commander(commander_id)
    if info is None:
        return jsonify(_status=ResponseStatus.make_error(msgs[500])), 500

    return jsonify(_status=ResponseStatus.Success,
                   commander=info.to_dict(),
                   place=recruiter.get_leader_ep(leader_id))


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
