#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import json
from flask_cors import cross_origin
from flask import Flask, jsonify, request, render_template
from flask_swagger import swagger
from logging import getLogger, StreamHandler, DEBUG

import commander
import leader
import recruiter
from objects import definitions

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def gen_spec():
    """
    swagger-specのdictを生成する
    :return dict: swagger-specのjsonになるdict
    """
    spec_dict = swagger(parent, template={'definitions': definitions})
    spec_dict['info']['title'] = 'SensingTroops'
    return spec_dict
    

@cross_origin()
def spec():
    return jsonify(gen_spec())


def spec_html():
    return render_template('swagger_ui.html',
                           spec_url=url_prefix + '/spec.json')


# entry point ------------------------------------------------------------------
if __name__ == "__main__":
    # parameter set / parse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest='command', help='sub-command help')
    s_parser = subparsers.add_parser(
        'spec', help='output swagger-spec (json)')
    s_parser.add_argument(
        'target', metavar='target', type=str, help='Target name of spec')
    r_parser = subparsers.add_parser(
        'run', help='run server')
    r_parser.add_argument(
        'target', metavar='class', type=str, help='Target class of server')
    r_parser.add_argument(
        'id', metavar='id', type=str, help='Target id of app')
    r_parser.add_argument(
        'name', metavar='name', type=str, help='Target name of app')
    r_parser.add_argument(
        '-P', '--port', type=int, default=50000, help='port')
    args = parser.parse_args()

    # set target app's params
    url_prefix = '/' + args.target
    server = None
    if args.target == 'commander':
        server = commander.server
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            # flaskのuse_reloader=Trueのときの二重起動対策
            ep = 'http://localhost:{0}{1}'.format(args.port, url_prefix)
            commander.initialize_app(args.id, args.name, ep)
    elif args.target == 'leader':
        server = leader.server
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            ep = 'http://localhost:{0}{1}'.format(args.port, url_prefix)
            leader.initialize_app(args.id, args.name, ep)
    elif args.target == 'recruiter':
        server = recruiter.server
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            config_path = '{0}/recruit.yml'.format(os.path.dirname(__file__))
            recruiter.initialize_app(config_path)
    else:
        logger.error('unknown target: {0}'.format(args.target))
        exit()
    server.add_url_rule('/spec.json', 'spec_json', spec)
    server.add_url_rule('/spec.html', 'spec_html', spec_html)

    # register app
    parent = Flask(__name__)
    parent.register_blueprint(server, url_prefix=url_prefix)

    # command: spec
    if args.command == 'spec':
        print(json.dumps(gen_spec()))
        exit()
    elif args.command == 'run':
        parent.debug = True
        parent.run(host='0.0.0.0', port=args.port,
                   use_debugger=True, use_reloader=True)
    else:
        logger.error('unknown command: {0}'.format(args.command))
        exit()
