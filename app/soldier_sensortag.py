import argparse
from bluepy.sensortag import SensorTag
from bluepy.btle import Scanner, ScanEntry,DefaultDelegate, BTLEException
from model.soldier import Soldier
from utils.recruiter_client import RecruiterClient
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


tag = None  # type: SensorTag

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev: ScanEntry, isNewDev, isNewData):
        global tag
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
        tag_weapons = {
            "temperature":  tag.IRtemperature.read,
            "humidity":     tag.humidity.read,
            "barometer":    tag.barometer.read,
            "accelerometer":tag.accelerometer.read,
            "magnetometer": tag.magnetometer.read,
            "gyroscope":    tag.gyroscope.read,
            "brightness":   tag.lightmeter.read
        }

        soldier = Soldier("CC2650-" + dev.addr, "tag_soldier")
        soldier.weapons.update(tag_weapons)
        rec_client = RecruiterClient.gen_rest_client(
            'http://localhost:50000/recruiter/')
        soldier.awake(rec_client, 1)



if __name__ == "__main__":
    scanner = Scanner().withDelegate(ScanDelegate())
    try:
        devices = scanner.scan(10.0)
    except BTLEException as e:
        if e.message != "Device disconnected":
            raise

    while True:
        pass
