import os
import unittest
import traceback
import utils.rest
from unittest.mock import patch
from controller import RecruiterServer, CommanderServer, LeaderServer
from model import Recruiter, Commander, Leader, Soldier
from logging import getLogger, StreamHandler, DEBUG, ERROR

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

getLogger("model").setLevel(ERROR)


def internal_error(error):
    logger.error(">> Internal Server Error")
    logger.error(traceback.format_exc())
    return "internal server error"


def gen_recruiter():
    config_path = '{0}/recruit.yml'.format(os.path.dirname(__file__))
    rec_model = Recruiter(config_path)
    RecruiterServer.set_model(rec_model)
    rec_server = RecruiterServer.generate_server("/recruiter")
    rec_server.error_handler_spec[None][500] = internal_error
    return rec_model, rec_server.test_client()


def gen_commander(com_id):
    com_model = Commander(com_id, "cmd_test",
                          "test://{0}/commander/".format(com_id))
    com_model.awake("test://recruiter/recruiter/")
    CommanderServer.set_model(com_model)
    com_server = CommanderServer.generate_server("/commander")
    com_server.error_handler_spec[None][500] = internal_error
    return com_model, com_server.test_client()


def gen_leader(lea_id):
    lea_model = Leader(lea_id, "lea_test", "test://{0}/leader/".format(lea_id))
    LeaderServer.set_model(lea_model)
    lea_server = LeaderServer.generate_server("/leader")
    lea_server.error_handler_spec[None][500] = internal_error
    return lea_model, lea_server.test_client()


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.models = dict()
        utils.rest.test_clients = dict()

    def start_single_without_awake(self):
        client = utils.rest.test_clients
        self.models["recruiter"], client["recruiter"] = gen_recruiter()
        self.models["cxxx0"], client["cxxx0"] = gen_commander("cxxx0")
        self.models["lxxx0"], client["lxxx0"] = gen_leader("lxxx0")
        self.models["sxxx0"] = Soldier("sxxx0", "sol_test")

    def awake_single(self):
        self.start_single_without_awake()
        self.models["cxxx0"].awake("test://recruiter/recruiter/")
        self.models["lxxx0"].awake("test://recruiter/recruiter/", 2)
        self.models["sxxx0"].awake("test://recruiter/recruiter/", 1)

    def test_awake_single(self):
        self.start_single_without_awake()
        self.assertTrue(
            self.models["cxxx0"].awake("test://recruiter/recruiter/"))
        self.assertTrue(
            self.models["lxxx0"].awake("test://recruiter/recruiter/", 2))
        self.assertTrue(
            self.models["sxxx0"].awake("test://recruiter/recruiter/", 1))

    def test_heartbeat(self):
        import time
        self.awake_single()
        time.sleep(3)  # leader, soldierのheartbeatが確実に1回行われるまで待つ
        self.assertTrue(self.models["lxxx0"].heartbeat_thread.is_alive())
        self.assertTrue(self.models["sxxx0"].heartbeat_thread.is_alive())


if __name__ == "__main__":
    unittest.main()
