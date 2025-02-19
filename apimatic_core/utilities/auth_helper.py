import base64
import calendar
from datetime import datetime
from typing import Callable, Dict, Optional, Union, Any
from pydantic import validate_call


class AuthHelper:
    @staticmethod
    @validate_call
    def get_base64_encoded_value(*props: str, delimiter: str = ':') -> Optional[str]:
        if props and not any(prop is None for prop in props):
            joined = delimiter.join(props)
            encoded = base64.b64encode(str.encode(joined)).decode('iso-8859-1')
            return encoded
        return None

    @staticmethod
    @validate_call
    def get_token_expiry(current_timestamp: int, expires_in: Union[int, str]) -> int:
        return current_timestamp + int(expires_in)

    @staticmethod
    @validate_call
    def get_current_utc_timestamp() -> int:
        return calendar.timegm(datetime.now().utctimetuple())

    @staticmethod
    @validate_call
    def is_token_expired(token_expiry: int, clock_skew_time: Optional[int] = None) -> bool:
        """
        Checks if OAuth token has expired.

        Returns:
            bool: True if token has expired, False otherwise.
        """
        if clock_skew_time is not None:
            token_expiry -= clock_skew_time
        utc_now = AuthHelper.get_current_utc_timestamp()
        return token_expiry < utc_now

    @staticmethod
    @validate_call
    def is_valid_auth(auth_params: Dict[str, Any]) -> bool:
        return bool(auth_params and all(param and auth_params[param] for param in auth_params))

    @staticmethod
    @validate_call
    def apply(auth_params: Dict[str, Any], func: Callable[[str, Any], None]) -> None:
        for param, value in auth_params.items():
            func(param, value)