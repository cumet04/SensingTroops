import argparse
import json
import socket
from flask import render_template, jsonify
from flask_cors import cross_origin
from flask_swagger import swagger
from logging import getLogger, StreamHandler, DEBUG
from controller import LeaderServer
from model import definitions, Leader

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


if __name__ == "__main__":
    # param setting
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--spec', action="store_true", help='output spec.json and exit')
    parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    parser.add_argument(
        '-P', '--port', type=int, default=50002, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/leader', help='url prefix')
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/recruiter/")
    params = parser.parse_args()

    # server setting
    server = LeaderServer.generate_server(params.prefix)

    if params.spec:
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        print(json.dumps(spec_dict, sort_keys=True, indent=2))
        exit()

    host_addr = socket.gethostbyname(socket.gethostname())
    ep = 'http://{0}:{1}{2}/'.format(host_addr, params.port, params.prefix)
    leader = Leader(params.id, params.name, ep)
    leader.awake(params.rec_addr, 2)
    LeaderServer.set_model(leader)

    @server.route(params.prefix + '/spec.json')
    @cross_origin()
    def output_spec_json():
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        return jsonify(spec_dict)

    @server.route(params.prefix + '/spec.html')
    def spec_html():
        return render_template('swagger_ui.html')

    server.debug = True
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
