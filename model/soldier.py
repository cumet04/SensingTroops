import random
import datetime
import utils.rest as rest
from model import Order, Work, logger
from typing import List, Dict
from threading import Event, Thread
from model.info_obj import InformationObject


definition = {
    'type': 'object',
    'properties': {
        'id': {'description': "the man's ID",
               'type': 'string'},
        'name': {'type': 'string'},
        'place': {'type': 'string'},
        'weapons': {'description': "A list of weapon",
                    'type': 'array',
                    'items': {'type': 'object'}},
        'orders': {'type': 'array',
                   'items': {'$ref': '#/definitions/Order'}},
    }
}


class SoldierInfo(InformationObject):
    def __init__(self,
                 id: str,
                 name: str,
                 place: str,
                 weapons: List[object],
                 orders: List[Order]):
        self.id = id
        self.name = name
        self.place = place
        self.weapons = weapons
        self.orders = orders

    @classmethod
    def make(cls, source: dict):
        try:
            return cls(
                source['id'],
                source['name'],
                source['place'],
                source['weapons'],
                [Order.make(o) for o in source['orders']]
            )
        except KeyError:
            raise TypeError


class Soldier(object):
    def __init__(self, sol_id, name):
        self.id = sol_id
        self.name = name
        self.place = ""
        self.weapons = {
            "zero": lambda: (0, "-"),
            "random": lambda: (random.random(), "-")
        }
        self.orders = {}  # type:Dict[str, Order]
        self.superior_ep = ""  # type: str
        self.heartbeat_thread = HeartBeat(self, 0)
        self.working_threads = []  # type: List[WorkingThread]

    def shutdown(self):
        self.heartbeat_thread.lock.set()
        [w.lock.set() for w in self.working_threads]

        if self.superior_ep == "":
            return True
        url = "{0}subordinates/{1}".format(self.superior_ep, self.id)
        res, err = rest.delete(url)
        if err is not None:
            logger.error("Removing soldier info from leader is failed.")
            return False
        return True

    def awake(self, rec_ep: str, heartbeat_rate: int):
        from model import LeaderInfo

        # 上官を解決する
        url = rec_ep + 'department/squad/leader?soldier_id=' + self.id
        res, err = rest.get(url)
        if err is not None:
            return False
        self.place = res.json()["place"]
        superior = LeaderInfo.make(res.json()['leader'])
        self.superior_ep = superior.endpoint
        logger.info("superior was resolved: id={0}".format(superior.id))

        # 分隊に加入する
        url = self.superior_ep + "subordinates"
        info = SoldierInfo(
            id=self.id,
            name=self.name,
            place=self.place,
            weapons=list(self.weapons.keys()),
            orders=list(self.orders.values()))
        res, err = rest.post(url, json=info.to_dict())
        if err is not None:
            return False
        logger.info("joined to squad: leader_id: {0}".format(superior.id))

        # orderを取得する
        self.heartbeat_thread.interval = heartbeat_rate
        self.heartbeat_thread.start()
        return True

    def accept_order(self, order: Order):
        if order.get_id() in self.orders:
            self.remove_order(order.get_id())

        th = WorkingThread(self, order)
        self.working_threads.append(th)
        th.start()
        self.orders[order.get_id()] = order

    def remove_order(self, oid):
        del self.orders[oid]
        for th in self.working_threads:
            if oid == th.order.get_id():
                th.lock.set()
                self.working_threads.remove(th)


class WorkingThread(Thread):
    def __init__(self, soldier: Soldier, order: Order):
        super(WorkingThread, self).__init__(daemon=True)
        self.order = order
        self.soldier = soldier
        self.lock = Event()

    def run(self):
        if 'timer' in self.order.trigger.keys():
            interval = self.order.trigger['timer']
            while not self.lock.wait(timeout=interval):
                values = []
                for type in self.order.values:
                    val, unit = self.soldier.weapons[type]()
                    if val is None:
                        self.soldier.shutdown()
                        return
                    values.append({"type": type, "value": val, "unit": unit})
                time = datetime.datetime.now(datetime.timezone.utc).isoformat()
                work = Work(time, self.order.purpose, values)

                url = "{0}subordinates/{1}/work".format(
                    self.soldier.superior_ep, self.soldier.id)
                res, err = rest.post(url, json=work.to_dict())
                if err is not None:
                    self.soldier.shutdown()
                    logger.fatal('in WorkingThread, failed to post work: {0}', err)
                    return
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
            url = self.soldier.superior_ep + "subordinates/" + self.soldier.id
            res, err = rest.get(url, etag=self.etag)
            if err is not None:
                # TODO: エラー処理ちゃんとやる
                logger.error('In HeartBeat, failed to post report')
                logger.error('> err: {0}', err)
                break
            if res.status_code == 304:
                continue
            self.etag = res.headers['ETag']
            info = SoldierInfo.make(res.json()['info'])

            logger.info([str(m) for m in info.orders])

            # 以前に受理されているorderにはあるが新規のorderリストには無い
            # （消された）orderを消す
            oid_list = [o.get_id() for o in info.orders]
            for old_oid in self.soldier.orders.keys():
                if old_oid not in oid_list:
                    self.soldier.remove_order(old_oid)

            for m in info.orders:
                self.soldier.accept_order(m)
        self.soldier.shutdown()
