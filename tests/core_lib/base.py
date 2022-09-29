import logging
import os
import platform
from datetime import datetime, date
from core_interfaces.types.http_method_enum import HttpMethodEnum
from core_lib.configurations.global_configuration import GlobalConfiguration
from core_lib.http.request.http_request import HttpRequest
from core_lib.http.response.http_response import HttpResponse
from core_lib.logger.endpoint_logger import EndpointLogger
from core_lib.request_builder import RequestBuilder
from core_lib.response_handler import ResponseHandler
from core_lib.types.error_case import ErrorCase
from tests.core_lib.authentications.basic_auth import BasicAuth
from tests.core_lib.authentications.bearer_auth import BearerAuth
from tests.core_lib.authentications.custom_header_authentication import CustomHeaderAuthentication
from tests.core_lib.authentications.custom_query_authentication import CustomQueryAuthentication
from tests.core_lib.exceptions.global_test_exception import GlobalTestException
from tests.core_lib.exceptions.nested_model_exception import NestedModelException
from tests.core_lib.models.cat_model import CatModel
from tests.core_lib.models.dog_model import DogModel
from tests.core_lib.models.one_of_xml import OneOfXML
from tests.core_lib.models.wolf_model import WolfModel
from tests.core_lib.models.xml_model import XMLModel
from tests.core_lib.models.days import Days
from tests.core_lib.models.person import Employee, Person
from tests.core_lib.callables.base_uri_callable import Server, BaseUriCallable


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
    def person_model():
        return Person(name='Bob', uid=1234567, address='street abc', birthday=date(1995, 2, 13),
                      birthtime=datetime(1995, 2, 13, 5, 30, 15), age=27,
                      additional_properties={'key1': 'value1', 'key2': 'value2'},
                      )

    @staticmethod
    def employee_model_additional_dictionary():
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
                                           additional_properties={
                                               'key1': {'inner_key1': 'inner_val1', 'inner_key2': 'inner_val2'},
                                               'key2': ['value2', 'value3']})])

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
    def xml_model():
        return XMLModel(string_attr='String', number_attr=10000, boolean_attr=False,
                        string_element='Hey! I am being tested.', number_element=5000,
                        boolean_element=False, elements=['a', 'b', 'c'])

    @staticmethod
    def one_of_xml_dog_model():
        return OneOfXML(value=DogModel(barks=True))

    @staticmethod
    def one_of_xml_cat_model():
        return OneOfXML(value=[CatModel(meows=True), CatModel(meows=False)])

    @staticmethod
    def one_of_xml_wolf_model():
        return OneOfXML(value=[WolfModel(howls=True), WolfModel(howls=False)])

    @staticmethod
    def read_file(file_name):
        real_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(real_path, 'core_lib', 'files', file_name)
        return open(file_path, "rb")

    @staticmethod
    def global_errors():
        return {
            '400': ErrorCase().description('400 Global').exception_type(GlobalTestException),
            '412': ErrorCase().description('Precondition Failed').exception_type(NestedModelException),
            'default': ErrorCase().description('Invalid response').exception_type(GlobalTestException),
        }

    @staticmethod
    def request():
        return HttpRequest(http_method=HttpMethodEnum.GET, query_url='http://localhost:3000/test')

    @staticmethod
    def response(status_code=200, reason_phrase=None, headers=None, text=None):
        return HttpResponse(status_code=status_code, reason_phrase=reason_phrase,
                            headers=headers, text=text, request=Base.request())

    @property
    def new_request_builder(self):
        return RequestBuilder().path('/test').server(Server.DEFAULT)

    @property
    def global_configuration(self):
        return GlobalConfiguration(None) \
            .base_uri_executor(BaseUriCallable().get_base_uri) \
            .global_errors(self.global_errors())

    @property
    def global_configuration_with_useragent(self):
        return self.global_configuration.user_agent(self.user_agent(), self.user_agent_parameters())

    @staticmethod
    def user_agent():
        return 'Python|31.8.0|{engine}|{engine-version}|{os-info}'

    @staticmethod
    def user_agent_parameters():
        return {
            'engine': {'value': platform.python_implementation(), 'encode': False},
            'engine-version': {'value': "", 'encode': False},
            'os-info': {'value': platform.system(), 'encode': False},
        }

    @property
    def new_request_builder(self):
        return RequestBuilder().path('/test')\
            .endpoint_name_for_logging('Dummy Endpoint')\
            .endpoint_logger(EndpointLogger(None))\
            .server(Server.DEFAULT)

    @property
    def new_response_handler(self):
        return ResponseHandler()\
            .endpoint_name_for_logging('Dummy Endpoint')\
            .endpoint_logger(EndpointLogger(None))

    @property
    def global_configuration(self):
        return GlobalConfiguration(None) \
            .base_uri_executor(BaseUriCallable().get_base_uri) \
            .global_errors(self.global_errors())

    @property
    def global_configuration_with_useragent(self):
        return self.global_configuration.user_agent(self.user_agent(), self.user_agent_parameters())

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

    @staticmethod
    def wrapped_parameters():
        return {
            'bodyScalar': True,
            'bodyNonScalar': Base.employee_model(),
        }
