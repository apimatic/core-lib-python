
class EndpointLogger:

    def __init__(self, logger=None):
        self._logger = logger
        self._endpoint_name = None

    def info(self, info_message):
        if self._logger:
            self._logger.info(info_message)

    def debug(self, debug_message):
        if self._logger:
            self._logger.debug(debug_message)

    def error(self, error_message, exc_info=True):
        if self._logger:
            self._logger.error(self, error_message, exc_info)