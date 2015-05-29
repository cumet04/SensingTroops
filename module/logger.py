from logging import getLogger,StreamHandler
from logging import CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


class Logger(object):
    def __init__(self, name, mode):
        self.logger = getLogger(name)
        handler = StreamHandler()
        handler.setLevel(mode)
        self.logger.setLevel(mode)
        self.logger.addHandler(handler)

    def debug(self, msg, *args, **kwargs):
        self.logger.log(DEBUG, msg, *args, **kwargs)
    def info(self, msg, *args, **kwargs):
        self.logger.log(INFO, msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs):
        self.logger.log(WARNING, msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self.logger.log(ERROR, msg, *args, **kwargs)
    def critical(self, msg, *args, **kwargs):
        self.logger.log(CRITICAL, msg, *args, **kwargs)


if __name__ == '__main__':
    log = Logger(DEBUG)
    log.debug("test no param")
    log.debug("test args: %s", "param1")
    d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
    log.debug("test kwargs: %s", "param2", extra=d)
