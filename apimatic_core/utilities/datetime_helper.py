from datetime import datetime, date
from apimatic_core.types.datetime_format import DateTimeFormat
from apimatic_core.utilities.api_helper import ApiHelper


class DateTimeHelper:

    @staticmethod
    def validate_datetime(datetime_value, datetime_format):
        if DateTimeFormat.RFC3339_DATE_TIME == datetime_format:
            return DateTimeHelper.is_rfc_3339(datetime_value)
        elif DateTimeFormat.UNIX_DATE_TIME == datetime_format:
            return DateTimeHelper.is_unix_timestamp(datetime_value)
        elif DateTimeFormat.HTTP_DATE_TIME == datetime_format:
            return DateTimeHelper.is_rfc_1123(datetime_value)

        return False

    @staticmethod
    def validate_date(date_value):
        try:
            if isinstance(date_value, date):
                datetime.strptime(date_value.isoformat(), "%Y-%m-%d")
                return True
            elif isinstance(date_value, str):
                datetime.strptime(date_value, "%Y-%m-%d")
                return True
            else:
                return False
        except ValueError:
            return False

    @staticmethod
    def is_rfc_1123(datetime_value):
        try:
            datetime.strptime(datetime_value, "%a, %d %b %Y %H:%M:%S %Z")
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    def is_rfc_3339(datetime_value):
        try:
            if '.' in datetime_value:
                datetime_value = datetime_value[:datetime_value.rindex('.')]
            datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M:%S")
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    def is_unix_timestamp(timestamp):
        try:
            datetime.fromtimestamp(float(timestamp))
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    def to_rfc3339_date_time(value):
        if value is None:
            return None

        date_time: ApiHelper.CustomDate = ApiHelper.apply_datetime_converter(value, ApiHelper.RFC3339DateTime)
        return DateTimeHelper._convert(date_time)

    @staticmethod
    def to_rfc1123_date_time(value):
        if value is None:
            return None

        date_time: ApiHelper.CustomDate = ApiHelper.apply_datetime_converter(value, ApiHelper.HttpDateTime)
        return DateTimeHelper._convert(date_time)

    @staticmethod
    def to_unix_timestamp(value):
        if value is None:
            return None

        date_time: ApiHelper.CustomDate = ApiHelper.apply_datetime_converter(value, ApiHelper.UnixDateTime)
        return DateTimeHelper._convert(date_time)

    @staticmethod
    def _convert(date_time):
        if date_time is None:
            return None

        if isinstance(date_time, list):
            return [DateTimeHelper._convert(element) for element in date_time]

        if isinstance(date_time, dict):
            return {key: DateTimeHelper._convert(element) for key, element in date_time.items()}

        return date_time.value

    @staticmethod
    def try_parse_from_rfc3339_date_time(value):
        if value is None:
            return None

        if isinstance(value, list):
            return [DateTimeHelper.try_parse_from_rfc3339_date_time(element) for element in value]

        if isinstance(value, dict):
            return {key: DateTimeHelper.try_parse_from_rfc3339_date_time(element) for key, element in value.items()}

        if isinstance(value, datetime):
            return value

        return ApiHelper.RFC3339DateTime.from_value(value).datetime

    @staticmethod
    def try_parse_from_rfc1123_date_time(value):
        if value is None:
            return None

        if isinstance(value, list):
            return [DateTimeHelper.try_parse_from_rfc1123_date_time(element) for element in value]

        if isinstance(value, dict):
            return {key: DateTimeHelper.try_parse_from_rfc1123_date_time(element) for key, element in value.items()}

        if isinstance(value, datetime):
            return value

        return ApiHelper.HttpDateTime.from_value(value).datetime

    @staticmethod
    def try_parse_from_unix_timestamp(value):
        if value is None:
            return None

        if isinstance(value, list):
            return [DateTimeHelper.try_parse_from_unix_timestamp(element) for element in value]

        if isinstance(value, dict):
            return {key: DateTimeHelper.try_parse_from_unix_timestamp(element) for key, element in value.items()}

        if isinstance(value, datetime):
            return value

        return ApiHelper.UnixDateTime.from_value(value).datetime
