import copy
import json
import utils.rest as rest
from threading import Thread, Event
from typing import List, Dict
from model.info_obj import InformationObject
from model import LeaderInfo, Campaign, Mission
from model import logger


definition = {
    'type': 'object',
    'properties': {
        'id': {'description': "the man's ID",
               'type': 'string'},
        'name': {'type': 'string'},
        'place': {'type': 'string'},
        'endpoint': {'type': 'string'},
        'subordinates': {'description': "A list of subordinates's ID",
                         'type': 'array',
                         'items': {'type': 'string'}},
        'campaigns': {'type': 'array',
                      'items': {'$ref': '#/definitions/Campaign'}},
    }
}


class CommanderInfo(InformationObject):
    def __init__(self,
                 id: str,
                 name: str,
                 place: str,
                 endpoint: str,
                 subordinates: List[str],
                 campaigns: List[Campaign]):
        self.id = id
        self.name = name
        self.place = place
        self.endpoint = endpoint
        self.subordinates = subordinates
        self.campaigns = campaigns

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['id'],
                source['name'],
                source['place'],
                source['endpoint'],
                source['subordinates'],
                [Campaign.make(c) for c in source['campaigns']]
            )
        except KeyError:
            raise TypeError


class Commander(object):
    def __init__(self, com_id, name, endpoint):
        self.id = com_id
        self.name = name
        self.place = ""
        self.endpoint = endpoint
        self.subordinates = {}  # type:Dict[str, LeaderInfo]
        self.sub_heart_waits = {}  # type:Dict[str, Event]
        self.campaigns = {}  # type:Dict[str, Campaign]
        self.report_cache = []
        self.recruiter_ep = ""

    def shutdown(self):
        url = "{0}commanders/{1}".format(self.recruiter_ep, self.id)
        res, err = rest.delete(url)  # type: Response, str
        if err is not None:
            logger.error("Removing commander info from recruiter is failed.")
            return False
        return True

    def awake(self, rec_ep: str):
        self.recruiter_ep = rec_ep
        url = "{0}commanders/{1}".format(rec_ep, self.id)
        res, err = rest.put(url, json=self.generate_info().to_dict())
        if err is not None:
            return False
        new_info = CommanderInfo.make(res.json()["commander"])
        self.place = new_info.place
        logger.info("register commander to recruiter: success")
        return True

    def generate_info(self):
        """
        自身のパラメータ群からCommanderInfoオブジェクトを生成する
        :return CommanderInfo: 生成したCommanderInfo
        """
        return CommanderInfo(
            id=self.id,
            name=self.name,
            place=self.place,
            endpoint=self.endpoint,
            subordinates=list(self.subordinates.keys()),
            campaigns=list(self.campaigns.values()))

    def generate_ui(self):
        # TODO: implementation
        pass

    def check_subordinate(self, sub_id):
        """
        指定された兵隊が部下に存在するかを確認する
        :param str sub_id: 確認したい部下のID
        :return bool: 存在すればTrue
        """
        return sub_id in self.subordinates

    def get_sub_info(self, sub_id):
        return self.subordinates[sub_id]

    def accept_campaign(self, campaign: Campaign):
        # Campaignの更新であれば（=IDが同じであれば）既存のものを消す
        if campaign.get_id() in self.campaigns:
            old_cam = self.campaigns[campaign.get_id()]
            for sub in self.subordinates.values():
                [sub.missions.remove(m) for m in sub.missions
                 if m.purpose == old_cam.get_id()]

        # 部下のMissionを生成・割り当てる
        target_subs = []
        if campaign.place == "All":
            target_subs = list(self.subordinates.keys())
        m_base = Mission(author='',
                         place='All',
                         purpose=campaign.get_id(),
                         requirement=campaign.requirement,
                         trigger=campaign.trigger)
        for t_id in target_subs:
            mission = copy.deepcopy(m_base)
            mission.author = t_id
            self.subordinates[t_id].missions.append(mission)

        logger.info(">> got campaign:")
        logger.info(json.dumps(campaign.to_dict(), sort_keys=True, indent=2))
        self.campaigns[campaign.get_id()] = campaign
        return campaign

    def accept_subordinate(self, sub_info):
        """
        部下の入隊を受け入れる
        :param LeaderInfo sub_info: 受け入れるLeaderの情報
        :return bool:
        """
        if self.check_subordinate(sub_info.id):
            return None
        self.subordinates[sub_info.id] = sub_info
        self.sub_heart_waits[sub_info.id] = Event()
        Thread(target=self._heart_watch,
               args=(sub_info.id, ), daemon=True).start()

        old_campaigns = self.campaigns.values()
        [self.accept_campaign(c) for c in old_campaigns]
        return sub_info

    def _heart_watch(self, sid):
        while self.sub_heart_waits[sid].wait(timeout=5):
            # timeoutまでにevent.setされたら待ち続行
            # timeoutしたらK.I.A.
            self.sub_heart_waits[sid].clear()
        logger.error("へんじがない ただのしかばねのようだ :{0}".format(sid))
        self.remove_subordinate(sid)

    def receive_heartbeat(self, sid):
        if not self.check_subordinate(sid):
            return False
        self.sub_heart_waits[sid].set()

    def remove_subordinate(self, sub_id):
        if not self.check_subordinate(sub_id):
            return False
        del self.subordinates[sub_id]
        del self.sub_heart_waits[sub_id]
        return True

    def accept_report(self, sub_id, report):
        if not self.check_subordinate(sub_id):
            return False

        if report.purpose == "_error":
            logger.info(">> error report is received from {0}".format(sub_id))
            logger.info(report.values[0]["msg"])
            return True

        if report.purpose in self.campaigns:
            campaign = self.campaigns[report.purpose]
            if "mongodb://" in campaign.destination:
                push = MongoPush(campaign.destination)
                values = [{
                    "purpose": campaign.purpose,
                    "time": w["time"],
                    "values": w["values"]
                } for w in report.values]
                push.push_values(values)

            logger.info("accept_report: {0}".format(
                json.dumps(report.to_dict(), sort_keys=True, indent=2)
            ))
            self.report_cache.append(report)
        return True


class MongoPush(object):
    def __init__(self, uri):
        import pymongo
        import re
        match_result = re.match(r"mongodb://(.*?)/(.*?)/(.*)", uri)
        if match_result is None:
            logger.error("uri is not mongodb-uri: {0}".format(uri))
            return
        host = match_result.group(1)
        db_name = match_result.group(2)
        col_name = match_result.group(3)
        self.col = pymongo.MongoClient(host)[db_name][col_name]

    def push_values(self, values):
        if len(values) == 0:
            return
        self.col.insert_many(values)
