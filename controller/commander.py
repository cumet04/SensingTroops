from functools import wraps
from flask import jsonify, request, Blueprint, make_response
from model import LeaderInfo, Report, Campaign
from model.commander import Commander
from utils.helpers import json_input, ResponseStatus
from controller import logger


server = Blueprint('commander', __name__)
commander = None  # type: Commander


@server.route('/', methods=['GET'])
def get_info():
    """
    Information of this commander
    このCommanderの情報をjson形式で返す
    ---
    parameters: []
    responses:
      200:
        description: Commander's information
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            info:
              description: Commander's information
              $ref: '#/definitions/CommanderInfo'
    """
    info = commander.generate_info().to_dict()
    return jsonify(_status=ResponseStatus.Success, info=info), 200


@server.route('/ui', methods=['GET'])
def show_status():
    """
    [NIY][NT] Status UI
    このCommander及びTroopの各種情報をWebUIで表示する
    ---
    parameters: []
    responses:
      200:
        description: Commander's status UI
    """
    # TODO: implementation
    # return render_template("captain_ui.html", com=app.generate_ui())
    return jsonify(_status=ResponseStatus.NotImplemented), 500


@server.route('/campaigns', methods=['GET'])
def get_campaigns():
    """
    Accepted campaigns
    このCommanderが受理したCampaignsの一覧を返す
    ---
    parameters: []
    responses:
      200:
        description: A list of campaign that is accepted by the commander
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            campaigns:
              type: array
              items:
                $ref: '#/definitions/Campaign'
    """
    camps_raw = commander.campaigns
    camps_dicts = [camp.to_dict() for camp in camps_raw.values()]
    return jsonify(_status=ResponseStatus.Success, campaigns=camps_dicts), 200


@server.route('/campaigns', methods=['POST'])
@json_input
def accept_campaigns():
    """
    Add a new campaigns
    このCommanderに新しいCampaignを一つだけ追加する
    ---
    parameters:
      - name: campaign
        description: A campaign to be accepted
        in: body
        required: true
        schema:
          $ref: '#/definitions/Campaign'
    responses:
      200:
        description: The campaign is accepted
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            accepted:
              description: The accepted campaign
              $ref: '#/definitions/Campaign'
    """
    campaign = Campaign.make(request.json)
    accepted = commander.accept_campaign(campaign).to_dict()
    if accepted is None:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success, accepted=accepted), 200


@server.route('/subordinates', methods=['GET'])
def get_subordinates():
    """
    All subordinates of this commander
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
                $ref: '#/definitions/LeaderInfo'
    """
    subs_raw = commander.subordinates
    subs_dicts = [sub.to_dict() for sub in subs_raw.values()]
    return jsonify(_status=ResponseStatus.Success, subordinates=subs_dicts)


@server.route('/subordinates', methods=['POST'])
@json_input
def accept_subordinate():
    """
    Add a new leader
    ---
    parameters:
      - name: subordinate
        description: Information of a leader who is to join
        in: body
        required: true
        schema:
          $ref: '#/definitions/LeaderInfo'
    responses:
      200:
        description: The leader is accepted
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            accepted:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
      400:
        description: "[NT] Requested leader already exists in the troop"
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    msgs = {
        400: "Requested leader already exists in the troop",
    }

    leader = LeaderInfo.make(request.json)
    if commander.check_subordinate(leader.id):
        return jsonify(_status=ResponseStatus.make_error(msgs[400])), 400

    if not commander.accept_subordinate(leader):
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success,
                   accepted=leader.to_dict()), 200


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # leaderのものと全く同一
    @wraps(f)
    def check_subordinate(sub_id, *args, **kwargs):
        if not commander.check_subordinate(sub_id):
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
              $ref: '#/definitions/LeaderInfo'
      404:
        description: The subordinate is not found
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    info = commander.get_sub_info(sub_id)
    etag = info.hash()
    if_none_match = str(request.if_none_match)[1:-1]  # ダブルクォートを削除
    if etag == if_none_match:
        return make_response(), 304

    response = jsonify(_status=ResponseStatus.Success, info=info.to_dict())
    response.set_etag(etag)
    return response


@server.route('/subordinates/<sub_id>/report', methods=['POST'])
@access_subordinate
@json_input
def accept_report(sub_id):
    """
    Accept new report
    ---
    parameters:
      - name: sub_id
        description: The report's author-id
        in: path
        type: string
      - name: report
        description: A report to be accepted
        in: body
        required: true
        schema:
          $ref: '#/definitions/Report'
    responses:
      200:
        description: The report is accepted
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
            accepted:
              description: The accepted report
              $ref: '#/definitions/Report'
      404:
        description: The subordinate is not found
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    report = Report.make(request.json)
    commander.accept_report(sub_id, report)
    return jsonify(_status=ResponseStatus.Success, accepted=report.to_dict())
