import argparse
import json
from flask import render_template, jsonify, Blueprint, Flask
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


app = Blueprint('leader', __name__)
leader = None  # type: Leader


@app.route('/', methods=['GET'])
def get_info():
    return render_template('swagger_ui.html')


if __name__ == "__main__":
    # param setting
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-P', '--port', type=int, default=50002, help='port')
    params = parser.parse_args()

    # server setting
    server = Flask(__name__)
    server.register_blueprint(app)

    server.debug = True
    server.run(host='0.0.0.0', port=params.port, use_reloader=False)
