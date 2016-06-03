#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
from utils.objects import LeaderInfo, SoldierInfo, Work
from utils.recruiter_client import RecruiterClient
from utils.leader_client import LeaderClient
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Soldier(object):
    def __init__(self, sol_id, name):
        self.id = sol_id
        self.name = name
        self.weapons = {}
        self.orders = []

    def awake(self, rec_client: RecruiterClient):
        # 上官を解決する
        superior, err = rec_client.get_department_squad_leader(self.id)
        if err is not None:
            logger.error("in Leader awake")
            logger.error("[GET]recruiter/department/squad/leader" +
                         " failed: {0}".format(err))
            return False
        logger.info("superior was resolved: id={0}".format(superior.id))

        # 分隊に加入する
        lea_client = LeaderClient.gen_rest_client(superior.endpoint)
        res, err = lea_client.post_subordinates(self.generate_info())
        if err is not None:
            logger.error("in Soldier awake")
            logger.error("[POST]leader/subordinates failed: {0}".format(err))
            return False
        logger.info("joined to squad")

        # orderを取得する
        # TODO: job assignが実装され次第

    def generate_info(self) -> SoldierInfo:
        """
        自身のパラメータ群からSoldierInfoオブジェクトを生成する
        :return SoldierInfo: 生成したSoldierInfo
        """
        return SoldierInfo(
            id=self.id,
            name=self.name,
            weapons=list(self.weapons.keys()),
            orders=self.orders)

