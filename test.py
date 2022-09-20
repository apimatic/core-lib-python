from datetime import datetime, date

from core_lib.utilities.api_helper import ApiHelper
print(str(date(1994, 2, 13)))
print(ApiHelper.when_defined(ApiHelper.UnixDateTime.from_datetime, datetime(1994, 2, 13, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.UnixDateTime.from_datetime, datetime(1994, 2, 14, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.UnixDateTime.from_datetime, datetime(1994, 2, 15, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.HttpDateTime.from_datetime, datetime(1994, 2, 13, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.HttpDateTime.from_datetime, datetime(1994, 2, 14, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.HttpDateTime.from_datetime, datetime(1994, 2, 15, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.RFC3339DateTime.from_datetime, datetime(1994, 2, 13, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.RFC3339DateTime.from_datetime, datetime(1994, 2, 14, 5, 30, 15)))
print(ApiHelper.when_defined(ApiHelper.RFC3339DateTime.from_datetime, datetime(1994, 2, 15, 5, 30, 15)))

print((ApiHelper.HttpDateTime(datetime(2010, 2, 13, 5, 30, 15)).value, ApiHelper.HttpDateTime(datetime(2010, 2, 13, 5, 30, 15)).value) == (ApiHelper.HttpDateTime(datetime(2010, 2, 13, 5, 30, 15)).value, ApiHelper.HttpDateTime(datetime(2010, 2, 13, 5, 30, 15)).value))

