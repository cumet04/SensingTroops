import argparse
import time
from bluepy.sensortag import SensorTag
from bluepy.btle import Scanner, ScanEntry,DefaultDelegate, BTLEException
from model.soldier import Soldier
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class TagValues():
    def __init__(self, tag: SensorTag):
        self.tag = tag

    def brightness(self):
        try:
            return (self.tag.lightmeter.read(), "lux")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def temperature(self):
        try:
            return (self.tag.IRtemperature.read()[0], "degC")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def target_temp(self):
        try:
            return (self.tag.IRtemperature.read()[1], "degC")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def humidity(self):
        try:
            return (self.tag.humidity.read()[1], "%")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def humi_temp(self):
        try:
            return (self.tag.humidity.read()[0], "degC")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def barometer(self):
        try:
            return (self.tag.barometer.read()[1], "mbar")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def baro_temp(self):
        try:
            return (self.tag.barometer.read()[0], "degC")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def accelerometer(self):
        try:
            return (self.tag.accelerometer.read(), "g")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def magnetometer(self):
        try:
            return (self.tag.magnetometer.read(), "uT")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)

    def gyroscope(self):
        try:
            return (self.tag.gyroscope.read(), "deg/sec")
        except:
            logger.info("Disconnected: {0}".format(self.tag.addr))
            self.tag = None
            return (None, None)


def connect(addr):
    logger.info("connecting: {0}".format(addr))
    try:
        tag = SensorTag(addr)
    except BTLEException as e:
        if "Failed to connect to peripheral" in e.message:
            logger.info("connection failed: {0}".format(addr))
            return None, None
        raise

    tag.IRtemperature.enable()
    tag.humidity.enable()
    tag.barometer.enable()
    tag.accelerometer.enable()
    tag.magnetometer.enable()
    tag.gyroscope.enable()
    tag.lightmeter.enable()
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
        if sol[0] is None or sol[0].tag is None:
            if sol[1] is not None:
                sol[1].shutdown()
            sol = connect(tags[0])

        sol = soldiers[tags[1]]
        if sol[0] is None or sol[0].tag is None:
            if sol[1] is not None:
                sol[1].shutdown()
            sol = connect(tags[1])

        time.sleep(5)

