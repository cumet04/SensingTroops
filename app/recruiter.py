import os
import argparse
import json
from logging import getLogger, StreamHandler, DEBUG
from flask_swagger import swagger
from flask_cors import cross_origin
from flask import jsonify, render_template
from controller import RecruiterServer
from model import definitions, Recruiter

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
        '-P', '--port', type=int, default=50000, help='port')
    parser.add_argument(
        '-F', '--prefix', type=str, default='/recruiter', help='url prefix')
    params = parser.parse_args()

    # server setting
    server = RecruiterServer.generate_server(params.prefix)

    if params.spec:
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        print(json.dumps(spec_dict, sort_keys=True, indent=2))
        exit()

    config = '{0}/../config/recruit.yml'.format(os.path.dirname(__file__))
    recruiter = Recruiter(config)
    RecruiterServer.set_model(recruiter)

    @server.route(params.prefix + '/spec.json')
    @cross_origin()
    def output_spec_json():
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        return jsonify(spec_dict)

    @server.route(params.prefix + '/spec.html')
    def output_spec_html():
        return render_template('swagger_ui.html')

    server.debug = True
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
