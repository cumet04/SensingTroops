#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from functools import wraps
from flask_cors import cross_origin
from common import json_input, LeaderInfo, CommanderInfo, Report
from flask import Flask, jsonify, request
from flask_swagger import swagger
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


# REST interface ---------------------------------------------------------------

server = Flask(__name__)
url_prefix = '/commander'


@server.route(url_prefix + '/', methods=['GET'])
def get_info():
    """
    Get this commander's information
    ---
    tags:
      - info
    definitions:
      - schema:
          id: CommanderInfo
          properties:
            id:
              type: string
            name:
              type: string
            endpoint:
              type: string
            subordinates:
              type: list
              # TODO: リストを表記する方法が不明なので要調査
            campaigns:
              type: list
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
    show status UI
    ---
    tags:
      - UI
    parameters: []
    responses:
      200:
        description: Commander's status UI
    """
    # TODO: implementation
    # return render_template("captain_ui.html", com=app.generate_ui())
    return jsonify(msg='this function is not implemented.'), 500


@server.route(url_prefix + '/subordinates', methods=['GET', 'POST'])
@json_input
def subordinates():
    if request.method == 'GET':
        return jsonify(result='success', subordinates=app.subordinates)
    elif request.method == 'POST':
        res = app.accept_subordinate(LeaderInfo(**request.json))
        return jsonify(result='success', accepted=res)


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """

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
    res = app.get_sub_info(sub_id)
    return jsonify(info=res)


@server.route(url_prefix + '/subordinates/<sub_id>/report',
              methods=['GET', 'POST'])
@access_subordinate
@json_input
def access_report(sgt_id):
    if request.method == 'GET':
        return jsonify(result='success', reports=app.report_cache)
    elif request.method == 'POST':
        res = app.accept_report(Report(**request.json))
        return jsonify(result='success', accepted=res)
    app.accept_report(sgt_id, request.json)
    return jsonify(result='success')


@server.route(url_prefix + '/spec')
@cross_origin()
def spec():
    return jsonify(swagger(server))


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        self_port = int(sys.argv[1])
    else:
        self_port = 52000

    ep = 'http://localhost:{0}{1}'.format(self_port, url_prefix)
    app = Commander('com-http', ep)
    server.debug = True
    server.run(host='0.0.0.0', port=self_port,
               use_debugger=True, use_reloader=False)
