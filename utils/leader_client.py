from typing import List
from model import LeaderInfo, SoldierInfo, Work, Mission
from utils.helpers import RestClient
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class LeaderClient(object):
    def __init__(self, client: RestClient):
        self.client = client

    def get_root(self) -> (LeaderInfo, str):
        try:
            st, res = self.client.get('')
            if st != 200:
                return None, res['status']['msg']
            return LeaderInfo.make(res['info']), None
        except Exception as e:
            logger.error("in LeaderClient.get_root")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_missions(self) -> (List[Mission], str):
        try:
            st, res = self.client.get('missions')
            if st != 200:
                return None, res['status']['msg']
            return [Mission.make(m) for m in res['missions']], None
        except Exception as e:
            logger.error("in LeaderClient.get_missions")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_missions(self, obj: Mission) -> (Mission, str):
        try:
            st, res = self.client.post('missions', obj.to_dict())
            if st != 200:
                return None, res['status']['msg']
            return Mission.make(res['accepted']), None
        except Exception as e:
            logger.error("in LeaderClient.post_missions")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_subordinates(self) -> (List[SoldierInfo], str):
        try:
            st, res = self.client.get('subordinates')
            if st != 200:
                return None, res['status']['msg']
            return [SoldierInfo.make(sol) for sol in res['subordinates']], None
        except Exception as e:
            logger.error("in LeaderClient.get_subordinates")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_subordinates(self, obj: SoldierInfo) -> (SoldierInfo, str):
        try:
            st, res = self.client.post('subordinates', obj.to_dict())
            if st != 200:
                return None, res['status']['msg']
            return SoldierInfo.make(res['accepted']), None
        except Exception as e:
            logger.error("in LeaderClient.post_subordinates")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def get_subordinates_spec(self, sub_id: str) -> (SoldierInfo, str):
        try:
            st, res = self.client.get('subordinates/' + sub_id)
            if st != 200:
                return None, res['status']['msg']
            return SoldierInfo.make(res['info']), None
        except Exception as e:
            logger.error("in LeaderClient.get_subordinates_spec")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    def post_work(self, sub_id: str, obj: Work) -> (Work, str):
        try:
            st, res = self.client.post('subordinates/' + sub_id, obj)
            if st != 200:
                return None, res['status']['msg']
            return Work.make(res['accepted']), None
        except Exception as e:
            logger.error("in LeaderClient.post_work")
            logger.error(">> got a exception: {0}".format(e.__class__.__name__))
            return None, None

    @staticmethod
    def gen_rest_client(base_url):
        return LeaderClient(RestClient(base_url))
