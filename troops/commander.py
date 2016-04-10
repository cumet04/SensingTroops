#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import argparse
from functools import wraps
from flask_cors import cross_origin
from objects import LeaderInfo, CommanderInfo, Report, Mission
from utils import json_input, gen_spec
from flask import Flask, jsonify, request
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Commander(object):
    def __init__(self, name, endpoint):
        self.id = ''  # テスト時はコマンドライン引数あたりから別途IDを割り当てる
        self.name = name
        self.endpoint = endpoint
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

    def accept_subordinate(self, sub_info):
        """
        部下の入隊を受け入れる
        :param LeaderInfo sub_info: 受け入れるLeaderの情報
        :return bool:
        """
        if self.check_subordinate(sub_info.id):
            return False
        self.subordinates[sub_info.id] = sub_info
        return True

    def accept_report(self, sub_id, report):
        if self.check_subordinate(sub_id):
            return False
        self.report_cache.append(report)
        return True


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

server = Flask(__name__)
url_prefix = '/commander'


@server.route(url_prefix + '/', methods=['GET'])
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
    info = app.generate_info()._asdict()
    return jsonify(result='success', info=info), 200


@server.route(url_prefix + '/ui', methods=['GET'])
def show_status():
    """
    Status UI
    ---
    parameters: []
    responses:
      200:
        description: Commander's status UI
    """
    # TODO: implementation
    # return render_template("captain_ui.html", com=app.generate_ui())
    return jsonify(msg='this function is not implemented.'), 500


@server.route(url_prefix + '/campaigns', methods=['GET'])
def get_campaigns():
    """
    Accepted campaigns
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
    pass


@server.route(url_prefix + '/campaigns', methods=['POST'])
def accept_campaigns():
    """
    Add new campaigns
    ---
    parameters:
      - name: campaign
        description: A campaign to be accepted
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
    pass


@server.route(url_prefix + '/subordinates', methods=['GET'])
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
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
    """
    return jsonify(result='success', subordinates=app.subordinates)


@server.route(url_prefix + '/subordinates', methods=['POST'])
@json_input
def accept_subordinate():
    """
    aaaa
    ---
    parameters:
      - name: sub_id
        type: string
        description: The report's author-id
    responses:
      200:
        description: The subordinate is found
        schema:
          properties:
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
    """
    res = app.accept_subordinate(LeaderInfo(**request.json))
    return jsonify(result='success', accepted=res)


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # leaderのものと全く同一
    @wraps(f)
    def check_subordinate(sub_id, *args, **kwargs):
        if not app.check_subordinate(sub_id):
            return jsonify(result='failed',
                           msg='the man is not my subordinate'), 404
        return f(sub_id, *args, **kwargs)

    return check_subordinate


@server.route(url_prefix + '/subordinates/<sub_id>', methods=['GET'])
@access_subordinate
def get_sub_info(sub_id):
    """
    Information of a subordinate
    ---
    parameters:
      - name: sub_id
        type: string
        description: ID of a requested subordinate
    responses:
      200:
        description: The subordinate is found
        schema:
          properties:
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/LeaderInfo'
    """
    res = app.get_sub_info(sub_id)
    return jsonify(info=res)


@server.route(url_prefix + '/subordinates/<sub_id>/report', methods=['POST'])
@access_subordinate
@json_input
def accept_report(sub_id):
    """
    Accept new report
    ---
    parameters:
      - name: sub_id
        type: string
        description: The report's author-id
      - name: report
        description: A report to be accepted
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
    res = app.accept_report(Report(**request.json))
    return jsonify(result='success', accepted=res)


@server.route(url_prefix + '/subordinates/<sub_id>/missions', methods=['GET'])
@access_subordinate
def get_mission(sub_id):
    """
    Latest missions assigned to the subordinate
    ---
    parameters:
      - name: sub_id
        type: string
        description: A leader-id
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


@server.route(url_prefix + '/spec')
@cross_origin()
def spec():
    return jsonify(gen_spec(app.__class__.__name__, server))


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--port', default=52000,
                        help='port')
    parser.add_argument('-S', '--swagger-spec', action='store_true',
                        default=False, help='output swagger-spec json')
    args = parser.parse_args()

    ep = 'http://localhost:{0}{1}'.format(args.port, url_prefix)
    app = Commander('com-http', ep)

    # output swagger-spec
    if args.swagger_spec:
        print(json.dumps(gen_spec(app.__class__.__name__, server)))
        exit()

    server.debug = True
    server.run(host='0.0.0.0', port=args.port,
               use_debugger=True, use_reloader=False)
