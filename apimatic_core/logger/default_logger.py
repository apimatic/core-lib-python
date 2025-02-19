import sys
from logging import StreamHandler, Formatter

from apimatic_core_interfaces.logger.logger import Logger
import logging

from pydantic import validate_call
from typing import Dict, Any


class ConsoleLogger(Logger):

    def __init__(self):
        self._logger: logging.Logger = logging.Logger(name='')
        stdout: StreamHandler = logging.StreamHandler(stream=sys.stdout)
        fmt: Formatter = logging.Formatter("%(levelname)s %(message)s")
        stdout.setFormatter(fmt)
        self._logger.addHandler(stdout)

    @validate_call
    def log(self, level: int, message: str, params: Dict[str, Any]):
        """Logs a message with a specified log level and additional parameters.

        Args:
            level (int): The log level of the message.
            message (str): The message to log.
            params (dict): Additional parameters to include in the log message.
        """
        self._logger.log(level, message, *params.values())
