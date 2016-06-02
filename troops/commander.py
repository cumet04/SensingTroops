#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
from functools import wraps
from flask import Flask, jsonify, request, render_template, Blueprint
from flask_cors import cross_origin
from flask_swagger import swagger
from utils.objects import LeaderInfo, CommanderInfo, Report,\
    Campaign, ResponseStatus, definitions
from utils.recruiter_client import RecruiterClient
from utils.helpers import json_input, asdict
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Commander(object):
    def __init__(self, com_id, name, endpoint):
        self.id = com_id
        self.name = name
        self.endpoint = endpoint
        self.subordinates = {}
        self.campaigns = []
        self.report_cache = []

    def awake(self, recruiter_client):
        info = self.generate_info()
        res, err = recruiter_client.put_commanders_spec(self.id, info)
        if err is not None:
            logger.error("in Commander awake")
            logger.error("[PUT]recruiter/commanders/id failed: {0}".format(err))
            return False
        logger.info("register commander to recruiter: success")
        return True

    def generate_info(self):
        """
        自身のパラメータ群からCommanderInfoオブジェクトを生成する
        :return CommanderInfo: 生成したCommanderInfo
        """
        return CommanderInfo(
            id=self.id,
            name=self.name,
            endpoint=self.endpoint,
            subordinates=list(self.subordinates.keys()),
            campaigns=self.campaigns)

    def generate_ui(self):
        # TODO: implementation
        pass

    def check_subordinate(self, sub_id):
        """
        指定された兵隊が部下に存在するかを確認する
        :param str sub_id: 確認したい部下のID
        :return bool: 存在すればTrue
        """
        return sub_id in self.subordinates

    def get_sub_info(self, sub_id):
        return self.subordinates[sub_id]

    def accept_campaign(self, campaign):
        self.campaigns.append(campaign)
        return campaign

    def accept_subordinate(self, sub_info):
        """
        部下の入隊を受け入れる
        :param LeaderInfo sub_info: 受け入れるLeaderの情報
        :return bool:
        """
        if self.check_subordinate(sub_info.id):
            return None
        self.subordinates[sub_info.id] = sub_info
        return sub_info

    def accept_report(self, sub_id, report):
        if self.check_subordinate(sub_id):
            return False
        self.report_cache.append(report)
        return True


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

server = None  # type: Flask
app = Blueprint('commander', __name__)
_commander = None  # type: Commander
url_prefix = '/commander'


def initialize_app(commander_id, commander_name, endpoint):
    global _commander
    _commander = Commander(commander_id, commander_name, endpoint)


@app.route('/', methods=['GET'])
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
    info = asdict(_commander.generate_info())
    return jsonify(_status=ResponseStatus.Success, info=info), 200


@app.route('/ui', methods=['GET'])
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


@app.route('/campaigns', methods=['GET'])
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
    camps_raw = _commander.campaigns
    camps_dicts = [asdict(camp) for camp in camps_raw]
    return jsonify(_status=ResponseStatus.Success, campaigns=camps_dicts), 200


@app.route('/campaigns', methods=['POST'])
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
    campaign = Campaign(**request.json)
    accepted = asdict(_commander.accept_campaign(campaign))
    if accepted is None:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success, accepted=accepted), 200


@app.route('/subordinates', methods=['GET'])
@json_input
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
    subs_raw = _commander.subordinates
    subs_dicts = [asdict(sub) for sub in subs_raw.values()]
    return jsonify(_status=ResponseStatus.Success, subordinates=subs_dicts)


@app.route('/subordinates', methods=['POST'])
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

    leader = LeaderInfo(**request.json)
    if _commander.check_subordinate(leader.id):
        return jsonify(_status=ResponseStatus.make_error(msgs[400])), 400

    if not _commander.accept_subordinate(leader):
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success,
                   accepted=asdict(leader)), 200


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # leaderのものと全く同一
    @wraps(f)
    def check_subordinate(sub_id, *args, **kwargs):
        if not _commander.check_subordinate(sub_id):
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
              $ref: '#/definitions/LeaderInfo'
      404:
        description: The subordinate is not found
        schema:
          properties:
            _status:
              description: Response status
              $ref: '#/definitions/ResponseStatus'
    """
    res = _commander.get_sub_info(sub_id)
    return jsonify(_status=ResponseStatus.Success, info=asdict(res))


@app.route('/subordinates/<sub_id>/report', methods=['POST'])
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
    # TODO: report.valuesは少なくともstringではないと思う
    report = Report(**request.json)
    _commander.accept_report(sub_id, report)
    return jsonify(_status=ResponseStatus.Success, accepted=asdict(report))


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
        '-P', '--port', type=int, default=50001, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/commander', help='url prefix')
    params = parser.parse_args()
    url_prefix = params.prefix

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # flaskのuse_reloader=Trueのときの二重起動対策
        ep = 'http://localhost:{0}{1}/'.format(params.port, url_prefix)
        initialize_app(params.id, params.name, ep)
        _commander.awake(RecruiterClient.gen_rest_client(
            'http://localhost:50000/recruiter/'))

    server = Flask(__name__)
    server.debug = True
    server.register_blueprint(app, url_prefix=url_prefix)
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
