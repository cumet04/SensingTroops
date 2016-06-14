import copy
import json
import pymongo
from typing import List, Dict
from model import LeaderInfo, CommanderInfo, Campaign, Mission
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Commander(object):
    def __init__(self, com_id, name, endpoint):
        self.id = com_id
        self.name = name
        self.endpoint = endpoint
        self.subordinates = {}  # type:Dict[str, LeaderInfo]
        self.campaigns = {}  # type:Dict[str, Campaign]
        self.report_cache = []

    def awake(self, recruiter_client):
        info = self.generate_info()
        res, err = recruiter_client.put_commanders_spec(self.id, info)
        if err is not None:
            logger.error("in Commander awake")
            logger.error("[PUT]recruiter/commanders/id failed: {0}".format(err))
            return False
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
        return sub_info

    def accept_report(self, sub_id, report):
        if not self.check_subordinate(sub_id):
            return False
        if report.purpose in self.campaigns:
            campaign = self.campaigns[report.purpose]
            col = pymongo.MongoClient(campaign.destination)['troops']['values']
            values = [{
                "purpose": campaign.purpose,
                "time": w["time"],
                "values": w["values"]
            } for w in report.values]
            col.insert_many(values)

        logger.info("accept_report: {0}".format(
            json.dumps(report.to_dict(), sort_keys=True, indent=2)
        ))
        self.report_cache.append(report)
        return True
