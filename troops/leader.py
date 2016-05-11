#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import argparse
from functools import wraps
from flask_cors import cross_origin
from objects import LeaderInfo, SoldierInfo, Work, Order
from utils import json_input, asdict
from flask import Flask, jsonify, request, render_template, Blueprint
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Leader(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.endpoint = ''
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


# ------------------------------------------------------------------------------
# REST interface ---------------------------------------------------------------
# ------------------------------------------------------------------------------

server = Blueprint('leader', __name__)
_app = Leader()


@server.route('/', methods=['GET'])
def get_info():
    """
    Information of this leader
    ---
    parameters: []
    responses:
      200:
        description: Leader's information
        schema:
          $ref: '#/definitions/LeaderInfo'
    """
    info = asdict(_app.generate_info())
    return jsonify(result='success', info=info), 200


@server.route('/missions', methods=['GET'])
def get_missions():
    """
    [NIY] Accepted missions
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
    return jsonify(msg='this function is not implemented yet.'), 500


@server.route('/missions', methods=['POST'])
def accept_missions():
    """
    [NIY] Add new missions
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
            result:
              description: The result of process; 'success' or 'failed'
              type: string
            accepted:
              description: The accepted mission
              $ref: '#/definitions/Mission'
    """
    return jsonify(msg='this function is not implemented yet.'), 500


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
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/SoldierInfo'
    """
    return jsonify(result='success', subordinates=_app.subordinates)


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
            accepted:
              description: Information object of the subordinate
              $ref: '#/definitions/SoldierInfo'
    """
    res = _app.accept_subordinate(SoldierInfo(**request.json))
    return jsonify(result='success', accepted=res)


def access_subordinate(f):
    """
    個別の部下にアクセスするための存在チェック用デコレータ
    """
    # TODO: utilsに吸収
    # commanderのものと全く同一
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
            info:
              description: Information object of the subordinate
              $ref: '#/definitions/SoldierInfo'
    """
    res = _app.get_sub_info(sub_id)
    return jsonify(info=res)


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
            result:
              description: The result of process; 'success' or 'failed'
              type: string
            accepted:
              description: The accepted work
              $ref: '#/definitions/Work'
    """
    res = _app.accept_work(Work(**request.json))
    return jsonify(result='success', accepted=res)


@server.route('/subordinates/<sub_id>/orders', methods=['GET'])
@access_subordinate
def get_order(sub_id):
    """
    Latest orders assigned to the subordinate
    ---
    parameters:
      - name: sub_id
        description: A soldier-id
        in: path
        type: string
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


def set_params(leader_id, leader_name, endpoint):
    _app.id = leader_id
    _app.name = leader_name
    _app.endpoint = endpoint
