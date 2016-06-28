import argparse
import hashlib
import utils.current_viewer.troops_viewer as tr_viewer
import utils.current_viewer.values_viewer as vl_viewer
from flask import render_template, jsonify, Flask, request, make_response
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


server = Flask(__name__)
rec_addr = "http://localhost:50000/recruiter/"


@server.route('/troops.html', methods=['GET'])
def show_troops():
    return render_template('troops_viewer.html')


@server.route('/troops.json', methods=['GET'])
def troops_json():
    data = tr_viewer.generate_data(rec_addr)

    m = hashlib.md5()
    m.update(str(data).encode())
    etag = m.hexdigest()
    if_none_match = str(request.if_none_match)[1:-1]  # ダブルクォートを削除
    if etag == if_none_match:
        return make_response(), 304

    response = jsonify(data=tr_viewer.generate_data(rec_addr))
    response.set_etag(etag)
    return response


@server.route('/values.html', methods=['GET'])
def show_values():
    return render_template('values_viewer.html')


@server.route('/values/<name>', methods=['GET'])
def values_data(name):
    data_func = getattr(vl_viewer, "get_{0}_data".format(name))
    return jsonify(values=data_func())


if __name__ == "__main__":
    # param setting
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-P', '--port', type=int, default=50010, help='port')
    params = parser.parse_args()

    server.debug = True
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
