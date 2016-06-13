import copy
from threading import Event, Thread
from model import SoldierInfo, LeaderInfo, Mission, Order
from typing import List, Dict
from utils.commander_client import CommanderClient
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Leader(object):
    def __init__(self, leader_id, name, endpoint):
        self.id = leader_id
        self.name = name
        self.endpoint = endpoint
        self.subordinates = {}  # type:Dict[str, SoldierInfo]
        self.missions = {}  # type:Dict[str, Mission]
        self.work_cache = []
        self.superior_client = None  # type:CommanderClient

    def awake(self, rec_client, heartbeat_rate: int):
        # 上官を解決する
        superior, err = rec_client.get_department_troop_commander(self.id)
        if superior is None and err is None:
            return False
        if err is not None:
            logger.error("in Leader awake")
            logger.error("[GET]recruiter/department/troop/commander" +
                         " failed: {0}".format(err))
            return False
        logger.info("superior was resolved: id={0}".format(superior.id))

        # 部隊に加入する
        com_client = CommanderClient.gen_rest_client(superior.endpoint)
        res, err = com_client.post_subordinates(self.generate_info())
        if res is None and err is None:
            return False
        if err is not None:
            logger.error("in Leader awake")
            logger.error("[POST]commander/subordinates failed: {0}".format(err))
            return False
        logger.info("joined to troop")
        self.superior_client = com_client

        # missionを取得する
        self.start_heartbeat(heartbeat_rate)

    def generate_info(self) -> LeaderInfo:
        """
        自身のパラメータ群からLeaderInfoオブジェクトを生成する
        :return LeaderInfo: 生成したLeaderInfo
        """
        return LeaderInfo(
            id=self.id,
            name=self.name,
            endpoint=self.endpoint,
            subordinates=list(self.subordinates.keys()),
            missions=list(self.missions.keys()))

    def check_subordinate(self, sub_id):
        """
        指定された兵隊が部下に存在するかを確認する
        :param str sub_id: 確認したい部下のID
        :return bool: 存在すればTrue
        """
        return sub_id in self.subordinates

    def update_missions(self, missions: List[Mission]):
        pass

    def start_heartbeat(self, interval):
        # TODO: すでに存在する場合

        def polling(leader: Leader, interval):
            while not self.heartbeat_thread_lock.wait(timeout=interval):
                res, err = self.superior_client.get_subordinates_spec(self.id)
                if err is not None:
                    logger.error("in Leader polling")
                    logger.error("[GET]commander/subordinates/sub_id failed: {0}".
                                 format(err))
                logger.info([str(m) for m in res.missions])
                for m in res.missions:
                    leader.accept_mission(m)

        self.heartbeat_thread_lock = Event()
        self.heartbeat_thread = Thread(target=polling, args=(self, interval))
        self.heartbeat_thread.start()

    def accept_mission(self, mission: Mission) -> Mission:
        # 部下のOrderを生成・割り当てる
        target_subs = []
        if mission.place == "All":
            target_subs = list(self.subordinates.keys())
        o_base = Order(author="",
                       values=mission.requirement.values,
                       trigger=mission.requirement.trigger,
                       purpose=mission.get_id())
        for t_id in target_subs:
            order = copy.deepcopy(o_base)
            order.author = t_id
            self.subordinates[t_id].orders.append(order)

        # 自身のデータ送信スレッドを生成する
        pass  # not implemented yet

        self.missions[mission.purpose] = mission
        return mission

    def get_sub_info(self, sub_id):
        return self.subordinates[sub_id]

    def accept_subordinate(self, sub_info):
        """
        部下の入隊を受け入れる
        :param SoldierInfo sub_info: 受け入れるLeaderの情報
        :return bool:
        """
        logger.debug('In accept_subordinate:')
        logger.debug('> sub_info:{0}'.format(sub_info))
        if self.check_subordinate(sub_info.id):
            return False
        self.subordinates[sub_info.id] = sub_info
        return True

    def accept_work(self, sub_id, work):
        if self.check_subordinate(sub_id):
            return False
        self.work_cache.append(work)
        return True
