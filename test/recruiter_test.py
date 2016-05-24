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


class RecruiterTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        config_path = '{0}/../troops/recruit.yml'.format(os.path.dirname(__file__))
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
        expected = {'result': 'success', "commanders": config_id_list}
        self.assertEqual(actual, expected)