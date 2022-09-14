from datetime import datetime, date
import pytest
from core_interfaces.types.http_method_enum import HttpMethodEnum
from core_lib.types.array_serialization_format import SerializationFormats
from core_lib.types.file_wrapper import FileWrapper
from core_lib.types.parameter import Parameter
from core_lib.utilities.api_helper import ApiHelper
from tests.core_lib.base import Base
from tests.core_lib.test_helper.base_uri_callable import Server


class TestRequestBuilder(Base):

    @pytest.mark.parametrize('input_server, expected_base_uri', [
        (Server.DEFAULT, 'http://localhost:3000/'),
        (Server.AUTH_SERVER, 'http://authserver:5000/')
    ])
    def test_base_uri(self, input_server, expected_base_uri):
        http_request = self.new_request_builder.server(input_server).path('/').build(self.global_configuration)
        assert http_request.query_url == expected_base_uri

    def test_path(self):
        http_request = self.new_request_builder.build(self.global_configuration)
        assert http_request.query_url == 'http://localhost:3000/test'

    def test_required_param(self):
        with pytest.raises(ValueError) as validation_error:
            self.new_request_builder \
                .query_param(Parameter()
                             .key('query_param')
                             .value(None)
                             .is_required(True)) \
                .build(self.global_configuration)
        assert validation_error.value.args[0] == 'Required parameter query_param cannot be None.'

    def test_optional_param(self):
        http_request = self.new_request_builder \
            .query_param(Parameter()
                         .key('query_param')
                         .value(None)
                         .is_required(False)) \
            .build(self.global_configuration)
        assert http_request.query_url == 'http://localhost:3000/test'

    @pytest.mark.parametrize('input_http_method, expected_http_method', [
        (HttpMethodEnum.POST, HttpMethodEnum.POST),
        (HttpMethodEnum.PUT, HttpMethodEnum.PUT),
        (HttpMethodEnum.PATCH, HttpMethodEnum.PATCH),
        (HttpMethodEnum.DELETE, HttpMethodEnum.DELETE),
        (HttpMethodEnum.GET, HttpMethodEnum.GET),
    ])
    def test_http_method(self, input_http_method, expected_http_method):
        http_request = self.new_request_builder \
            .http_method(input_http_method) \
            .build(self.global_configuration)
        assert http_request.http_method == expected_http_method

    @pytest.mark.parametrize('input_template_param_value, expected_template_param_value, should_encode', [
        ('Basic Test', 'Basic%20Test', True),
        ('Basic"Test', 'Basic%22Test', True),
        ('Basic<Test', 'Basic%3CTest', True),
        ('Basic>Test', 'Basic%3ETest', True),
        ('Basic#Test', 'Basic%23Test', True),
        ('Basic%Test', 'Basic%25Test', True),
        ('Basic|Test', 'Basic%7CTest', True),
        ('Basic Test', 'Basic Test', False),
        ('Basic"Test', 'Basic"Test', False),
        ('Basic<Test', 'Basic<Test', False),
        ('Basic>Test', 'Basic>Test', False),
        ('Basic#Test', 'Basic#Test', False),
        ('Basic%Test', 'Basic%Test', False),
        ('Basic|Test', 'Basic|Test', False),
    ])
    def test_template_params_with_encoding(self, input_template_param_value, expected_template_param_value,
                                           should_encode):
        http_request = self.new_request_builder \
            .path('/{template_param}') \
            .template_param(Parameter()
                            .key('template_param')
                            .value(input_template_param_value)
                            .should_encode(should_encode)) \
            .build(self.global_configuration)
        assert http_request.query_url == 'http://localhost:3000/{}'.format(expected_template_param_value)

    @pytest.mark.parametrize('input_query_param_value, expected_query_param_value, array_serialization_format', [
        ('string', 'query_param=string', SerializationFormats.INDEXED),
        (500, 'query_param=500', SerializationFormats.INDEXED),
        (500.12, 'query_param=500.12', SerializationFormats.INDEXED),
        (date(1994, 2, 13), 'query_param=1994-02-13', SerializationFormats.INDEXED),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         'query_param=761117415', SerializationFormats.INDEXED),
        (ApiHelper.HttpDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         'query_param=Sun%2C%2013%20Feb%201994%2000%3A30%3A15%20GMT', SerializationFormats.INDEXED),
        (ApiHelper.RFC3339DateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         'query_param=1994-02-13T05%3A30%3A15', SerializationFormats.INDEXED),
        ([1, 2, 3, 4], 'query_param[0]=1&query_param[1]=2&query_param[2]=3&query_param[3]=4',
         SerializationFormats.INDEXED),
        ([1, 2, 3, 4], 'query_param[]=1&query_param[]=2&query_param[]=3&query_param[]=4',
         SerializationFormats.UN_INDEXED),
        ([1, 2, 3, 4], 'query_param=1&query_param=2&query_param=3&query_param=4',
         SerializationFormats.PLAIN),
        ([1, 2, 3, 4], 'query_param=1%2C2%2C3%2C4', SerializationFormats.CSV),
        ([1, 2, 3, 4], 'query_param=1%7C2%7C3%7C4', SerializationFormats.PSV),
        ([1, 2, 3, 4], 'query_param=1%092%093%094', SerializationFormats.TSV),
        ({'key1': 'value1', 'key2': 'value2'}, 'query_param[key1]=value1&query_param[key2]=value2',
         SerializationFormats.INDEXED),
        ({'key1': 'value1', 'key2': [1, 2, 3, 4]},
         'query_param[key1]=value1'
         '&query_param[key2][0]=1'
         '&query_param[key2][1]=2'
         '&query_param[key2][2]=3'
         '&query_param[key2][3]=4', SerializationFormats.INDEXED),
        ({'key1': 'value1', 'key2': [1, 2, 3, {'key1': 'value1', 'key2': 'value2'}]},
         'query_param[key1]=value1'
         '&query_param[key2][0]=1'
         '&query_param[key2][1]=2'
         '&query_param[key2][2]=3'
         '&query_param[key2][3][key1]=value1'
         '&query_param[key2][3][key2]=value2', SerializationFormats.INDEXED),
        (Base.employee_model(),
         'query_param[address]=street%20abc'
         '&query_param[age]=27'
         '&query_param[birthday]=1995-02-13'
         '&query_param[birthtime]=1995-02-13T05%3A30%3A15'
         '&query_param[department]=IT'
         '&query_param[dependents][0][address]=street%20abc'
         '&query_param[dependents][0][age]=12'
         '&query_param[dependents][0][birthday]=2010-02-13'
         '&query_param[dependents][0][birthtime]=2010-02-13T05%3A30%3A15'
         '&query_param[dependents][0][name]=John'
         '&query_param[dependents][0][uid]=7654321'
         '&query_param[dependents][0][personType]=Per'
         '&query_param[dependents][0][key1]=value1'
         '&query_param[dependents][0][key2]=value2'
         '&query_param[hiredAt]=Sat%2C%2013%20Feb%202010%2000%3A30%3A15%20GMT'
         '&query_param[joiningDay]=Monday'
         '&query_param[name]=Bob'
         '&query_param[salary]=30000'
         '&query_param[uid]=1234567'
         '&query_param[workingDays][0]=Monday'
         '&query_param[workingDays][1]=Tuesday'
         '&query_param[personType]=Empl', SerializationFormats.INDEXED)
    ])
    def test_query_params(self, input_query_param_value, expected_query_param_value, array_serialization_format):
        http_request = self.new_request_builder \
            .query_param(Parameter()
                         .key('query_param')
                         .value(input_query_param_value)) \
            .array_serialization_format(array_serialization_format) \
            .build(self.global_configuration)
        assert http_request.query_url == 'http://localhost:3000/test?{}'.format(expected_query_param_value)

    @pytest.mark.parametrize('input_local_header_param_value, expected_local_header_param_value', [
        ('string', {'header_param': 'string'}),
        (500, {'header_param': 500}),
        (500.12, {'header_param': 500.12}),
        (str(date(1994, 2, 13)), {'header_param': '1994-02-13'}),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         {'header_param': 761117415}),
        (ApiHelper.HttpDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         {'header_param': 'Sun, 13 Feb 1994 00:30:15 GMT'}),
        (ApiHelper.RFC3339DateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         {'header_param': '1994-02-13T05:30:15'}),
        ([1, 2, 3, 4], {'header_param': [1, 2, 3, 4]})
    ])
    def test_local_headers(self, input_local_header_param_value, expected_local_header_param_value):
        http_request = self.new_request_builder \
            .header_param(Parameter()
                          .key('header_param')
                          .value(input_local_header_param_value)) \
            .build(self.global_configuration)
        assert http_request.headers == expected_local_header_param_value

    @pytest.mark.parametrize('input_global_header_param_value, expected_global_header_param_value', [
        ('my-string', {'header_param': 'my-string'}),
        (5000, {'header_param': 5000}),
        (5000.12, {'header_param': 5000.12}),
        (str(date(1998, 2, 13)), {'header_param': '1998-02-13'}),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         {'header_param': 761117415}),
        (ApiHelper.HttpDateTime.from_datetime(datetime(1998, 2, 13, 5, 30, 15)),
         {'header_param': 'Fri, 13 Feb 1998 00:30:15 GMT'}),
        (ApiHelper.RFC3339DateTime.from_datetime(datetime(1998, 2, 13, 5, 30, 15)),
         {'header_param': '1998-02-13T05:30:15'}),
        ([100, 200, 300, 400], {'header_param': [100, 200, 300, 400]})
    ])
    def test_global_headers(self, input_global_header_param_value, expected_global_header_param_value):
        http_request = self.new_request_builder \
            .build(self.global_configuration
                   .global_header('header_param', input_global_header_param_value))
        assert http_request.headers == expected_global_header_param_value

    @pytest.mark.parametrize('input_global_header_param_value,'
                             'input_local_header_param_value,'
                             'expected_header_param_value', [
                                 ('global_string', 'local_string', {'header_param': 'local_string'})
                             ])
    def test_headers_precedence(self, input_global_header_param_value, input_local_header_param_value,
                                expected_header_param_value):
        http_request = self.new_request_builder \
            .header_param(Parameter()
                          .key('header_param')
                          .value(input_local_header_param_value)) \
            .build(self.global_configuration.global_header('header_param', input_global_header_param_value))
        assert http_request.headers == expected_header_param_value

    @pytest.mark.parametrize('input_form_param_value, expected_form_param_value, array_serialization_format', [
        ('string', [('form_param', 'string')], SerializationFormats.INDEXED),
        (500, [('form_param', 500)], SerializationFormats.INDEXED),
        (500.12, [('form_param', 500.12)], SerializationFormats.INDEXED),
        (str(date(1994, 2, 13)), [('form_param', '1994-02-13')], SerializationFormats.INDEXED),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         [('form_param', 761117415)], SerializationFormats.INDEXED),
        (ApiHelper.HttpDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         [('form_param', 'Sun, 13 Feb 1994 00:30:15 GMT')], SerializationFormats.INDEXED),
        (ApiHelper.RFC3339DateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)),
         [('form_param', '1994-02-13T05:30:15')], SerializationFormats.INDEXED),
        ([1, 2, 3, 4], [('form_param[0]', 1), ('form_param[1]', 2), ('form_param[2]', 3), ('form_param[3]', 4)],
         SerializationFormats.INDEXED),
        ([1, 2, 3, 4], [('form_param[]', 1), ('form_param[]', 2), ('form_param[]', 3), ('form_param[]', 4)],
         SerializationFormats.UN_INDEXED),
        ([1, 2, 3, 4], [('form_param', 1), ('form_param', 2), ('form_param', 3), ('form_param', 4)],
         SerializationFormats.PLAIN),
        ({'key1': 'value1', 'key2': 'value2'}, [('form_param[key1]', 'value1'), ('form_param[key2]', 'value2')],
         SerializationFormats.INDEXED),
        ({'key1': 'value1', 'key2': [1, 2, 3, 4]},
         [('form_param[key1]', 'value1'), ('form_param[key2][0]', 1), ('form_param[key2][1]', 2),
          ('form_param[key2][2]', 3), ('form_param[key2][3]', 4)], SerializationFormats.INDEXED),
        ({'key1': 'value1', 'key2': [1, 2, 3, {'key1': 'value1', 'key2': 'value2'}]},
         [('form_param[key1]', 'value1'), ('form_param[key2][0]', 1), ('form_param[key2][1]', 2),
          ('form_param[key2][2]', 3), ('form_param[key2][3][key1]', 'value1'), ('form_param[key2][3][key2]', 'value2')],
         SerializationFormats.INDEXED),
        (Base.employee_model(),
         [('form_param[address]', 'street abc'), ('form_param[age]', 27), ('form_param[birthday]', '1995-02-13'),
          ('form_param[birthtime]', ApiHelper.RFC3339DateTime(datetime(1995, 2, 13, 5, 30, 15))),
          ('form_param[department]', 'IT'), ('form_param[dependents][0][address]', 'street abc'),
          ('form_param[dependents][0][age]', 12), ('form_param[dependents][0][birthday]', '2010-02-13'),
          ('form_param[dependents][0][birthtime]', ApiHelper.RFC3339DateTime(datetime(2010, 2, 13, 5, 30, 15))),
          ('form_param[dependents][0][name]', 'John'), ('form_param[dependents][0][uid]', 7654321),
          ('form_param[dependents][0][personType]', 'Per'), ('form_param[dependents][0][key1]', 'value1'),
          ('form_param[dependents][0][key2]', 'value2'),
          ('form_param[hiredAt]', ApiHelper.HttpDateTime(datetime(2010, 2, 13, 5, 30, 15))),
          ('form_param[joiningDay]', 'Monday'), ('form_param[name]', 'Bob'), ('form_param[salary]', 30000),
          ('form_param[uid]', 1234567), ('form_param[workingDays][0]', 'Monday'),
          ('form_param[workingDays][1]', 'Tuesday'), ('form_param[personType]', 'Empl')], SerializationFormats.INDEXED)
    ])
    def test_form_params(self, input_form_param_value, expected_form_param_value, array_serialization_format):
        http_request = self.new_request_builder \
            .form_param(Parameter()
                        .key('form_param')
                        .value(input_form_param_value)) \
            .array_serialization_format(array_serialization_format) \
            .build(self.global_configuration)
        for index, item in enumerate(http_request.parameters):
            # form encoding stores the datetime object so converting datetime to string for assertions as assertions
            # do not work for objects
            if isinstance(item[1], ApiHelper.CustomDate):
                assert item[0] == expected_form_param_value[index][0] \
                       and item[1].value == expected_form_param_value[index][1].value
            else:
                assert item == expected_form_param_value[index]

    @pytest.mark.parametrize('input_additional_form_param_value, expected_additional_form_param_value', [
        ({'key1': 'value1', 'key2': 'value2'}, [('key1', 'value1'), ('key2', 'value2')])
    ])
    def test_addition_form_params(self, input_additional_form_param_value, expected_additional_form_param_value):
        http_request = self.new_request_builder \
            .additional_form_params(input_additional_form_param_value) \
            .build(self.global_configuration)
        assert http_request.parameters == expected_additional_form_param_value

    @pytest.mark.parametrize('input_form_param_value,'
                             'input_additional_form_param_value,'
                             'expected_form_param_value', [
                                 ({'key1': 'value1', 'key2': 'value2'},
                                  {'additional_key1': 'additional_value1', 'additional_key2': 'additional_value2'},
                                  [('form_param[key1]', 'value1'), ('form_param[key2]', 'value2'),
                                   ('additional_key1', 'additional_value1'),
                                   ('additional_key2', 'additional_value2')])
                             ])
    def test_form_params_with_additional_form_params(self, input_form_param_value, input_additional_form_param_value,
                                                     expected_form_param_value):
        http_request = self.new_request_builder \
            .form_param(Parameter()
                        .key('form_param')
                        .value(input_form_param_value)) \
            .additional_form_params(input_additional_form_param_value) \
            .build(self.global_configuration)
        assert http_request.parameters == expected_form_param_value

    @pytest.mark.parametrize('input_body_param_value, expected_body_param_value', [
        ('string', 'string'),
        (500, 500),
        (500.12, 500.12),
        (str(date(1994, 2, 13)), '1994-02-13'),
        (ApiHelper.UnixDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)), 761117415),
        (ApiHelper.HttpDateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)), 'Sun, 13 Feb 1994 00:30:15 GMT'),
        (ApiHelper.RFC3339DateTime.from_datetime(datetime(1994, 2, 13, 5, 30, 15)), '1994-02-13T05:30:15')
    ])
    def test_json_body_params_without_serializer(self, input_body_param_value, expected_body_param_value):
        http_request = self.new_request_builder \
            .body_param(Parameter()
                        .value(input_body_param_value)) \
            .build(self.global_configuration)
        assert http_request.parameters == expected_body_param_value

    @pytest.mark.parametrize('input_body_param_value1, input_body_param_value2, expected_body_param_value', [
        ('string1', 'string2', '{"param1": "string1", "param2": "string2"}'),
        (100, 200, '{"param1": 100, "param2": 200}'),
        (100.12, 200.12, '{"param1": 100.12, "param2": 200.12}')
    ])
    def test_multiple_json_body_params_with_serializer(self, input_body_param_value1, input_body_param_value2,
                                                       expected_body_param_value):
        http_request = self.new_request_builder \
            .body_param(Parameter()
                        .key('param1')
                        .value(input_body_param_value1)) \
            .body_param(Parameter()
                        .key('param2')
                        .value(input_body_param_value2)) \
            .body_serializer(ApiHelper.json_serialize) \
            .build(self.global_configuration)
        assert http_request.parameters == expected_body_param_value

    @pytest.mark.parametrize('input_body_param_value, expected_body_param_value', [
        ([1, 2, 3, 4], '[1, 2, 3, 4]'),
        ({'key1': 'value1', 'key2': 'value2'}, '{"key1": "value1", "key2": "value2"}'),
        ({'key1': 'value1', 'key2': [1, 2, 3, 4]}, '{"key1": "value1", "key2": [1, 2, 3, 4]}'),
        ({'key1': 'value1', 'key2': [1, 2, 3, {'key1': 'value1', 'key2': 'value2'}]},
         '{"key1": "value1", "key2": [1, 2, 3, {"key1": "value1", "key2": "value2"}]}'),
        (Base.employee_model(), '{"address": "street abc", "age": 27, "birthday": "1995-02-13", "birthtime": '
                                '"1995-02-13T05:30:15", "boss": null, "department": "IT", "dependents": [{"address": '
                                '"street abc", "age": 12, "birthday": "2010-02-13", "birthtime": '
                                '"2010-02-13T05:30:15", "name": "John", "uid": 7654321, "personType": "Per", '
                                '"key1": "value1", "key2": "value2"}], "hiredAt": "Sat, 13 Feb 2010 00:30:15 GMT", '
                                '"joiningDay": "Monday", "name": "Bob", "salary": 30000, "uid": 1234567, '
                                '"workingDays": ["Monday", "Tuesday"], "personType": "Empl"}')
    ])
    def test_json_body_params_with_serializer(self, input_body_param_value, expected_body_param_value):
        http_request = self.new_request_builder \
            .body_param(Parameter()
                        .value(input_body_param_value)) \
            .body_serializer(ApiHelper.json_serialize) \
            .build(self.global_configuration)
        assert http_request.parameters == expected_body_param_value

    @pytest.mark.parametrize('input_body_param_value, expected_body_param_value, expected_content_type', [
                                 (FileWrapper(Base.read_file('apimatic.png'), 'image/png'),
                                  Base.read_file('apimatic.png'), 'image/png')])
    def test_file_as_body_param(self, input_body_param_value, expected_body_param_value, expected_content_type):
        try:
            http_request = self.new_request_builder \
                .header_param(Parameter().key('content-type').value('application/xml')) \
                .body_param(Parameter().value(input_body_param_value)) \
                .build(self.global_configuration)

            actual_body_param_value = http_request.parameters

            assert actual_body_param_value.read() == expected_body_param_value.read() \
                   and http_request.headers['content-type'] == expected_content_type
        finally:
            actual_body_param_value.close()
            expected_body_param_value.close()

    @pytest.mark.parametrize('input_multipart_param_value1, input_default_content_type1, '
                             'input_multipart_param_value2, input_default_content_type2, '
                             'expected_multipart_param_value1, expected_default_content_type1, '
                             'expected_multipart_param_value2, expected_default_content_type2', [
                                 (Base.read_file('apimatic.png'), 'image/png', Base.employee_model(),
                                  'application/json', Base.read_file('apimatic.png'), 'image/png',
                                  '{"address": "street abc", "age": 27, "birthday": "1995-02-13", "birthtime": '
                                  '"1995-02-13T05:30:15", "boss": null, "department": "IT", "dependents": [{"address": '
                                  '"street abc", "age": 12, "birthday": "2010-02-13", "birthtime": '
                                  '"2010-02-13T05:30:15", "name": "John", "uid": 7654321, "personType": "Per", '
                                  '"key1": "value1", "key2": "value2"}], "hiredAt": "Sat, 13 Feb 2010 00:30:15 GMT", '
                                  '"joiningDay": "Monday", "name": "Bob", "salary": 30000, "uid": 1234567, '
                                  '"workingDays": ["Monday", "Tuesday"], "personType": "Empl"}', 'application/json')
                             ])
    def test_multipart_request_without_file_wrapper(self, input_multipart_param_value1,
                                                    input_default_content_type1,
                                                    input_multipart_param_value2,
                                                    input_default_content_type2,
                                                    expected_multipart_param_value1,
                                                    expected_default_content_type1,
                                                    expected_multipart_param_value2,
                                                    expected_default_content_type2):
        try:
            http_request = self.new_request_builder \
                .multipart_param(Parameter().key('file_wrapper')
                                 .value(input_multipart_param_value1)
                                 .default_content_type(input_default_content_type1)) \
                .multipart_param(Parameter().key('model')
                                 .value(ApiHelper.json_serialize(input_multipart_param_value2))
                                 .default_content_type(input_default_content_type2)) \
                .build(self.global_configuration)

            actual_multipart_param_value1 = http_request.files['file_wrapper'][1]
            actual_multipart_param_content_type1 = http_request.files['file_wrapper'][2]
            actual_multipart_param_value2 = http_request.files['model'][1]
            actual_multipart_param_content_type2 = http_request.files['model'][2]

            assert actual_multipart_param_value1.read() == expected_multipart_param_value1.read() \
                   and actual_multipart_param_content_type1 == expected_default_content_type1 \
                   and actual_multipart_param_value2 == expected_multipart_param_value2 \
                   and actual_multipart_param_content_type2 == expected_default_content_type2
        finally:
            actual_multipart_param_value1.close()
            expected_multipart_param_value1.close()

    @pytest.mark.parametrize('input_multipart_param_value1,'
                             'input_multipart_param_value2, input_default_content_type2, '
                             'expected_multipart_param_value1, expected_default_content_type1, '
                             'expected_multipart_param_value2, expected_default_content_type2', [
                                 (FileWrapper(Base.read_file('apimatic.png'), 'image/png'), Base.employee_model(),
                                  'application/json', Base.read_file('apimatic.png'), 'image/png',
                                  '{"address": "street abc", "age": 27, "birthday": "1995-02-13", "birthtime": '
                                  '"1995-02-13T05:30:15", "boss": null, "department": "IT", "dependents": [{"address": '
                                  '"street abc", "age": 12, "birthday": "2010-02-13", "birthtime": '
                                  '"2010-02-13T05:30:15", "name": "John", "uid": 7654321, "personType": "Per", '
                                  '"key1": "value1", "key2": "value2"}], "hiredAt": "Sat, 13 Feb 2010 00:30:15 GMT", '
                                  '"joiningDay": "Monday", "name": "Bob", "salary": 30000, "uid": 1234567, '
                                  '"workingDays": ["Monday", "Tuesday"], "personType": "Empl"}', 'application/json')
                             ])
    def test_multipart_request_with_file_wrapper(self, input_multipart_param_value1,
                                                 input_multipart_param_value2,
                                                 input_default_content_type2,
                                                 expected_multipart_param_value1,
                                                 expected_default_content_type1,
                                                 expected_multipart_param_value2,
                                                 expected_default_content_type2):
        try:
            http_request = self.new_request_builder \
                .multipart_param(Parameter().key('file')
                                 .value(input_multipart_param_value1)) \
                .multipart_param(Parameter().key('model')
                                 .value(ApiHelper.json_serialize(input_multipart_param_value2))
                                 .default_content_type(input_default_content_type2)) \
                .build(self.global_configuration)

            actual_multipart_param_value1 = http_request.files['file'][1]
            actual_multipart_param_content_type1 = http_request.files['file'][2]
            actual_multipart_param_value2 = http_request.files['model'][1]
            actual_multipart_param_content_type2 = http_request.files['model'][2]

            assert actual_multipart_param_value1.read() == expected_multipart_param_value1.read() \
                   and actual_multipart_param_content_type1 == expected_default_content_type1 \
                   and actual_multipart_param_value2 == expected_multipart_param_value2 \
                   and actual_multipart_param_content_type2 == expected_default_content_type2
        finally:
            actual_multipart_param_value1.close()
            expected_multipart_param_value1.close()
