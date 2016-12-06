from model import CommanderInfo, LeaderInfo, SoldierInfo, \
    Campaign, Mission, Order
import utils.rest as rest


def generate_data(rec_addr):
    url = "{0}commanders".format(rec_addr)
    res, err = rest.get(url)
    if err is not None:
        return {}

    com_addr_list = []
    for cid in res.json()["commanders"]:
        url = "{0}commanders/{1}".format(rec_addr, cid)
        res, err = rest.get(url)
        if err is not None:
            return {}

        com_info = res.json()["commander"]
        if len(com_info) == 0:
            continue
        com_addr_list.append(com_info["endpoint"])

    return [gen_commander_data(addr) for addr in com_addr_list]


def gen_commander_data(com_addr):
    res, err = rest.get(com_addr)
    if err is not None:
        return {}
    info = CommanderInfo.make(res.json()["info"])

    url = "{0}subordinates".format(com_addr)
    res, err = rest.get(url)
    if err is not None:
        return {}
    subs = res.json()["subordinates"]
    sub_addr_list = [sub["endpoint"] for sub in subs]

    leaders = [gen_leader_data(addr) for addr in sub_addr_list]
    leaders = [l for l in leaders if len(l) != 0]
    return {
        "text": "Commander: {0}({1}) at {2}".
            format(info.name, info.id, info.place),
        "icon": "troops commander",
        "href": info.endpoint,
        "nodes": [
            {
                "text": "campaigns",
                "nodes": [gen_campaign_data(c) for c in info.campaigns]
            },
            {
                "text": "subordinates",
                "nodes": leaders
            },
        ]
    }


def gen_campaign_data(campaign):
    return {
        "text": str(campaign)
    }


def gen_leader_data(lea_addr):
    res, err = rest.get(lea_addr)
    if err is not None:
        return {}
    info = LeaderInfo.make(res.json()["info"])

    url = "{0}subordinates".format(lea_addr)
    res, err = rest.get(url)
    if err is not None:
        return {}
    subs = res.json()["subordinates"]
    sub_info_list = [SoldierInfo.make(s) for s in subs]

    return {
        "text": "Leader: {0}({1}) at {2}".
            format(info.name, info.id, info.place),
        "icon": "troops leader",
        "href": info.endpoint,
        "nodes": [
            {
                "text": "missions",
                "nodes": [gen_mission_data(m) for m in info.missions]
            },
            {
                "text": "subordinates",
                "nodes": [gen_soldier_data(info) for info in sub_info_list]
            },
        ]
    }


def gen_mission_data(mission):
    return {
        "text": str(mission)
    }


def gen_soldier_data(info: SoldierInfo):
    return {
        "text": "Soldier: {0}({1}) at {2}".
            format(info.name, info.id, info.place),
        "icon": "troops soldier",
        "nodes": [
            {
                "text": "weapons: {0}".format(info.weapons),
            },
            {
                "text": "orders",
                "nodes": [gen_order_data(o) for o in info.orders]
            },
        ]
    }


def gen_order_data(order):
    return {
        "text": str(order)
    }
