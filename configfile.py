import json
# import os
# import sys
import io

class Config(object):
    def loadconfig(self, conf_name):
        try:
            conf_file = open(conf_name, 'r')
            conf_dict = json.loads(conf_file.read())
        except IOError as e:
            print("loadconfig failed : file open failed")
            return False
        for name, value in conf_dict.items():
            self.__dict__[name] = value
