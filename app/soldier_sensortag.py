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
        return self.tag.lightmeter.read()

    def temperature(self):
        return self.tag.IRtemperature.read()[0]

    def target_temp(self):
        return self.tag.IRtemperature.read()[1]

    def humidity(self):
        return self.tag.humidity.read()[1]

    def humi_temp(self):
        return self.tag.humidity.read()[0]

    def barometer(self):
        return self.tag.barometer.read()[1]

    def baro_temp(self):
        return self.tag.barometer.read()[0]

    def accelerometer(self):
        return self.tag.accelerometer.read()

    def magnetometer(self):
        return self.tag.magnetometer.read()

    def gyroscope(self):
        return self.tag.gyroscope.read()


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.soldiers = []

    def handleDiscovery(self, dev: ScanEntry, isNewDev, isNewData):
        name = str(dev.getValueText(9))  # 9 = Complete Local Name
        if not (isNewDev and "CC2650" in name):
            return

        logger.info("Tag is found: {0}".format(dev.addr))
        tag = SensorTag(dev.addr)
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

        soldier = Soldier("CC2650-" + dev.addr, name)
        soldier.weapons.update(tag_weapons)
        if not soldier.awake(rec_addr, 3):
            soldier.shutdown()


if __name__ == "__main__":
    global rec_addr
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/recruiter/")
    params = parser.parse_args()
    rec_addr = params.rec_addr

    scanner = Scanner().withDelegate(ScanDelegate())
    while True:
        try:
            logger.info("scanning ...")
            devices = scanner.scan(10.0)
        except BTLEException as e:
            if e.message != "Device disconnected" and \
                e.message != "Failed to connect to peripheral":
                    raise
