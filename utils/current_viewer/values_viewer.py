import pymongo


def get_collection():
    return pymongo.MongoClient("localhost")["troops"]["values"]


def get_random_data():
    col = get_collection()
    search = {"values": {"$elemMatch": {"type": "random"}}}
    filter = {"_id": 0}
    res = col.find(search, projection=filter)

    value_list = []
    for item in res:
        # センサデータのvaluesからtypeがrandomのものを見つけそのvalueを取り出す
        values = item["values"]
        v = [o["value"] for o in values if o["type"] == "random"][0]
        value_list.append([item["time"], v])
    return value_list
