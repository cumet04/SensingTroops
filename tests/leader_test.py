import unittest
import json
import copy
from controller import LeaderServer
from model.leader import Leader
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG, ERROR
from model import LeaderInfo, SoldierInfo, Work, Mission

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class LeaderTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        # utils.helpers.logger.setLevel(ERROR)
        # leader.logger.setLevel(ERROR)
        self.leader_obj = Leader("lxxx0", "lea_http", "http://localhost:50000")
        LeaderServer.set_model(self.leader_obj)
        server = LeaderServer.generate_server("/leader")
        self.app = server.test_client()

    def tearDown(self):
        pass

# [GET] /
    def test_get_info(self):
        response = self.app.get('/leader', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        lea = LeaderInfo(id='lxxx0',
                         name='lea_http',
                         endpoint='http://localhost:50000',
                         subordinates=[],
                         missions=[])
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "info": lea.to_dict()
        }
        self.assertEqual(actual, expected)

# [GET] /missions
    def test_get_missions_none(self):
        response = self.app.get('/leader/missions')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'missions': []
        }
        self.assertEqual(actual, expected)

    def test_get_missions_single(self):
        # add a mission
        mission = Mission(author='lxxx0',
                          destination='mongoserv',
                          place='on desk',
                          purpose='A great app',
                          requirements={
                              "values": "val",
                              "trigger": "tri"
                          },
                          trigger='a trigger')
        self.leader_obj.accept_mission(mission)

        # get subordinates
        response = self.app.get('/leader/missions')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'missions': [mission.to_dict()]
        }
        self.assertEqual(actual, expected)

    def test_get_missions_multi(self):
        # add some missions
        mission_base = Mission(author='lxxx0',
                               destination='mongoserv',
                               place='on desk',
                               purpose='A great app',
                               requirements={
                                   "values": "val",
                                   "trigger": "tri"
                               },
                               trigger='a trigger')
        mission_list = []
        for place in ['on chair', 'front of door', 'on desk', 'living room']:
            m = copy.deepcopy(mission_base)
            m.place = place
            mission_list.append(m)

        for m in mission_list:
            self.leader_obj.accept_mission(m)

        # get missions
        response = self.app.get('/leader/missions')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))
        actual_list = actual['missions']

        # assert status
        expected_status = {'success': True, 'msg': "status is ok"}
        self.assertEqual(actual['_status'], expected_status)

        # assert items
        expected_list = [c.to_dict() for c in mission_list]
        self.assertEqual(len(actual_list), len(expected_list))
        for exp in expected_list:
            if exp not in actual_list:
                self.fail('{0} is not found.'.format(exp))
        pass

# [GET] /subordinates
    def test_get_subordinates_none(self):
        response = self.app.get('/leader/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'subordinates': []
        }
        self.assertEqual(actual, expected)

    def test_get_subordinates_single(self):
        # add a soldier
        soldier = SoldierInfo(id='sxxx0',
                              name='sol_http',
                              weapons=[],
                              orders=[])
        self.app.post('/leader/subordinates',
                      data=json.dumps(soldier.to_dict()),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/leader/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'subordinates': [soldier.to_dict()]
        }
        self.assertEqual(actual, expected)

    def test_get_subordinates_multi(self):
        # add some soldier
        soldier_base = SoldierInfo(id='sxxx0',
                                   name='sol_http',
                                   weapons=[],
                                   orders=[])
        soldier_list = []
        for s_id in ['sxxx0', 'sxxx1', 'sxxx2', 'sxxx3']:
            s = copy.deepcopy(soldier_base)
            s.id = s_id
            soldier_list.append(s)
        for s in soldier_list:
            self.app.post('/leader/subordinates',
                          data=json.dumps(s.to_dict()),
                          content_type='application/json')

        # get subordinates
        response = self.app.get('/leader/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))
        actual_list = actual['subordinates']

        # assert status
        expected_status = {'success': True, 'msg': "status is ok"}
        self.assertEqual(actual['_status'], expected_status)

        # assert items
        expected_list = [s.to_dict() for s in soldier_list]
        self.assertEqual(len(actual_list), len(expected_list))
        for exp in expected_list:
            if exp not in actual_list:
                self.fail('{0} is not found.'.format(exp))
        pass

# [POST] /subordinates
    def test_add_subordinates(self):
        soldier = SoldierInfo(id='sxxx0',
                              name='sol_http',
                              weapons=[],
                              orders=[])
        response = self.app.post('/leader/subordinates',
                                 data=json.dumps(soldier.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": soldier.to_dict()
        }
        self.assertEqual(actual, expected)

# [GET] /subordinates/{sub_id}
    def test_get_subordinate_info(self):
        # add soldier
        soldier = SoldierInfo(id='sxxx0',
                              name='sol_http',
                              weapons=[],
                              orders=[])
        self.app.post('/leader/subordinates',
                      data=json.dumps(soldier.to_dict()),
                      content_type='application/json')

        # get the soldier
        response = self.app.get('/leader/subordinates/sxxx0')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'info': soldier.to_dict()
        }
        self.assertEqual(actual, expected)

    def test_get_subordinate_info_with_invalid_id(self):
        # get the soldier
        response = self.app.get('/leader/subordinates/bad_id')
        self.assertEqual(response.status_code, 404)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False,
                        'msg': "The subordinate is not found"},
        }
        self.assertEqual(actual, expected)

# [POST] /subordinates/{sub_id}/work
    def test_submit_work(self):
        # add soldier
        soldier = SoldierInfo(id='sxxx0',
                              name='sol_http',
                              weapons=[],
                              orders=[])
        self.app.post('/leader/subordinates',
                      data=json.dumps(soldier.to_dict()),
                      content_type='application/json')

        # submit a work
        work = Work(purpose="some app",
                    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    values="some values")
        response = self.app.post('/leader/subordinates/sxxx0/work',
                                 data=json.dumps(work.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": work.to_dict()
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
