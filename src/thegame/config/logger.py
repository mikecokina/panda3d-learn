import logging


def setup_logging(loglevel):
    logging.basicConfig(level=getattr(logging, str(loglevel).upper()),
                        format='%(asctime)s : [%(levelname)s] : %(name)s : %(message)s')


def getLogger(name, suppress=False, loglevel="INFO"):
    setup_logging(loglevel)
    return logging.getLogger(name=name) if not suppress else Logger(name)


def getPersistentLogger(name, loglevel="INFO"):
    setup_logging(loglevel)
    return logging.getLogger(name=name)


class Logger(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name

    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def warn(self, *args, **kwargs):
        pass
