#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../troops')

import unittest
import recruiter
import json
from flask import Flask
from logging import getLogger, StreamHandler, FileHandler, DEBUG
from objects import LeaderInfo, CommanderInfo, Report, Mission, Campaign
from utils import asdict

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


# このテストクラスはRecruiter.load_configが正しく動作することを前提にしている

class RecruiterTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        config_path = '{0}/recruit.yml'.format(os.path.dirname(__file__))
        recruiter.logger.setLevel(ERROR)
        recruiter.initialize_app(config_path)
        app = Flask(__name__)
        app.register_blueprint(recruiter.server, url_prefix="/recruiter")
        self.app = app.test_client()

    def tearDown(self):
        pass

# [GET] /commanders
    def test_list_commander(self):
        response = self.app.get('/recruiter/commanders')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        config_id_list = [tr.commander for tr in recruiter._app.TroopList]
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "commanders": config_id_list
        }
        self.assertEqual(actual, expected)

# [GET] /commanders/{com_id}
    def test_get_commander_info(self):
        pass

    def test_get_not_registered_commander_info(self):
        pass

    def test_get_invalid_commander_info(self):
        pass

# [PUT] /commanders/{com_id}
    def test_replace_commander_info(self):
        pass

# [GET] /department/squad/leader
    def test_get_squad_leader(self):
        pass

    def test_get_squad_leader_without_id(self):
        pass

    def test_get_squad_leader_with_invalid_id(self):
        pass

# [GET] /department/troop/commander
    def test_get_troop_commander(self):
        pass

    def test_get_troop_commander_without_id(self):
        pass

    def test_get_troop_commander_with_invalid_id(self):
        pass

