import unittest
import json
import copy
import traceback
from controller import CommanderServer
from model.commander import Commander
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG, ERROR
from model import LeaderInfo, CommanderInfo, Requirement, Report, Campaign

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

getLogger("model.commander").setLevel(ERROR)


class CommanderTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        # TODO: commander.logger.setLevel(ERROR)
        commander = Commander("cxxx0", "cmd_http", "http://localhost:50000")
        CommanderServer.set_model(commander)
        server = CommanderServer.generate_server("/commander")

        @server.errorhandler(500)
        def internal_error(error):
            logger.error(">> Internal Server Error")
            logger.error(traceback.format_exc())
            return "internal server error"
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
            "info": com.to_dict()
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
                            requirement=Requirement(
                                values=["zero", "random"],
                                trigger={"timer": 10}
                            ),
                            trigger={"timer": 30})
        self.app.post('/commander/campaigns',
                      data=json.dumps(campaign.to_dict()),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/campaigns')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'campaigns': [campaign.to_dict()]
        }
        self.assertEqual(actual, expected)

    def test_get_campaigns_multi(self):
        # add some campaigns
        campaign_base = Campaign(author='cxxx0',
                                 destination='mongoserv',
                                 place='S101',
                                 purpose='A great app',
                                 requirement=Requirement(
                                     values=["zero", "random"],
                                     trigger={"timer": 10}
                                 ),
                                 trigger={"timer": 30})
        campaign_list = []
        for place in ['S101', 'S102', 'S103', 'S104']:
            c = copy.deepcopy(campaign_base)
            c.place = place
            campaign_list.append(c)
        for c in campaign_list:
            self.app.post('/commander/campaigns',
                          data=json.dumps(c.to_dict()),
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
        expected_list = [c.to_dict() for c in campaign_list]
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
                            requirement=Requirement(
                                values=["zero", "random"],
                                trigger={"timer": 10}
                            ),
                            trigger={"timer": 30})
        response = self.app.post('/commander/campaigns',
                                 data=json.dumps(campaign.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": campaign.to_dict()
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
                      data=json.dumps(leader.to_dict()),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/commander/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'subordinates': [leader.to_dict()]
        }
        self.assertEqual(actual, expected)

    def test_get_subordinates_multi(self):
        # add some leader
        leader_base = LeaderInfo(id='lxxx0',
                                 name='cmd_http',
                                 endpoint='http://localhost:50000',
                                 subordinates=[],
                                 missions=[])
        leader_list = []
        for l_id in ['lxxx0', 'lxxx1', 'lxxx2', 'lxxx3']:
            l = copy.deepcopy(leader_base)
            l.id = l_id
            leader_list.append(l)
        for l in leader_list:
            self.app.post('/commander/subordinates',
                          data=json.dumps(l.to_dict()),
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
        expected_list = [l.to_dict() for l in leader_list]
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
                                 data=json.dumps(leader.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": leader.to_dict()
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
                      data=json.dumps(leader.to_dict()),
                      content_type='application/json')

        # get the leader
        response = self.app.get('/commander/subordinates/lxxx0')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'info': leader.to_dict()
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
                      data=json.dumps(leader.to_dict()),
                      content_type='application/json')

        # submit a report
        report = Report(purpose="some app",
                        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        values="some values")
        response = self.app.post('/commander/subordinates/lxxx0/report',
                                 data=json.dumps(report.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": report.to_dict()
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
