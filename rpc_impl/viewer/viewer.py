import argparse
import xmlrpc.client as xmlrpc_client
from flask import Flask, request, jsonify

server = Flask(__name__)


@server.route('/xmlrpc/exec', methods=['GET', 'POST'])
def exec_rpc():
    endpoint = ''
    method = ''
    params = []
    if request.method == 'GET':
        endpoint = request.args.get('endpoint', default='', type=str)
        method = request.args.get('method', default='', type=str)
        for i in range(1000):
            v = request.args.get('param%d' % i, default=None, type=str)
            if v is None:
                break
            # TODO: 必要に応じて数値へのキャスト
            params.append(v)
    elif request.method == 'POST':
        # TODO:
        pass
    if endpoint == '' or method == '':
        return "lack of parameter", 400

    client = xmlrpc_client.ServerProxy(endpoint)
    return jsonify(getattr(client, method)(*params))


@server.route('/xmlrpc/helps', methods=['GET'])
def exec_help():
    endpoint = request.args.get('endpoint', default='', type=str)
    if endpoint == '':
        return "lack of parameter", 400

    client = xmlrpc_client.ServerProxy(endpoint)
    helps = {}
    for name in client.system.listMethods():
        if "system." in name:
            continue
        helps[name] = client.system.methodHelp(name)
    return jsonify(helps)


if __name__ == "__main__":
    # param setting
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-P', '--port', type=int, default=50001, help='port')
    args = parser.parse_args()
    port = args.port

    server.debug = True
    server.run(host='0.0.0.0', port=port)
