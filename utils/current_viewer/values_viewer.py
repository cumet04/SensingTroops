import pymongo
import datetime


def get_collection():
    return pymongo.MongoClient("192.168.0.21")["test"]["troops"]
    # return pymongo.MongoClient("localhost")["troops"]["values"]


def get_values(purpose, place, type, max_count):
    now = datetime.datetime.now(datetime.timezone.utc)
    limit_time = now - datetime.timedelta(days=1)

    col = get_collection()
    s_purpose = {"purpose": purpose}
    s_place = {"place": place}
    s_type = {"data.type": type}
    s_time = {"time": {"$gt": limit_time}}
    search = {}
    search.update(s_purpose)
    search.update(s_place)
    search.update(s_type)
    search.update(s_time)

    filter = {"_id": 0}
    res = col.find(search, projection=filter).sort("time", pymongo.DESCENDING)
    res_list = list(res)
    scaled_items = res_list[::len(res_list) // max_count + 1]

    return [
        [i["time"], i["data"]["value"], i["data"]["unit"]]
        for i in scaled_items
    ]
