import argparse
import json
from logging import getLogger, StreamHandler, DEBUG
from flask import render_template, jsonify
from flask_cors import cross_origin
from flask_swagger import swagger
from controller import CommanderServer
from model import definitions
from model.commander import Commander

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--spec', action="store_true", help='output spec.json and exit')
    parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    parser.add_argument(
        '-P', '--port', type=int, default=50001, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/commander', help='url prefix')
    params = parser.parse_args()


    server = CommanderServer.generate_server(params.prefix)

    if params.spec:
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        print(json.dumps(spec_dict, sort_keys=True, indent=2))
        exit()

    ep = 'http://localhost:{0}{1}/'.format(params.port, params.prefix)
    commander = Commander(params.id, params.name, ep)
    commander.awake('http://localhost:50000/recruiter/')
    CommanderServer.set_model(commander)

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
