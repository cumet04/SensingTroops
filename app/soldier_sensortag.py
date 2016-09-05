import argparse
import time
import traceback
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


class TagReader():
    def __init__(self, addr):
        self.addr = addr
        Thread(target= self.sensing, daemon=True).start()

    def sensing(self):
        while True:
            logger.info("a sensing is going to be tried in 5sec...")
            time.sleep(5)

            self.values = {
                "brightness": 0,
                "temperature": 0,
                "target_temp": 0,
                "humidity": 0,
                "humi_temp": 0,
                "barometer": 0,
                "baro_temp": 0,
                "accelerometer": [0, 0, 0],
                "magnetometer": [0, 0, 0],
                "gyroscope": [0, 0, 0],
            }

            try:
                self.tag = self.connect()
                if self.tag is None:
                    continue

                if not self.enable_sensors():
                    continue

                if not self.poll_values():
                    continue
            except:
                logger.fatal("unknow error is occured")
                logger.fatal(traceback.format_exc())

    def connect(self):
        try:
            tag = SensorTag(self.addr)
            return tag
        except BTLEException as e:
            if "Failed to connect to peripheral" in e.message:
                logger.error("connection failed: {0}".format(self.addr))
                return None
            raise

    def enable_sensors(self):
        try:
            self.tag.IRtemperature.enable()
            self.tag.humidity.enable()
            self.tag.barometer.enable()
            self.tag.accelerometer.enable()
            self.tag.magnetometer.enable()
            self.tag.gyroscope.enable()
            self.tag.lightmeter.enable()
        except BTLEException as e:
            logger.info("Disconnected: {0} in enable".format(self.addr))
            logger.error(traceback.format_exc())
            return False
        return True

    def poll_values(self):
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
            except BTLEException:
                logger.info("Disconnected: {0}".format(self.tag.addr))
                break


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

    soldier = Soldier("CC2650-" + addr, "SensorTag")
    soldier.weapons.update(tag_weapons)
    if not soldier.awake(rec_addr, 10):
        soldier.shutdown()
    return reader, soldier


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/recruiter/")
    parser.add_argument(
        '-T', '--tag_addr', type=str, help="sensortag's MAC addr")
    params = parser.parse_args()
    rec_addr = params.rec_addr
    tag_addr = params.tag_addr


    reader = TagReader(tag_addr)
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

    soldier = Soldier("CC2650-" + tag_addr, "SensorTag")
    soldier.weapons.update(tag_weapons)
    if not soldier.awake(rec_addr, 10):
        soldier.shutdown()
