#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import argparse
from functools import wraps
from flask_cors import cross_origin
from objects import LeaderInfo, CommanderInfo, Report,\
    Mission, Campaign, ResponseStatus
from utils import json_input, asdict
from flask import Flask, jsonify, request, render_template, Blueprint
from logging import getLogger, StreamHandler, DEBUG, FileHandler

logger = getLogger(__name__)
handler = FileHandler('/tmp/troops/commander.log')
# handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Commander(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.endpoint = ''
        self.subordinates = {}
        self.campaigns = []
        self.report_cache = []

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

server = Blueprint('commander', __name__)
_app = None


def initialize_app(commander_id, commander_name, endpoint):
    global _app
    _app = Commander()
    _app.id = commander_id
    _app.name = commander_name
    _app.endpoint = endpoint


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
    info = asdict(_app.generate_info())
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
    camps_raw = _app.campaigns
    camps_dicts = [asdict(camp) for camp in camps_raw]
    return jsonify(_status=ResponseStatus.Success, campaigns=camps_dicts), 200


@server.route('/campaigns', methods=['POST'])
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
    accepted = asdict(_app.accept_campaign(campaign))
    if accepted is None:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success, accepted=accepted), 200


@server.route('/subordinates', methods=['GET'])
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
    subs_raw = _app.subordinates
    subs_dicts = [asdict(sub) for sub in subs_raw.values()]
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
    """
    leader = LeaderInfo(**request.json)
    accepted = asdict(_app.accept_subordinate(leader))
    if accepted is None:
        return jsonify(_status=ResponseStatus.Failed), 500

    return jsonify(_status=ResponseStatus.Success, accepted=accepted), 200


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # leaderのものと全く同一
    @wraps(f)
    def check_subordinate(sub_id, *args, **kwargs):
        if not _app.check_subordinate(sub_id):
            return jsonify(result='failed',
                           msg='the man is not my subordinate'), 404
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
    """
    res = _app.get_sub_info(sub_id)
    return jsonify(_status=ResponseStatus.Success, info=asdict(res))


@server.route('/subordinates/<sub_id>/report', methods=['POST'])
@access_subordinate
@json_input
def accept_report(sub_id):
    """
    [NT] Accept new report
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
    """
    res = _app.accept_report(Report(**request.json))
    return jsonify(_status=ResponseStatus.Success, accepted=res)

