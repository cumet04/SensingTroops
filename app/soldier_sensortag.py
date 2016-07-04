import argparse
import time
from bluepy.sensortag import SensorTag
from bluepy.btle import Scanner, ScanEntry,DefaultDelegate, BTLEException
from model.soldier import Soldier
from logging import getLogger, StreamHandler, DEBUG
from threading import Thread

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class TagValues():
    def __init__(self, tag: SensorTag):
        self.tag = tag
        self.values = {
            "brightness": None,
            "temperature": None,
            "target_temp": None,
            "humidity": None,
            "humi_temp": None,
            "barometer": None,
            "baro_temp": None,
            "accelerometer": None,
            "magnetometer": None,
            "gyroscope": None,
        }
        Thread(target=self.get_values, daemon=True).start()

    def get_values(self):
        wait = 1
        while True:
            try:
                time.sleep(wait)
                self.values["brightness"] = self.tag.lightmeter.read()
                time.sleep(wait)
                self.values["temperature"], self.values["target_temp"] = \
                    self.tag.IRtemperature.read()
                time.sleep(wait)
                self.values["humi_temp"], self.values["humidity"] = \
                    self.tag.humidity.read()
                time.sleep(wait)
                self.values["baro_temp"], self.values["barometer"] = \
                    self.tag.barometer.read()
                time.sleep(wait)
                self.values["accelerometer"] = self.tag.accelerometer.read()
                time.sleep(wait)
                self.values["magnetometer"] = self.tag.magnetometer.read()
                time.sleep(wait)
                self.values["gyroscope"] = self.tag.gyroscope.read()
            except:
                logger.info("Disconnected: {0}".format(self.tag.addr))
                self.tag = None
                self.values = {
                    "brightness": None,
                    "temperature": None,
                    "target_temp": None,
                    "humidity": None,
                    "humi_temp": None,
                    "barometer": None,
                    "baro_temp": None,
                    "accelerometer": None,
                    "magnetometer": None,
                    "gyroscope": None,
                }
                return

    def brightness(self):
        return (self.values["brightness"], "lux")

    def temperature(self):
        return (self.values["temperature"], "degC")

    def target_temp(self):
        return (self.values["target_temp"], "degC")

    def humidity(self):
        return (self.values["humidity"], "%")

    def humi_temp(self):
        return (self.values["humi_temp"], "degC")

    def barometer(self):
        return (self.values["barometer"], "mbar")

    def baro_temp(self):
        return (self.values["baro_temp"], "degC")

    def accelerometer(self):
        return (self.values["accelerometer"], "g")

    def magnetometer(self):
        return (self.values["magnetometer"], "uT")

    def gyroscope(self):
        return (self.values["gyroscope"], "deg/sec")


def connect(addr):
    logger.info("connecting: {0}".format(addr))
    try:
        tag = SensorTag(addr)
    except BTLEException as e:
        if "Failed to connect to peripheral" in e.message:
            logger.info("connection failed: {0}".format(addr))
            return None, None
        raise
    logger.info("connected: {0}".format(addr))

    time.sleep(3)
    tag.IRtemperature.enable()
    tag.humidity.enable()
    tag.barometer.enable()
    tag.accelerometer.enable()
    tag.magnetometer.enable()
    tag.gyroscope.enable()
    tag.lightmeter.enable()
    time.sleep(10)
    reader = TagValues(tag)
    tag_weapons = {
        "temperature":   reader.temperature,
        "humidity":      reader.humidity,
        "barometer":     reader.barometer,
        "accelerometer": reader.accelerometer,
        "magnetometer":  reader.magnetometer,
        "gyroscope":     reader.gyroscope,
        "brightness":    reader.brightness,
        "target_temp":   reader.target_temp,
        "humi_temp":     reader.humi_temp,
        "baro_temp":     reader.baro_temp,
    }

    soldier = Soldier("CC2650-" + addr, "SensorTag")
    soldier.weapons.update(tag_weapons)
    if not soldier.awake(rec_addr, 10):
        soldier.shutdown()
    return reader, soldier


if __name__ == "__main__":
    global tags
    tags = []
    global rec_addr
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/recruiter/")
    params = parser.parse_args()
    rec_addr = params.rec_addr

    for line in open('/opt/tags.conf', 'r'):
        tags.append(line[:-1])
    print(tags)

    soldiers = {
        tags[0]: connect(tags[0]),
        tags[1]: connect(tags[1])
    }
    while True:
        sol = soldiers[tags[0]]
        if sol == (None, None) or sol[0].tag is None or not sol[1].is_alive():
            if sol[1] is not None:
                sol[1].shutdown()
            sol = connect(tags[0])

        sol = soldiers[tags[1]]
        if sol == (None, None) or sol[0].tag is None or not sol[1].is_alive():
            if sol[1] is not None:
                sol[1].shutdown()
            sol = connect(tags[1])

        time.sleep(10)
