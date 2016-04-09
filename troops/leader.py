#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import argparse
from functools import wraps
from flask_cors import cross_origin
from objects import definitions, LeaderInfo, SoldierInfo, Work, Order
from utils import json_input
from flask import Flask, jsonify, request
from flask_swagger import swagger
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Leader(object):
    def __init__(self, name, endpoint):
        self.id = ''  # テスト時はコマンドライン引数あたりから別途IDを割り当てる
        self.name = name
        self.endpoint = endpoint
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

    def get_sub_info(self, sub_id):
        return self.subordinates[sub_id]

    def accept_subordinate(self, sub_info):
        """
        部下の入隊を受け入れる
        :param SoldierInfo sub_info: 受け入れるLeaderの情報
        :return bool:
        """
        if self.check_subordinate(sub_info.id):
            return False
        self.subordinates[sub_info.id] = sub_info
        return True

    def accept_work(self, sub_id, work):
        if self.check_subordinate(sub_id):
            return False
        self.work_cache.append(work)
        return True


# REST interface ---------------------------------------------------------------

server = Flask(__name__)
url_prefix = '/leader'


@server.route(url_prefix + '/', methods=['GET'])
def get_info():
    """
    Get this leader's information
    ---
    parameters: []
    responses:
      200:
        description: Leader's information
        schema:
          $ref: '#/definitions/LeaderInfo'
    """
    info = app.generate_info()._asdict()
    return jsonify(result='success', info=info), 200


@server.route(url_prefix + '/missions', methods=['GET'])
def get_missions():
    """
    Get accepted missions
    ---
    parameters: []
    responses:
      200:
        description: A list of missions that is accepted by the leader
        schema:
          properties:
            missions:
              type: array
              items:
                $ref: '#/definitions/Mission'
    """
    pass


@server.route(url_prefix + '/missions', methods=['POST'])
def accept_missions():
    """
    Add new missions
    ---
    parameters:
      - name: mission
        description: A mission to be accepted
        schema:
          $ref: '#/definitions/Mission'
    responses:
      200:
        description: The mission is accepted
        schema:
          properties:
            result:
              description: The result of process; 'success' or 'failed'
              type: string
            accepted:
              description: The accepted mission
              $ref: '#/definitions/Mission'
    """
    pass


@server.route(url_prefix + '/subordinates', methods=['GET'])
@json_input
def get_subordinates():
    """
    Get all subordinates of this leader
    ---
    parameters: []
    responses:
      200:
        description: The subordinate is found
        schema:
          properties:
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/SoldierInfo'
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
    res = app.accept_subordinate(SoldierInfo(**request.json))
    return jsonify(result='success', accepted=res)


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # commanderのものと全く同一
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
    Get information of a subordinate
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
              $ref: '#/definitions/SoldierInfo'
    """
    res = app.get_sub_info(sub_id)
    return jsonify(info=res)


@server.route(url_prefix + '/subordinates/<sub_id>/work', methods=['POST'])
@access_subordinate
@json_input
def accept_work(sub_id):
    """
    Accept new work
    ---
    parameters:
      - name: sub_id
        type: string
        description: The work's author-id
      - name: work
        description: A work to be accepted
        schema:
          $ref: '#/definitions/Work'
    responses:
      200:
        description: The work is accepted
        schema:
          properties:
            result:
              description: The result of process; 'success' or 'failed'
              type: string
            accepted:
              description: The accepted work
              $ref: '#/definitions/Work'
    """
    res = app.accept_work(Work(**request.json))
    return jsonify(result='success', accepted=res)


@server.route(url_prefix + '/subordinates/<sub_id>/order', methods=['GET'])
@access_subordinate
def get_order(sub_id):
    """
    Get the subordinate's latest order
    ---
    parameters:
      - name: sub_id
        type: string
        description: A soldier-id
    responses:
      200:
        description: A list of order
        schema:
          properties:
            orders:
              type: array
              items:
                $ref: '#/definitions/Order'
        headers:
          ETag:
            type: string
    """
    return jsonify(missions=[Order()])


@server.route(url_prefix + '/spec')
@cross_origin()
def spec():
    return jsonify(gen_spec(app))


def gen_spec(app_obj):
    # swagger-specのdictを生成する関数
    # 全アクタで共通になるようにコーディングしているが
    # server変数やdefinitions変数にアクセスする必要があるため
    # utils.pyには含んでいない
    spec_dict = swagger(server, template={'definitions': definitions})
    class_name = app_obj.__class__.__name__
    spec_dict['info']['title'] = 'SensingTroops - ' + class_name
    return spec_dict


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--port', default=51000,
                        help='port')
    parser.add_argument('-S', '--swagger-spec', action='store_true',
                        default=False, help='output swagger-spec json')
    args = parser.parse_args()

    ep = 'http://localhost:{0}{1}'.format(args.port, url_prefix)
    app = Leader('lea-http', ep)

    # output swagger-spec
    if args.swagger_spec:
        print(json.dumps(gen_spec(app)))
        exit()

    server.debug = True
    server.run(host='0.0.0.0', port=args.port,
               use_debugger=True, use_reloader=False)
