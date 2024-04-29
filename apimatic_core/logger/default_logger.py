import sys

from apimatic_core_interfaces.logger.Logger import Logger
import logging


class ConsoleLogger(Logger):

    def __init__(self):
        self._logger = logging.Logger(name='')
        stdout = logging.StreamHandler(stream=sys.stdout)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s",
                                datefmt="%Y-%m-%dT%H:%M:%SZ")
        stdout.setFormatter(fmt)
        self._logger.addHandler(stdout)

    def log(self, level, message, params):
        self._logger.log(level, message, params)
        pass
