import json
import os
import sys
import threading

from flask import Flask, jsonify, request, url_for, abort, Response

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/module')
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


class Sensor():
    def __init__(self):
        self.sensor_values = {}
        self.sensor_values['brightness'] = 400
        self.sensor_values['button'] = True
        self.sensor_values['mpltemp'] = 20
        self.sensor_values['pressure'] = 1024
        self.sensor_values['humidity'] = 40
        self.sensor_values['temprature'] = 20
        self.sensor_values['currentpir'] = True
        self.sensor_values['pircount'] = 27

    def json_value(self, sensor):
        if sensor == 'all':
            result = []
            for s, v in self.sensor_values.items():
                result.append({'name': s, 'value': v})
            return result

        if sensor in self.sensor_values:
            result = {'name': sensor, 'value': self.sensor_values[sensor]}
            return result

        return None


logger = Logger(__name__, DEBUG)
flask = Flask(__name__)
sensorbox = Sensor()

# Web API functions ------------------------------------------------------------

@flask.route('/sensor/<path>', methods=['GET', 'POST'])
def get_sensor(path):
    result = sensorbox.json_value(path)
    if result is None: abort(404)

    res_str = json.dumps(result, sort_keys=True, indent = 2)
    return Response(res_str,  mimetype='application/json')


# entry point ------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 5000
    flask.run(port=port)
