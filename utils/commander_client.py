#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import List
from utils.objects import LeaderInfo, CommanderInfo, Report, Campaign
from utils.helpers import asdict, RestClient

from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class CommanderClient(object):
    def __init__(self, client: RestClient):
        self.client = client

    def get_root(self) -> (CommanderInfo, str):
        try:
            st, res = self.client.get('')
            if st != 200:
                return None, res['status']['msg']
            return CommanderInfo(**res['info']), None
        except Exception as e:
            logger.error("in CommanderClient.get_root")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_campaigns(self) -> (List[Campaign], str):
        try:
            st, res = self.client.get('campaigns')
            if st != 200:
                return None, res['_status']['msg']
            return [Campaign(**cam) for cam in res['campaigns']], None
        except Exception as e:
            logger.error("in CommanderClient.get_campaigns")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_campaigns(self, obj: Campaign) -> (Campaign, str):
        try:
            st, res = self.client.post('campaigns', asdict(obj))
            if st != 200:
                return None, res['_status']['msg']
            return Campaign(**res['accepted']), None
        except Exception as e:
            logger.error("in CommanderClient.post_campaigns")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_subordinates(self) -> (List[LeaderInfo], str):
        try:
            st, res = self.client.get('subordinates')
            if st != 200:
                return None, res['_status']['msg']
            return [LeaderInfo(**l) for l in res['subordinates']]
        except Exception as e:
            logger.error("in CommanderClient.get_subordinates")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_subordinates(self, obj: LeaderInfo) -> (LeaderInfo, str):
        try:
            st, res = self.client.post('subordinates', asdict(obj))
            if st != 200:
                return None, res['_status']['msg']
            return LeaderInfo(**res['accepted']), None
        except Exception as e:
            logger.error("in CommanderClient.post_subordinates")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_subordinates_spec(self, sub_id: str) -> (LeaderInfo, str):
        try:
            st, res = self.client.get('subordinates/' + sub_id)
            if st != 200:
                return None, res['_status']['msg']
            return LeaderInfo(**res['info']), None
        except Exception as e:
            logger.error("in CommanderClient.get_subordinates_spec")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_report(self, sub_id: str, obj: Report) -> (Report, str):
        try:
            st, res = self.client.post('subordinates/{0}/report'.format(sub_id),
                                       asdict(obj))
            if st != 200:
                return res['_status']['msg']
            return Report(**res['accepted']), None
        except Exception as e:
            logger.error("in CommanderClient.post_report")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    @staticmethod
    def gen_rest_client(base_url):
        return CommanderClient(RestClient(base_url))


