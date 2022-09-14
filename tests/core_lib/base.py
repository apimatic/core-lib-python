import os
from datetime import datetime, date
from core_lib.configurations.global_configuration import GlobalConfiguration
from core_lib.request_builder import RequestBuilder
from tests.core_lib.models.days import Days
from tests.core_lib.models.person import Employee, Person
from tests.core_lib.test_helper.base_uri_callable import Server, BaseUriCallable


class Base:

    @staticmethod
    def employee_model():
        return Employee(name='Bob', uid=1234567, address='street abc', department='IT', birthday=str(date(1995, 2, 13)),
                        birthtime=datetime(1995, 2, 13, 5, 30, 15), age=27,
                        additional_properties={'key1': 'value1', 'key2': 'value2'},
                        hired_at=datetime(2010, 2, 13, 5, 30, 15), joining_day=Days.MONDAY,
                        working_days=[Days.MONDAY, Days.TUESDAY], salary=30000,
                        dependents=[Person(name='John',
                                           uid=7654321,
                                           address='street abc',
                                           birthday=str(date(2010, 2, 13)),
                                           birthtime=datetime(2010, 2, 13, 5, 30, 15),
                                           age=12,
                                           additional_properties={'key1': 'value1', 'key2': 'value2'})])

    @staticmethod
    def read_file(file_name):
        real_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(real_path, 'core_lib', 'files', file_name)
        return open(file_path, "rb+")

    @property
    def new_request_builder(self):
        return RequestBuilder().path('/test').server(Server.DEFAULT)

    @property
    def global_configuration(self):
        return GlobalConfiguration(None).base_uri_executor(BaseUriCallable().get_base_uri)
