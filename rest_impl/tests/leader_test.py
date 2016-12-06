import unittest
import copy
import requests
import time
import traceback
from json import dumps, loads
from unittest.mock import patch
from controller import LeaderServer
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG, ERROR
from model import Leader, LeaderInfo, SoldierInfo, Requirement, Work, Mission

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

getLogger("model").setLevel(ERROR)


class LeaderTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.leader_obj = Leader("lxxx0", "lea_http", "http://localhost:50000")
        LeaderServer.set_model(self.leader_obj)
        server = LeaderServer.generate_server("/leader")

        @server.errorhandler(500)
        def internal_error(error):
            logger.error(">> Internal Server Error")
            logger.error(traceback.format_exc())
            return "internal server error"
        self.app = server.test_client()

    def tearDown(self):
        self.leader_obj.shutdown()

# [GET] /
    def test_get_info(self):
        response = self.app.get('/leader', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))

        lea = LeaderInfo(id='lxxx0',
                         name='lea_http',
                         place="",
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
        actual = loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'missions': []
        }
        self.assertEqual(actual, expected)

    def test_get_missions_single(self):
        # add a mission
        mission = Mission(author='lxxx0',
                          place='on desk',
                          purpose='A great app',
                          requirement=Requirement(
                              values=["zero", "random"],
                              trigger={"timer": 10}
                          ),
                          trigger={"timer": 30})
        self.leader_obj.accept_mission(mission)

        # get subordinates
        response = self.app.get('/leader/missions')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'missions': [mission.to_dict()]
        }
        self.assertEqual(actual, expected)

    def test_get_missions_multi(self):
        # add some missions
        mission_base = Mission(author='lxxx0',
                               place='on desk',
                               purpose='A great app',
                               requirement=Requirement(
                                   values=["zero", "random"],
                                   trigger={"timer": 10}
                               ),
                               trigger={"timer": 30})
        mission_list = []
        for purpose in ['on chair', 'front of door', 'on desk', 'living room']:
            m = copy.deepcopy(mission_base)
            m.purpose = purpose
            mission_list.append(m)

        for m in mission_list:
            self.leader_obj.accept_mission(m)

        # get missions
        response = self.app.get('/leader/missions')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))
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
        actual = loads(response.data.decode("utf-8"))

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
                              place="left",
                              weapons=[],
                              orders=[])
        self.app.post('/leader/subordinates',
                      data=dumps(soldier.to_dict()),
                      content_type='application/json')

        # get subordinates
        response = self.app.get('/leader/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))

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
                                   place="left",
                                   weapons=[],
                                   orders=[])
        soldier_list = []
        for s_id in ['sxxx0', 'sxxx1', 'sxxx2', 'sxxx3']:
            s = copy.deepcopy(soldier_base)
            s.id = s_id
            soldier_list.append(s)
        for s in soldier_list:
            self.app.post('/leader/subordinates',
                          data=dumps(s.to_dict()),
                          content_type='application/json')

        # get subordinates
        response = self.app.get('/leader/subordinates')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))
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
                              place="left",
                              weapons=[],
                              orders=[])
        response = self.app.post('/leader/subordinates',
                                 data=dumps(soldier.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))

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
                              place="left",
                              weapons=[],
                              orders=[])
        self.app.post('/leader/subordinates',
                      data=dumps(soldier.to_dict()),
                      content_type='application/json')

        # get the soldier
        response = self.app.get('/leader/subordinates/sxxx0')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))

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
        actual = loads(response.data.decode("utf-8"))

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
                              place="left",
                              weapons=[],
                              orders=[])
        self.app.post('/leader/subordinates',
                      data=dumps(soldier.to_dict()),
                      content_type='application/json')

        # submit a work
        work = Work(purpose="some app",
                    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    values="some values")
        response = self.app.post('/leader/subordinates/sxxx0/work',
                                 data=dumps(work.to_dict()),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        actual = loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "accepted": work.to_dict()
        }
        self.assertEqual(actual, expected)

# internal logic test ----------------------------------------------------------

    def test_missoin_do(self):
        def post_report(url, data=None, json=None, etag=None, **kwargs):
            res = requests.Response()
            res.status_code = 200
            res_dict = {
                "_status": {"msg": "ok", "success": True},
                "accepted": json
            }
            res._content = dumps(res_dict).encode()
            return res, None

        self.leader_obj.superior_ep = "test://cxxx0/commander/"
        soldier = SoldierInfo(id="sxxx0", name="sol-test", place="left",
                              weapons=[], orders=[])
        self.leader_obj.accept_subordinate(soldier)

        mission = Mission(author="sxxx0",
                          requirement=Requirement(
                              values=["zero", "random"],
                              trigger={"timer": 0.4}
                          ),
                          trigger={"timer": 0.7},
                          place="All",
                          purpose="some purpose hash")

        work_1 = Work(time=datetime.utcnow().isoformat(),
                      purpose=mission.get_id(),
                      values=[0, 0.584249])
        work_2 = Work(time=datetime.utcnow().isoformat(),
                      purpose=mission.get_id(),
                      values=[0, 0.238491])
        work_3 = Work(time=datetime.utcnow().isoformat(),
                      purpose="0" + mission.get_id()[:-1],  # 上２つとずらす
                      values=[0, 0.045066])
        self.leader_obj.accept_work("sxxx0", work_1)
        self.leader_obj.accept_work("sxxx0", work_2)
        self.leader_obj.accept_work("sxxx0", work_3)

        with patch("utils.rest.post", side_effect=post_report) as m:
            self.leader_obj.accept_mission(mission)
            time.sleep(1)
            self.assertEqual(m.call_count, 1)
            self.assertEqual(m.call_args[0][0],
                             "test://cxxx0/commander/subordinates/lxxx0/report")

            # reportのチェック
            actual = m.call_args[1]["json"]
            self.assertEqual(set(actual.keys()),
                             {"time", "place", "purpose", "values"})
            self.assertEqual(actual["purpose"], "some purpose hash")
            self.assertEqual(len(actual["values"]), 2)

            # report.valuesのチェック
            work_in_1 = work_1.to_dict()
            del work_in_1["purpose"]
            work_in_1["place"] = "left"
            work_in_2 = work_2.to_dict()
            del work_in_2["purpose"]
            work_in_2["place"] = "left"
            self.assertIn(work_in_1, actual["values"])
            self.assertIn(work_in_2, actual["values"])

        self.leader_obj.superior_ep = ""  # shutdownでDELETEを送信するのを阻止


if __name__ == "__main__":
    unittest.main()
