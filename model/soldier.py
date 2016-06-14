import random
import datetime
from typing import List
from threading import Event, Thread
from model import SoldierInfo, Order, Work
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
        self.weapons = {
            "zero": lambda: 0,
            "random": random.random
        }
        self.orders = []
        self.superior_client = None  # type: LeaderClient
        self.heartbeat_thread = HeartBeat(self, 0)
        self.working_threads = []  # type: List[WorkingThread]

    def awake(self, rec_client: RecruiterClient, heartbeat_rate: int):
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
        self.superior_client = lea_client

        # orderを取得する
        self.start_heartbeat(heartbeat_rate)

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

    def accept_order(self, order: Order):
        th = WorkingThread(self, order)
        self.working_threads.append(th)
        th.start()

    def start_heartbeat(self, interval):
        self.heartbeat_thread.interval = interval
        self.heartbeat_thread.start()


class WorkingThread(Thread):
    def __init__(self, soldier: Soldier,order: Order):
        super(WorkingThread, self).__init__(daemon=True)
        self.order = order
        self.soldier = soldier
        self.lock = Event()

    def run(self):
        if 'timer' in self.order.trigger.keys():
            interval = self.order.trigger['timer']
            while not self.lock.wait(timeout=interval):
                values = [self.soldier.weapons[w]() for w in self.order.values]
                time = datetime.datetime.utcnow().isoformat()
                work = Work(time, self.order.purpose, values)

                lea_client = self.soldier.superior_client
                res, err = lea_client.post_work(self.soldier.id, work)
                if err is not None:
                    logger.error("in WorkingThread run")
                    logger.error(
                        "[GET]leader/subordinates/sub_id/work failed: {0}".
                         format(err))
        else:
            pass


class HeartBeat(Thread):
    def __init__(self, soldier: Soldier, interval: int):
        super(HeartBeat, self).__init__(daemon=True)
        self.lock = Event()
        self.soldier = soldier
        self.interval = interval
        self.etag = None

    def run(self):
        while not self.lock.wait(timeout=self.interval):
            lea_client = self.soldier.superior_client
            res, err = lea_client.get_subordinates_spec(self.soldier.id,
                                                        etag=self.etag)
            if lea_client.client.last_response.status_code == 304:
                continue
            if err is not None:
                logger.error("in HeartBeat run")
                logger.error("[GET]leader/subordinates/sub_id failed: {0}".
                             format(err))

            self.etag = lea_client.client.last_response.headers['ETag']
            logger.info([str(m) for m in res.orders])
            [w.lock.set() for w in self.soldier.working_threads]
            self.soldier.working_threads.clear()
            for m in res.orders:
                self.soldier.accept_order(m)

