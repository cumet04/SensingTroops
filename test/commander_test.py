#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import commander
import json
from flask import Flask
from logging import getLogger, StreamHandler, DEBUG
from objects import LeaderInfo, CommanderInfo, Report, Mission

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class CommanderTestCase(unittest.TestCase):

    def setUp(self):
        commander.set_params("cxxx0", "cmd_http", "http://localhost:50000")
        app = Flask(__name__)
        app.register_blueprint(commander.server, url_prefix="/commander")
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_info(self):
        response = self.app.get('/commander/')
        actual = json.loads(response.data.decode("utf-8"))

        commander = CommanderInfo(id='cxxx0',
                                  name='cmd_http',
                                  endpoint='http://localhost:50000',
                                  subordinates=[],
                                  campaigns=[])
        expected = {"result": "success", "info": commander._asdict()}

        self.assertEqual(actual, expected)

