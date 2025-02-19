import logging

from apimatic_core_interfaces.logger.logger import Logger
from typing import Dict, Any

from pydantic import validate_call


class ApiLogger(Logger):
    logger: logging.Logger = logging.getLogger('mocked_logger')

    @validate_call
    def log(self, level: int, message: str, params: Dict[str, Any]):
        self.logger.log(level, message, *params.values())


