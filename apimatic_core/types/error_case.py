
class ErrorCase:

    def get_error_message(self):
        return self._error_message

    def get_error_message_template(self):
        return self._error_message_template

    def get_exception_type(self):
        return self._exception_type

    def is_error_message_template(self):
        return True if self._error_message_template else False

    def __init__(self):
        self._error_message = None
        self._error_message_template = None
        self._exception_type = None

    def error_message(self, error_message):
        self._error_message = error_message
        return self

    def error_message_template(self, error_message_template):
        self._error_message_template = error_message_template
        return self

    def exception_type(self, exception_type):
        self._exception_type = exception_type
        return self
