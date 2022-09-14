import base64
import calendar
from datetime import datetime


class AuthHelper:

    @staticmethod
    def apply_base64_encoding(username, password, delimiter=':'):
        if username and password:
            joined = "{}{}{}".format(username, delimiter, password)
            encoded = base64.b64encode(str.encode(joined)).decode('iso-8859-1')
            return encoded

    @staticmethod
    def set_token_expiry(token):
        if hasattr(token, 'expires_in'):
            utc_now = calendar.timegm(datetime.now().utctimetuple())
            token.expiry = (utc_now + int(token.expires_in))

    @staticmethod
    def is_token_expired(token):
        """ Checks if OAuth token has expired.

        Returns:
            bool: True if token has expired, False otherwise.

        """
        utc_now = calendar.timegm(datetime.now().utctimetuple())
        return hasattr(token, 'expiry') and token.expiry is not None and token.expiry < utc_now
