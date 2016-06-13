from typing import List
from model import LeaderInfo, CommanderInfo
from utils.helpers import RestClient
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class RecruiterClient(object):
    def __init__(self, client: RestClient):
        self.client = client

    def get_commanders(self) -> (List[str], str):
        try:
            st, res = self.client.get('commanders')
            if st != 200:
                return None, res['_status']['msg']
            return res['commanders'], None
        except Exception as e:
            logger.error("in RecruiterClient.get_commanders")
            logger.error(">> got a exception: {0}".format(e))
            return None, None

    def get_commanders_spec(self, com_id: str) -> (CommanderInfo, str):
        try:
            st, res = self.client.get('commanders/' + com_id)
            if st != 200:
                return None, res['_status']['msg']
            return CommanderInfo.make(res['commander']), None
        except Exception as e:
            logger.error("in RecruiterClient.get_commanders_spec")
            logger.error(">> got a exception: {0}".format(e))
            return None, None

    def put_commanders_spec(self, com_id: str, obj: CommanderInfo) \
            -> (CommanderInfo, str):
        try:
            st, res = self.client.put('commanders/' + com_id, obj.to_dict())
            if st != 200:
                return None, res['_status']['msg']
            return CommanderInfo.make(res['commander']), None
        except Exception as e:
            logger.error("in RecruiterClient.put_commanders_spec")
            logger.error(">> got a exception: {0}".format(e))
            return None, None

    def get_department_squad_leader(self, soldier_id: str) -> (LeaderInfo, str):
        try:
            st, res = self.client.get('department/squad/leader?soldier_id=' +
                                      soldier_id)
            if st != 200:
                return None, res['_status']['msg']
            return LeaderInfo.make(res['leader']), None
        except Exception as e:
            logger.error("in RecruiterClient.get_department_squad_leader")
            logger.error(">> got a exception: {0}".format(e))
            return None, None

    def get_department_troop_commander(self, leader_id: str) \
            -> (CommanderInfo, str):
        try:
            st, res = self.client.get('department/troop/commander?leader_id=' +
                                      leader_id)
            if st != 200:
                return None, res['_status']['msg']
            return CommanderInfo.make(res['commander']), None
        except Exception as e:
            logger.error("in RecruiterClient.get_department_troop_commander")
            logger.error(">> got a exception: {0}".format(e))
            return None, None

    @staticmethod
    def gen_rest_client(base_url):
        return RecruiterClient(RestClient(base_url))
