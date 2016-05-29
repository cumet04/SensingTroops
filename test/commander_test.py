#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../troops')

import unittest
import commander
import json
import utils
from datetime import datetime
from flask import Flask
from logging import getLogger, StreamHandler, DEBUG, ERROR
from objects import LeaderInfo, CommanderInfo, Report, Campaign
from utils import asdict

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class CommanderTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        utils.logger.setLevel(ERROR)
        commander.logger.setLevel(ERROR)
        commander.initialize_app("cxxx0", "cmd_http", "http://localhost:50000")
        server = Flask(__name__)
        server.register_blueprint(commander.app,
                                  url_prefix=commander.url_prefix)
        self.app = server.test_client()

    def tearDown(self):
        pass

# [GET] /
    def test_get_info(self):
        response = self.app.get('/commander', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        com = CommanderInfo(id='cxxx0',
                            name='cmd_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            campaigns=[])
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "info": asdict(com)
        }
        self.assertEqual(actual, expected)

# [GET] /campaigns
    def test_get_campaigns_none(self):
        response = self.app.get('/commander/campaigns')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'campaigns': []
        }
        self.assertEqual(actual, expected)

    def test_get_campaigns_single(self):
        # add a campaigns
        campaign = Campaign(author='cxxx0',
                            destination='mongoserv',
                            place='S101',
                            purpose='A great app',
                            requirements='brightness sound',
                            trigger='a trigger')
        self.app.post('/commander/campaigns',
                      data=json.dumps(asdict(campaign)),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/campaigns')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'campaigns': [asdict(campaign)]
        }
        self.assertEqual(actual, expected)

    def test_get_campaigns_multi(self):
        # add some campaigns
        campaign_base = Campaign(author='cxxx0',
                                 destination='mongoserv',
                                 place='S101',
                                 purpose='A great app',
                                 requirements='brightness sound',
                                 trigger='a trigger')
        campaign_list = [
            campaign_base._replace(place='S101'),
            campaign_base._replace(place='S102'),
            campaign_base._replace(place='S103'),
            campaign_base._replace(place='S104'),
        ]
        for c in campaign_list:
            self.app.post('/commander/campaigns',
                          data=json.dumps(asdict(c)),
                          content_type='application/json')

        # get campaigns
        response = self.app.get('/commander/campaigns')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))
        actual_list = actual['campaigns']

        # assert status
        expected_status = {'success': True, 'msg': "status is ok"}
        self.assertEqual(actual['_status'], expected_status)

        # assert items
        expected_list = [asdict(c) for c in campaign_list]
        self.assertEqual(len(actual_list), len(expected_list))
        for exp in expected_list:
            if exp not in actual_list:
                self.fail('{0} is not found.'.format(exp))
        pass

# [POST] /campaigns
    def test_add_campaign(self):
        # 各種パラメータの詳細が決まっていないため、暫定値を採用。
        # 最終的には、API自体に無効な入力パラメータをハネる機能を搭載したうえで
        # TODO: 無効値を確認する用のテストを作成すべき
        campaign = Campaign(author='cxxx0',
                            destination='mongoserv',
                            place='S101',
                            purpose='A great app',
                            requirements='brightness sound',
                            trigger='a trigger')
        response = self.app.post('/commander/campaigns',
                                 data=json.dumps(asdict(campaign)),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": asdict(campaign)
        }
        self.assertEqual(actual, expected)

# [GET] /subordinates
    def test_get_subordinates_none(self):
        response = self.app.get('/commander/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'subordinates': []
        }
        self.assertEqual(actual, expected)

    def test_get_subordinates_single(self):
        # add a leader
        leader = LeaderInfo(id='lxxx0',
                            name='cmd_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            missions=[])
        self.app.post('/commander/subordinates',
                      data=json.dumps(asdict(leader)),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'subordinates': [asdict(leader)]
        }
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
                          data=json.dumps(asdict(l)),
                          content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))
        actual_list = actual['subordinates']

        # assert status
        expected_status = {'success': True, 'msg': "status is ok"}
        self.assertEqual(actual['_status'], expected_status)

        # assert items
        expected_list = [asdict(l) for l in leader_list]
        self.assertEqual(len(actual_list), len(expected_list))
        for exp in expected_list:
            if exp not in actual_list:
                self.fail('{0} is not found.'.format(exp))
        pass

# [POST] /subordinates
    def test_add_subordinate(self):
        leader = LeaderInfo(id='lxxx0',
                            name='cmd_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            missions=[])
        response = self.app.post('/commander/subordinates',
                                 data=json.dumps(asdict(leader)),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": asdict(leader)
        }
        self.assertEqual(actual, expected)

# [GET] /subordinates/{sub_id}
    def test_get_subordinate_info(self):
        # add leader
        leader = LeaderInfo(id='lxxx0',
                            name='lea_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            missions=[])
        self.app.post('/commander/subordinates',
                      data=json.dumps(asdict(leader)),
                      content_type='application/json')

        # get the leader
        response = self.app.get('/commander/subordinates/lxxx0')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'info': asdict(leader)
        }
        self.assertEqual(actual, expected)

    def test_get_subordinate_info_with_invalid_id(self):
        # get the leader
        response = self.app.get('/commander/subordinates/bad_id')
        self.assertEqual(response.status_code, 404)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False,
                        'msg': "The subordinate is not found"},
        }
        self.assertEqual(actual, expected)

# [POST] /subordinates/{sub_id}/report
    def test_submit_report(self):
        # add leader
        leader = LeaderInfo(id='lxxx0',
                            name='lea_http',
                            endpoint='http://localhost:50000',
                            subordinates=[],
                            missions=[])
        self.app.post('/commander/subordinates',
                      data=json.dumps(asdict(leader)),
                      content_type='application/json')

        # submit a report
        report = Report(purpose="some app",
                        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        values="some values")
        response = self.app.post('/commander/subordinates/lxxx0/report',
                                 data=json.dumps(asdict(report)),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": asdict(report)
        }
        self.assertEqual(actual, expected)
