import argparse
import asyncio
import struct
import time
import os
from bluepy.sensortag import SensorTag
from bluepy.btle import BTLEException, AssignedNumbers
from logging import getLogger, StreamHandler, DEBUG
from troops.soldier import SoldierBase, main, LOOP

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class SensorTagSoldier(SoldierBase):

    def __init__(self, addr, loop):
        super().__init__()
        self.enable_wait = 1  # wait seconds for enable sensor to read value
        self.addr = addr
        self.tag = None
        self.loop = loop

    def connect(self):
        try:
            self.tag = SensorTag(self.addr)
            return self.tag
        except BTLEException as e:
            if "Failed to connect to peripheral" in e.message:
                logger.error("connection failed: %s", self.addr)
                return None
            if "Device disconnected" in e.message:
                logger.error("Device disconnected: %s", self.addr)
                return None
            raise

    async def brightness(self):
        try:
            self.tag.lightmeter.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.lightmeter.read()
            self.tag.lightmeter.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "lux"

    async def temperature(self):
        try:
            self.tag.IRtemperature.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.IRtemperature.read()[0]
            self.tag.IRtemperature.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "degC"

    async def target_temp(self):
        try:
            self.tag.IRtemperature.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.IRtemperature.read()[1]
            self.tag.IRtemperature.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "degC"

    async def humidity(self):
        try:
            self.tag.humidity.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.humidity.read()[1]
            self.tag.humidity.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "%"

    async def humi_temp(self):
        try:
            self.tag.humidity.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.humidity.read()[0]
            self.tag.humidity.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "degC"

    async def barometer(self):
        try:
            self.tag.barometer.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.barometer.read()[1]
            self.tag.barometer.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "mbar"

    async def baro_temp(self):
        try:
            self.tag.barometer.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.barometer.read()[0]
            self.tag.barometer.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "degC"

    async def accelerometer(self):
        try:
            self.tag.accelerometer.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.accelerometer.read()
            self.tag.accelerometer.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "g"

    async def magnetometer(self):
        try:
            self.tag.magnetometer.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.magnetometer.read()
            self.tag.magnetometer.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "uT"

    async def gyroscope(self):
        try:
            self.tag.gyroscope.enable()
            await asyncio.sleep(self.enable_wait, loop=self.loop)
            val = self.tag.gyroscope.read()
            self.tag.gyroscope.disable()
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "deg/sec"

    async def battery(self):
        try:
            # AssignedNumbersは実行時にjsonファイルからメンバを読むので
            # linterなどがエラーを吐く場合があるが実際には問題ない
            b_uuid = AssignedNumbers.battery_level
            chara = self.tag.getCharacteristics(uuid=b_uuid)[0]
            val = struct.unpack('b', chara.read())[0]
        except BTLEException:
            logger.error("failed to read value: %s", self.addr)
            return None, None
        return val, "%"


if __name__ == "__main__":
    # read args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I', '--id', type=str, default='', help='Target id of app')
    parser.add_argument(
        '-P', '--port', type=int, default=53000, help="rpc-server's port num")
    parser.add_argument(
        '-R', '--rec_addr', type=str, help="recruiter url",
        default="http://localhost:50000/")
    parser.add_argument(
        '-T', '--tag_addr', type=str, help="sensortag's MAC addr")
    params = parser.parse_args()

    s = SensorTagSoldier(params.tag_addr, LOOP)
    if s.connect() is None:
        logger.error("failed to connect to SensorTag. retry after 10 seconds.")
        time.sleep(10)
        os._exit(1)

    r = main(s, params.port, params.id, params.rec_addr)
    if r is not None:
        logger.error('soldier failed: ' + r)
