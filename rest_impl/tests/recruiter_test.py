import os
import unittest
import json
import traceback
from controller import RecruiterServer
from model import Recruiter, CommanderInfo
from logging import getLogger, StreamHandler, DEBUG, ERROR


logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

getLogger("model").setLevel(ERROR)


# このテストクラスはRecruiter.load_configが正しく動作することを前提にしている

class RecruiterTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        config_path = '{0}/recruit.yml'.format(os.path.dirname(__file__))
        recruiter = Recruiter(config_path)
        RecruiterServer.set_model(recruiter)
        server = RecruiterServer.generate_server("/recruiter")
        @server.errorhandler(500)
        def internal_error(error):
            logger.error(">> Internal Server Error")
            logger.error(traceback.format_exc())
            return "internal server error", 500
        self.app = server.test_client()

    def tearDown(self):
        pass

# [GET] /commanders
    def test_list_commander(self):
        response = self.app.get('/recruiter/commanders')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        config_id_list = ["cxxx0", "cxxx1"]
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "commanders": config_id_list
        }
        self.assertEqual(actual, expected)

# [GET] /commanders/{com_id}
    def test_get_commander_info(self):
        # add a commander
        commander = CommanderInfo(id='cxxx0',
                                  name='cmd_http',
                                  place="S101",
                                  endpoint='http://localhost:50000',
                                  subordinates=[],
                                  campaigns=[])
        self.app.put('/recruiter/commanders/cxxx0',
                     data=json.dumps(commander.to_dict()),
                     content_type='application/json')

        # get commander's info
        response = self.app.get('/recruiter/commanders/cxxx0')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'commander': commander.to_dict()
        }
        self.assertEqual(actual, expected)

    def test_get_commander_info_with_not_registered_id(self):
        # get not-registered commander's info
        response = self.app.get('/recruiter/commanders/cxxx0')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            'commander': {}
        }
        self.assertEqual(actual, expected)

    def test_get_commander_info_with_invalid_id(self):
        # get invalid commander's info
        response = self.app.get('/recruiter/commanders/bad_id')
        self.assertEqual(response.status_code, 404)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False, 'msg': "resource not found"},
        }
        self.assertEqual(actual, expected)

# [PUT] /commanders/{com_id}
    def test_replace_commander_info(self):
        # add a commander
        commander = CommanderInfo(id='cxxx0',
                                  name='cmd_http',
                                  place="",
                                  endpoint='http://localhost:50000',
                                  subordinates=[],
                                  campaigns=[])
        response = self.app.put('/recruiter/commanders/cxxx0',
                                data=json.dumps(commander.to_dict()),
                                content_type='application/json')

        # assert
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))

        commander.place = "S101"
        expected = {
            "_status": {'success': True, 'msg': "status is ok"},
            "commander": commander.to_dict()
        }
        self.assertEqual(actual, expected)

# [DELETE] /commanders/{cid}
    def test_delete_commander_info(self):
        # add a commander
        commander = CommanderInfo(id='cxxx0',
                                  name='cmd_http',
                                  place="",
                                  endpoint='http://localhost:50000',
                                  subordinates=[],
                                  campaigns=[])
        self.app.put('/recruiter/commanders/cxxx0',
                     data=json.dumps(commander.to_dict()),
                     content_type='application/json')

        response = self.app.delete('/recruiter/commanders/cxxx0')
        self.assertEqual(response.status_code, 200)
        actual = json.loads(response.data.decode("utf-8"))
        expected = {
            "_status": {'success': True, 'msg': "status is ok"}
        }
        self.assertEqual(actual, expected)


# [GET] /department/squad/leader
    def test_get_squad_leader(self):
        # TODO: commanderのモックが必要になるので後回し
        pass

    def test_get_squad_leader_without_id(self):
        response = self.app.get('/recruiter/department/squad/leader')
        self.assertEqual(response.status_code, 400)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False,
                        'msg': "Query param: soldier_id is required"},
        }
        self.assertEqual(actual, expected)

    def test_get_squad_leader_with_invalid_id(self):
        response = self.app.get('/recruiter/department/squad/leader' +
                                '?soldier_id=bad_id')
        self.assertEqual(response.status_code, 404)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False,
                        'msg': "Specified soldier does not exist on database"},
        }
        self.assertEqual(actual, expected)

# [GET] /department/troop/commander
    def test_get_troop_commander(self):
        # add a commander
        commander = CommanderInfo(id='cxxx1',
                                  name='cmd_http',
                                  place="S103",
                                  endpoint='http://localhost:50000',
                                  subordinates=[],
                                  campaigns=[])
        self.app.put('/recruiter/commanders/cxxx1',
                     data=json.dumps(commander.to_dict()),
                     content_type='application/json')

        # get commander's info with all leader_ids
        leaders = ['lxxx2', 'lxxx3', 'lxxx4']
        places = {"lxxx2": "desk2", "lxxx3": "desk3", "lxxx4": "desk4"}
        for leader_id in leaders:
            response = self.app.get('/recruiter/department/troop/commander' +
                                    '?leader_id=' + leader_id)
            self.assertEqual(response.status_code, 200)
            actual = json.loads(response.data.decode("utf-8"))

            # assert
            expected = {
                "_status": {'success': True, 'msg': "status is ok"},
                "commander": commander.to_dict(),
                "place": places[leader_id]
            }
            self.assertEqual(actual, expected)
        pass

    def test_get_troop_commander_without_id(self):
        response = self.app.get('/recruiter/department/troop/commander')
        self.assertEqual(response.status_code, 400)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False,
                        'msg': "Query-param leader_id is required"},
        }
        self.assertEqual(actual, expected)

    def test_get_troop_commander_with_invalid_id(self):
        response = self.app.get('/recruiter/department/troop/commander' +
                                '?leader_id=bad_id')
        self.assertEqual(response.status_code, 404)
        actual = json.loads(response.data.decode("utf-8"))

        # assert
        expected = {
            "_status": {'success': False,
                        'msg': "Specified leader does not exist on database"},
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
