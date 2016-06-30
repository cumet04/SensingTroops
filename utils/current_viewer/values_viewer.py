import pymongo


def get_collection():
    return pymongo.MongoClient("192.168.0.21")["test"]["troops"]


def get_values(purpose, place, type):
    col = get_collection()
    s_purpose = {"purpose": purpose}
    s_place = {"place": place}
    s_type = {"data.type": type}
    search = {}
    search.update(s_purpose)
    search.update(s_place)
    search.update(s_type)

    filter = {"_id": 0}
    res = col.find(search, projection=filter)

    value_list = []
    for item in res:
        v = item["data"]["value"]
        unit = item["data"]["unit"]
        value_list.append([item["time"], v, unit])
    return value_list
