import unittest
import time
import requests
import copy
import traceback
from controller import LeaderServer
from datetime import datetime
from json import dumps
from unittest.mock import patch
from logging import getLogger, StreamHandler, DEBUG, ERROR
from model import Soldier, SoldierInfo, Requirement, Work, Order

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class SoldierTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.soldier = Soldier("sxxx0", "sol_test")

    def tearDown(self):
        self.soldier.__del__()

    def test_order_do(self):
        self.soldier.superior_ep = "test://lxxx0/leader/"
        order = Order(author="sxxx0",
                      values=["zero", "random"],
                      trigger={"timer": 0.7},
                      purpose="some purpose hash")
        def accept_work(url, data=None, json=None, etag=None, **kwargs):
            res = requests.Response()
            res.status_code = 200
            res_dict = {
                "_status": {"msg": "ok", "success": True},
                "accepted": json
            }
            res._content = dumps(res_dict).encode()
            return res, None

        with patch("utils.rest.post", side_effect=accept_work) as m:
            self.soldier.accept_order(order)
            time.sleep(1)
            self.assertEqual(m.call_count, 1)
            self.assertEqual(m.call_args[0][0],
                             "test://lxxx0/leader/subordinates/sxxx0/work")

            # workのチェック
            actual = m.call_args[1]["json"]
            self.assertEqual(set(actual.keys()), {"time", "purpose", "values"})
            self.assertEqual(actual["purpose"], "some purpose hash")
            self.assertEqual(len(actual["values"]), 2)


if __name__ == "__main__":
    unittest.main()
