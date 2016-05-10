#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import argparse
from functools import wraps
from flask_cors import cross_origin
from objects import LeaderInfo, CommanderInfo, Report, Mission, Campaign
from utils import json_input
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
_app = Commander()


@server.route('/', methods=['GET'])
def get_info():
    """
    Information of this commander
    ---
    parameters: []
    responses:
      200:
        description: Commander's information
        schema:
          $ref: '#/definitions/CommanderInfo'
    """
    info = _app.generate_info()._asdict()
    return jsonify(result='success', info=info), 200


@server.route('/ui', methods=['GET'])
def show_status():
    """
    [NIY][NT] Status UI
    ---
    parameters: []
    responses:
      200:
        description: Commander's status UI
    """
    # TODO: implementation
    # return render_template("captain_ui.html", com=app.generate_ui())
    return jsonify(msg='this function is not implemented yet.'), 500


@server.route('/campaigns', methods=['GET'])
def get_campaigns():
    """
    [NT] Accepted campaigns
    ---
    parameters: []
    responses:
      200:
        description: A list of campaign that is accepted by the commander
        schema:
          properties:
            campaigns:
              type: array
              items:
                $ref: '#/definitions/Campaign'
    """
    return jsonify(campaigns=_app.campaigns), 200


@server.route('/campaigns', methods=['POST'])
def accept_campaigns():
    """
    [NT] Add new campaigns
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
            result:
              description: The result of process; 'success' or 'failed'
              type: string
            accepted:
              description: The accepted campaign
              $ref: '#/definitions/Campaign'
    """
    campaign = Campaign(**request.json)
    accepted = _app.accept_campaign(campaign)._asdict()
    if accepted is None:
        return jsonify(msg='accept_campaign failed.'), 500

    return jsonify(result='success', accepted=accepted), 200


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
            subordinates:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
    """
    subs_raw = _app.subordinates
    subs_dicts = [sub._asdict() for sub in subs_raw.values()]
    return jsonify(subordinates=subs_dicts)


@server.route('/subordinates', methods=['POST'])
@json_input
def accept_subordinate():
    """
    Add new leader
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
            accepted:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
    """
    leader = LeaderInfo(**request.json)
    accepted = _app.accept_subordinate(leader)._asdict()
    if accepted is None:
        return jsonify(msg='accept_subordinate failed.'), 500

    return jsonify(result='success', accepted=accepted), 200


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
    [NT] Information of a subordinate
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
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
    """
    res = _app.get_sub_info(sub_id)
    return jsonify(info=res)


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
            result:
              description: The result of process; 'success' or 'failed'
              type: string
            accepted:
              description: The accepted report
              $ref: '#/definitions/Report'
    """
    res = _app.accept_report(Report(**request.json))
    return jsonify(result='success', accepted=res)


@server.route('/subordinates/<sub_id>/missions', methods=['GET'])
@access_subordinate
def get_mission(sub_id):
    """
    [NT] Latest missions assigned to the subordinate
    ---
    parameters:
      - name: sub_id
        description: A leader-id
        in: path
        type: string
    responses:
      200:
        description: A list of mission
        schema:
          properties:
            missions:
              type: array
              items:
                $ref: '#/definitions/Mission'
        headers:
          ETag:
            type: string
    """
    return jsonify(missions=[Mission()])


def set_params(commander_id, commander_name, endpoint):
    _app.id = commander_id
    _app.name = commander_name
    _app.endpoint = endpoint
