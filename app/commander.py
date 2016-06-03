import argparse
from logging import getLogger, StreamHandler, DEBUG
from flask import render_template, jsonify
from flask_cors import cross_origin
from flask_swagger import swagger
from controller import CommanderServer
from model import definitions
from model.commander import Commander
from utils.recruiter_client import RecruiterClient

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    parser.add_argument(
        '-P', '--port', type=int, default=50001, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/leader', help='url prefix')
    params = parser.parse_args()

    ep = 'http://localhost:{0}{1}/'.format(params.port, params.prefix)
    commander = Commander(params.id, params.name, ep)
    commander.awake(RecruiterClient.gen_rest_client(
        'http://localhost:50000/recruiter/'))
    CommanderServer.set_model(commander)

    server = CommanderServer.generate_server(params.prefix)

    @server.route(params.prefix + '/spec.json')
    @cross_origin()
    def spec_json():
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        return jsonify(spec_dict)

    @server.route(params.prefix + '/spec.html')
    def spec_html():
        return render_template('swagger_ui.html')

    server.debug = True
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
