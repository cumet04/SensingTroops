#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import unittest
import commander
import json
from flask import Flask
from logging import getLogger, StreamHandler, FileHandler, DEBUG
from objects import LeaderInfo, CommanderInfo, Report, Mission

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class CommanderTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        del sys.modules['commander']
        import commander  # モジュールのリロードをしないと内部のappがリセットされないため
        commander.set_params("cxxx0", "cmd_http", "http://localhost:50000")
        app = Flask(__name__)
        app.register_blueprint(commander.server, url_prefix="/commander")
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_info(self):
        response = self.app.get('/commander/')
        self.assertEqual(response.status_code, 200)
        # follow_redirects=True)
        actual = json.loads(response.data.decode("utf-8"))

        commander = CommanderInfo(id='cxxx0',
                                  name='cmd_http',
                                  endpoint='http://localhost:50000',
                                  subordinates=[],
                                  campaigns=[])
        expected = {"result": "success", "info": dict(commander._asdict())}

        self.assertEqual(actual, expected)

    def test_add_subordinate(self):
        leader = LeaderInfo(id='lxxx0',
                            name='cmd_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            missions=[])
        response = self.app.post('/commander/subordinates',
                                 data=json.dumps(leader._asdict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        expected = {'result': 'success', "accepted": dict(leader._asdict())}
        self.assertEqual(actual, expected)

    def test_get_subordinates_single(self):
        # add a leader
        leader = LeaderInfo(id='lxxx0',
                            name='cmd_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            missions=[])
        self.app.post('/commander/subordinates',
                      data=json.dumps(leader._asdict()),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {'subordinates': [dict(leader._asdict())]}
        self.assertEqual(actual, expected)

    def test_get_subordinates_multi(self):
        # add some leader
        leader_base = LeaderInfo(id='lxxx0',
                                 name='cmd_http',
                                 endpoint='http://localhost:50000',
                                 subordinates=[],
                                 missions=[])
        leader_list = [
            leader_base._replace(id='lxxx0'),
            leader_base._replace(id='lxxx1'),
            leader_base._replace(id='lxxx2'),
            leader_base._replace(id='lxxx3'),
        ]
        for l in leader_list:
            self.app.post('/commander/subordinates',
                          data=json.dumps(l._asdict()),
                          content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))
        actual_list = actual['subordinates']

        # assert
        expected_list = [dict(l._asdict()) for l in leader_list]
        for exp in expected_list:
            if exp not in actual_list:
                self.fail('{0} is not found.'.format(exp))
