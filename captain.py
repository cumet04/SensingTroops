from logging import getLogger,StreamHandler,DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

import datetime
import json
import sys
import os
import pymongo

from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
from common import get_dict
from flask import Flask, jsonify, request, url_for, abort, Response

# client = pymongo.MongoClient(host='192.168.0.21', port=27017)
# self.coll = client.test.tmp
# self.coll.insert_many(data)

class Captain(object):
    
    def __init__(self):
        self.cache = []
        self.member_list = {}

    def accept_report(self, id, report):
        if id not in self.member_list:
            return jsonify(msg='the sergeant is not my soldier'), 403

        self.cache.append({'sgt_id':id, 'work':report})
        logger.info('accept work from sgt: {0}'.format(id))
        return jsonify(result='success')

    def accept_sgt(self, info):
        new_id = str(id(info))
        self.member_list[new_id] = {'info':info}
        logger.info('accept a new sergeant: {0}, {1}'.format(info['name'], id))
        return jsonify(result='success', name=info['name'], id=new_id)

    def show_cache(self):
        return jsonify(cache = self.cache)


# REST interface ---------------------------------------------------------------

app = Captain()
server = Flask(__name__)


@server.route('/sgt/join', methods=['POST'])
def sgt_join():
    input = get_dict()
    if input[1] != 200: return input

    res = app.accept_sgt(input[0])
    return res

@server.route('/sgt/<id>/report', methods=['POST'])
def sgt_report(id):
    input = get_dict()
    if input[1] != 200: return input

    res = app.accept_report(id, input[0])
    return res

@server.route('/dev/cache', methods=['GET'])
def dev_cache():
    return app.show_cache()


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 5100
    server.run(port=port, debug=True)
