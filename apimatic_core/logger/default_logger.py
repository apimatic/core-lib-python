import sys

from apimatic_core_interfaces.logger.logger import Logger
from pythonjsonlogger import jsonlogger
import logging


class ConsoleLogger(Logger):

    def __init__(self):
        self._logger = logging.Logger(name='')
        stdout = logging.StreamHandler(stream=sys.stdout)
        fmt = jsonlogger.JsonFormatter(
            "%(asctime)s [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ"
        )
        stdout.setFormatter(fmt)
        self._logger.addHandler(stdout)

    def log(self, level, message, params):
        """Logs a message with a specified log level and additional parameters.

        Args:
            level (int): The log level of the message.
            message (str): The message to log.
            params (dict): Additional parameters to include in the log message.
        """
        self._logger.log(level, message, extra=params)
        pass
