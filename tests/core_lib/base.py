import os
from datetime import datetime, date
from core_lib.configurations.global_configuration import GlobalConfiguration
from core_lib.request_builder import RequestBuilder
from tests.core_lib.authentications.basic_auth import BasicAuth
from tests.core_lib.authentications.bearer_auth import BearerAuth
from tests.core_lib.authentications.custom_header_authentication import CustomHeaderAuthentication
from tests.core_lib.authentications.custom_query_authentication import CustomQueryAuthentication
from tests.core_lib.models.attributes_and_elements_model import AttributesAndElementsModel
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
    def basic_auth():
        return BasicAuth(basic_auth_user_name='test_username', basic_auth_password='test_password')

    @staticmethod
    def bearer_auth():
        return BearerAuth(access_token='0b79bab50daca910b000d4f1a2b675d604257e42')

    @staticmethod
    def custom_header_auth():
        return CustomHeaderAuthentication(token='Qaws2W233WedeRe4T56G6Vref2')

    @staticmethod
    def custom_query_auth():
        return CustomQueryAuthentication(api_key='W233WedeRe4T56G6Vref2', token='Qaws2W233WedeRe4T56G6Vref2')

    @staticmethod
    def attributes_and_elements_model():
        return AttributesAndElementsModel(string_attr='String', number_attr='Number',
                                          string_element='Hey! I am being tested.', number_element=5000)

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

    @property
    def global_configuration_with_auth(self):
        return self.global_configuration.auth_managers(
            {'basic_auth': self.basic_auth(), 'bearer_auth': self.bearer_auth(),
             'custom_header_auth': self.custom_header_auth(), 'custom_query_auth': self.custom_query_auth()})

    @property
    def global_configuration_with_uninitialized_auth_params(self):
        return self.global_configuration.auth_managers(
            {'basic_auth': BasicAuth(None, None), 'bearer_auth': BearerAuth(None),
             'custom_header_auth': CustomHeaderAuthentication(None)})
