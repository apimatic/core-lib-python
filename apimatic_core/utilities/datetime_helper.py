from datetime import datetime, date
from typing import Optional, Union, List, Dict

from apimatic_core_interfaces.formats.datetime_format import DateTimeFormat
from pydantic import validate_call
from apimatic_core.utilities.api_helper import ApiHelper


class DateTimeHelper:
    @staticmethod
    @validate_call
    def validate_datetime(datetime_value: Union[str, float, int], datetime_format: Optional[DateTimeFormat]) -> bool:
        if datetime_format is None:
            return False

        """Validate datetime string against a given format."""
        if datetime_format == DateTimeFormat.RFC3339_DATE_TIME:
            return DateTimeHelper.is_rfc_3339(str(datetime_value))
        elif datetime_format == DateTimeFormat.UNIX_DATE_TIME:
            return DateTimeHelper.is_unix_timestamp(datetime_value)
        elif datetime_format == DateTimeFormat.HTTP_DATE_TIME:
            return DateTimeHelper.is_rfc_1123(str(datetime_value))
        return False

    @staticmethod
    @validate_call
    def validate_date(date_value: Union[str, date]) -> bool:
        """Validate a date string or `date` object."""
        try:
            if isinstance(date_value, date):
                datetime.strptime(date_value.isoformat(), "%Y-%m-%d")
            elif isinstance(date_value, str):
                datetime.strptime(date_value, "%Y-%m-%d")
            else:
                return False
            return True
        except ValueError:
            return False

    @staticmethod
    @validate_call
    def is_rfc_1123(datetime_value: str) -> bool:
        """Check if the string is in RFC 1123 format."""
        try:
            datetime.strptime(datetime_value, "%a, %d %b %Y %H:%M:%S %Z")
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    @validate_call
    def is_rfc_3339(datetime_value: str) -> bool:
        """Check if the string is in RFC 3339 format."""
        try:
            if "." in datetime_value:
                datetime_value = datetime_value[:datetime_value.rindex(".")]
            datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M:%S")
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    @validate_call
    def is_unix_timestamp(timestamp: Union[str, int, float]) -> bool:
        """Check if the value is a valid Unix timestamp."""
        try:
            datetime.fromtimestamp(float(timestamp))
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    def to_rfc3339_date_time(
        value: Union[None, List[datetime], Dict[str, datetime], datetime]
    ) -> Union[None, str, List[str], Dict[str, str]]:
        """Convert datetime values to RFC 3339 format."""
        if value is None:
            return None
        date_time = ApiHelper.apply_datetime_converter(value, ApiHelper.RFC3339DateTime)
        return DateTimeHelper._convert_to_rfc3339(date_time)

    @staticmethod
    def _convert_to_rfc3339(
        date_time: Union[None, ApiHelper.CustomDate, List[ApiHelper.CustomDate], Dict[str, ApiHelper.CustomDate]]
    ) -> Union[None, str, List[str], Dict[str, str]]:
        """Convert CustomDate objects to RFC 3339 strings."""
        if date_time is None:
            return None
        if isinstance(date_time, ApiHelper.CustomDate):
            return str(date_time.value)
        if isinstance(date_time, list):
            return [DateTimeHelper._convert_to_rfc3339(element) for element in date_time] # type: ignore[misc]
        if isinstance(date_time, dict):
            return {key: DateTimeHelper._convert_to_rfc3339(value) for key, value in date_time.items()} # type: ignore[misc]
        raise TypeError("Unsupported type for RFC 3339 conversion")

    @staticmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    def to_rfc1123_date_time(
            value: Union[None, List[datetime], Dict[str, datetime], datetime]
    ) -> Union[None, str, List[str], Dict[str, str]]:
        """Convert datetime values to RFC 1123 format."""
        if value is None:
            return None
        date_time = ApiHelper.apply_datetime_converter(value, ApiHelper.HttpDateTime)
        return DateTimeHelper._convert_to_rfc1123(date_time)

    @staticmethod
    def _convert_to_rfc1123(
            date_time: Union[None, ApiHelper.CustomDate, List[ApiHelper.CustomDate], Dict[str, ApiHelper.CustomDate]]
    ) -> Union[None, str, List[str], Dict[str, str]]:
        """Convert CustomDate objects to RFC 1123 strings."""
        if date_time is None:
            return None
        if isinstance(date_time, ApiHelper.CustomDate):
            return str(date_time.value)
        if isinstance(date_time, list):
            return [DateTimeHelper._convert_to_rfc1123(element) for element in date_time] # type: ignore[misc]
        if isinstance(date_time, dict):
            return {key: DateTimeHelper._convert_to_rfc1123(value) for key, value in date_time.items()} # type: ignore[misc]
        raise TypeError("Unsupported type for RFC 3339 conversion")

    @staticmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    def to_unix_timestamp(
        value: Union[None, List[datetime], Dict[str, datetime], datetime]
    ) -> Union[None, float, List[float], Dict[str, float]]:
        """Convert datetime values to Unix timestamps."""
        if value is None:
            return None
        date_time = ApiHelper.apply_datetime_converter(value, ApiHelper.UnixDateTime)
        return DateTimeHelper._convert_to_unix(date_time)

    @staticmethod
    def _convert_to_unix(
        date_time: Union[None, ApiHelper.CustomDate, List[ApiHelper.CustomDate], Dict[str, ApiHelper.CustomDate]]
    ) -> Union[None, float, List[float], Dict[str, float]]:
        """Convert CustomDate objects to Unix timestamps."""
        if date_time is None:
            return None
        if isinstance(date_time, ApiHelper.CustomDate):
            return float(date_time.value)
        if isinstance(date_time, list):
            return [DateTimeHelper._convert_to_unix(element) for element in date_time] # type: ignore[misc]
        if isinstance(date_time, dict):
            return {key: DateTimeHelper._convert_to_unix(value) for key, value in date_time.items()} # type: ignore[misc]
        raise TypeError("Unsupported type for Unix timestamp conversion")

    @staticmethod
    @validate_call
    def try_parse_from_rfc3339_date_time(
        value: Optional[Union[str, datetime, List[Union[str, datetime]], Dict[str, Union[str, datetime]]]]
    ) -> Optional[Union[datetime, List[datetime], Dict[str, datetime]]]:
        """Parse RFC 3339 strings into datetime objects."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value

        if isinstance(value, list):
            return [DateTimeHelper.try_parse_from_rfc3339_date_time(element) for element in value] # type: ignore[misc]
        if isinstance(value, dict):
            return {key: DateTimeHelper.try_parse_from_rfc3339_date_time(element) for key, element in value.items()} # type: ignore[misc]
        return ApiHelper.RFC3339DateTime.from_value(value).datetime

    @staticmethod
    @validate_call
    def try_parse_from_rfc1123_date_time(
        value: Optional[Union[str, datetime, List[Union[str, datetime]], Dict[str, Union[str, datetime]]]]
    ) -> Optional[Union[datetime, List[datetime], Dict[str, datetime]]]:
        """Parse RFC 1123 strings into datetime objects."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value

        if isinstance(value, list):
            return [DateTimeHelper.try_parse_from_rfc1123_date_time(element) for element in value] # type: ignore[misc]
        if isinstance(value, dict):
            return {key: DateTimeHelper.try_parse_from_rfc1123_date_time(element) for key, element in value.items()} # type: ignore[misc]
        return ApiHelper.HttpDateTime.from_value(value).datetime

    @staticmethod
    @validate_call
    def try_parse_from_unix_timestamp(
        value: Optional[
            Union[int, float, datetime, List[Union[int, float, datetime]], Dict[str, Union[int, float, datetime]]]
        ]
    ) -> Optional[Union[datetime, List[datetime], Dict[str, datetime]]]:
        """Parse Unix timestamps into datetime objects."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value

        if isinstance(value, list):
            return [DateTimeHelper.try_parse_from_unix_timestamp(element) for element in value] # type: ignore[misc]
        if isinstance(value, dict):
            return {key: DateTimeHelper.try_parse_from_unix_timestamp(element) for key, element in value.items()} # type: ignore[misc]
        return datetime.fromtimestamp(float(value))
