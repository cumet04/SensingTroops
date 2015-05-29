import json
# import os
# import sys
import io
from logger import Logger
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET

logger = Logger(__name__, DEBUG)

class Config(object):
    def __str__(self):
        result = "config object:"
        for name, value in self.__dict__.items():
            result += "\n - {0} : {1}".format(name, value)
        return result

    def loadfile(self, conf_name, params):
        logger.debug('loadfile : ' + conf_name)
        try:
            conf_file = open(conf_name, 'r')
            contents = conf_file.read()
            conf_dict = json.loads(contents)
        except IOError as e:
            print("loadconfig failed : file open failed")
            return False

        for name in params:
            if name in conf_dict:
                self.__dict__[name] = conf_dict[name]
            else:
                logger.error('Config.loadfile missing param: %s', name)
                return False
        return True

    def savefile(self, conf_name):
        logger.debug('savefile : ' + conf_name)

        conf_dict = {}
        for name in self.__dict__:
            conf_dict[name] = self.__dict__[name]
        json_string = json.dumps(conf_dict)
        logger.debug('savefile, write json : ' + json_string)

        try:
            conf_file = open(conf_name, 'w')
            conf_file.write(json_string)
        except IOError as e:
            print("loadconfig failed : file open failed")
            return False
        return True
