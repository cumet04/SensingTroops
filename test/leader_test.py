#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../troops')

import unittest
import leader
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


class LeaderTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        leader.initialize_app("lxxx0", "lea_http", "http://localhost:50000")
        app = Flask(__name__)
        app.register_blueprint(leader.server, url_prefix="/leader")
        self.app = app.test_client()

    def tearDown(self):
        pass

# [GET] /
    def test_get_info(self):
        pass

# [GET] /missions
    def test_get_missions_none(self):
        pass

    def test_get_missions_single(self):
        pass

    def test_get_missions_multi(self):
        pass

# [POST] /missions
    def test_add_missions(self):
        pass

# [GET] /subordinates
    def test_get_subordinates_none(self):
        pass

    def test_get_subordinates_single(self):
        pass

    def test_get_subordinates_multi(self):
        pass

# [POST] /subordinates
    def test_add_subordinates(self):
        pass

# [GET] /subordinates/{sub_id}
    def test_get_subordinate_info(self):
        pass

    def test_get_subordinate_info_with_invalid_id(self):
        pass

# [POST] /subordinates/{sub_id}/work
    def test_submit_work(self):
        pass
