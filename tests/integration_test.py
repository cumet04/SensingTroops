import os
import unittest
import traceback
import flask
import json
from flask.testing import FlaskClient
from typing import Dict
from unittest.mock import patch
from utils.rest import test_client
from controller import RecruiterServer, CommanderServer, LeaderServer
from model import Recruiter, Commander, Leader, Soldier
from logging import getLogger, StreamHandler, DEBUG, ERROR

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

getLogger("model.recruiter").setLevel(ERROR)
getLogger("model.commander").setLevel(ERROR)
getLogger("model.leader").setLevel(ERROR)
getLogger("model.soldier").setLevel(ERROR)


class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = dict()  # type: Dict[str, FlaskClient]

        # インスタンス変数をデコレータに渡すため処理をメソッドにパックして実行
        @test_client(self.client)
        def init_apps():
            def internal_error(error):
                logger.error(">> Internal Server Error")
                logger.error(traceback.format_exc())
                return "internal server error"

            # init recruiter
            config_path = '{0}/recruit.yml'.format(os.path.dirname(__file__))
            RecruiterServer.set_model(Recruiter(config_path))
            rec_server = RecruiterServer.generate_server("/recruiter")
            rec_server.error_handler_spec[None][500] = internal_error
            self.client["recruiter"] = rec_server.test_client()

            # init commander
            com_model = Commander("cxxx0", "cmd_test",
                                  "test://cxxx0/commander/")
            com_model.awake("test://recruiter/recruiter/")
            CommanderServer.set_model(com_model)
            com_server = CommanderServer.generate_server("/commander")
            com_server.error_handler_spec[None][500] = internal_error
            self.client["cxxx0"] = com_server.test_client()

            # init leader
            lea_model = Leader("lxxx0", "lea_test", "test://lxxx0/leader/")
            lea_model.awake("test://recruiter/recruiter/", 2)
            LeaderServer.set_model(lea_model)
            lea_server = LeaderServer.generate_server("/leader")
            lea_server.error_handler_spec[None][500] = internal_error
            self.client["lxxx0"] = lea_server.test_client()

            # init soldier
            sol_model = Soldier("sxxx0", "sol_test")
            sol_model.awake("test://recruiter/recruiter/", 1)
        init_apps()

    def test_none(self):
        pass
