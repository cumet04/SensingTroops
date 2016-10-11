import argparse
import json
import signal
from flask import render_template, jsonify, request
from flask_swagger import swagger
from logging import getLogger, StreamHandler, DEBUG, ERROR
from controller import LeaderServer
from model import definitions, Leader
from utils.helpers import DelegateHandler, get_ip, get_mac

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
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-N', '--name', type=str, default='', help='Target name of app')
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

    if params.id == "":
        params.id = get_mac()
    if params.name == "":
        params.name = "leader"

    host_addr = get_ip()
    ep = 'http://{0}:{1}{2}/'.format(host_addr, params.port, params.prefix)
    leader = Leader(params.id, params.name, ep)

    retry = 10
    for i in range(retry):
        if leader.awake(params.rec_addr, 30):
            logger.info('leader.awake succeeded.')
            break
        else:
            logger.error("leader.awake failed. retry after 20 seconds.")
            sleep(20)
    # FIXME: 全部失敗しても普通に処理が進行する
    
    LeaderServer.set_model(leader)

    @server.route(params.prefix + '/spec.json')
    def output_spec_json():
        spec_dict = swagger(server, template={'definitions': definitions})
        spec_dict['info']['title'] = 'SensingTroops'
        return jsonify(spec_dict)

    @server.route(params.prefix + '/spec.html')
    def spec_html():
        return render_template('swagger_ui.html')

    # エラーログ送信用ログハンドラ
    error_handler = DelegateHandler(leader.submit_error)
    error_handler.setLevel(ERROR)
    getLogger("model").addHandler(error_handler)

    # 強制終了のハンドラ
    original_shutdown = signal.getsignal(signal.SIGINT)
    def shutdown(signum, frame):
        leader.shutdown()
        original_shutdown(signum, frame)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    server.debug = True
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
