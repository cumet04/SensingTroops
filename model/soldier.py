from threading import Event, Thread
from model import SoldierInfo, LeaderInfo
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
        self.superior_client = None  # type: LeaderClient

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
        self.superior_client = lea_client

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

    def start_heartbeat(self, interval):
        # TODO: すでに存在する場合

        def polling(self: Soldier, interval):
            while not self.heartbeat_thread_lock.wait(timeout=interval):
                res, err = self.superior_client.get_subordinates_spec(self.id)
                if err is not None:
                    logger.error("in Soldier polling")
                    logger.error("[GET]leader/subordinates/sub_id failed: {0}".
                                 format(err))
                logger.info([str(o) for o in res.orders])

        self.heartbeat_thread_lock = Event()
        self.heartbeat_thread = Thread(target=polling, args=(self, interval))
        self.heartbeat_thread.start()
