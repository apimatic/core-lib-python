# core-lib-python
This project contains core logic and the utilities for the APIMatic's Python SDK
# Getting Started with CoreLib Python

## Introduction

The Core logic for APIMatic's Python SDK can be found here: (instert link later)


## Install the Package
You will need Python 3.7-3.9 to support this package.

Simply run the command below to install the core library in your SDK. The core library has been added as a dependency in the requirements.txt file

```php
pip install -r requirements.txt
```
## API Call Classes
| Name                                                                        | Description                                                           |
|-----------------------------------------------------------------------------|-----------------------------------------------------------------------|
| [`RequestBuilder`](core_lib/request_builder.py)             | Used to build an API Request                                          |
| [`APICall`](core_lib/api_call.py)                            | Used to create an API Call object                                     |
| [`ResponseHandler`](core_lib/response_handler.py )          | Used to handle the response returned by the server                    |


## Authentication
| Name                                                                         | Description                                                                          |
|------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| [`HeaderAuth`](core-lib-python/core_lib/authentication/header_auth.py)       | A class supports HTTP authentication through HTTP Headers                            |
| [`QueryAuth`](src/Response/Types/ErrorType.php)                              | A class supports HTTP authentication through query parameters                        |
| [`AuthGroup`](core-lib-python/core_lib/authentication/multiple/auth_group.py)| A helper class to support  multiple authentication operation                         |
| [`And`](core-lib-python/core_lib/authentication/multiple/and_auth_group.py)  | A helper class to support AND operation between multiple authentication types        |
| [`Or`](core-lib-python/core_lib/authentication/multiple/or_auth_group.py)    | A helper class to support OR operation between multiple authentication  types        |
| [`Single`](core-lib-python/core_lib/authentication/multiple/single_auth.py)  | A helper class to support single authentication                                      |


## Configurations
| Name                                                                                         | Description                                                          |
|--------------------------------------------------------------------------------------------  |----------------------------------------------------------------------|
| [`EndpointConfiguration`](core-lib-python/core_lib/configurations/endpoint_configuration.py) | A class which hold the possible configurations for an endpoint       |
| [`GlobalConfiguration`](core-lib-python/core_lib/configurations/global_configuration.py )    | A class which hold the global configuration properties to make a                                                                                                        successful Api Call                                                  |

## Decorators
| Name                                                                         | Description                                                                          |
|------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| [`LazyProperty`](core-lib-python/core_lib/decorators/lazy_property.py)       | A decorator class for lazy instantiation                                             |

## Factories
| Name                                                                                  | Description                                                                 |
|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [`HttpResponseFactory`](core-lib-python/core_lib/factories/http_response_factory.py)  | A factory class to create an HTTP Response                                  |

## HTTP
| Name                                                                                                          | Description                                         |
|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| [`HttpCallBack`](core-lib-python/core_lib/factories/http_response_factory.py)                                 | A factory class to create an HTTP Response          |
| [`HttpClientConfiguration`](core-lib-python/core_lib/http/configurations/http_client_configuration.py)        | A class used for configuring the SDK by a user      |
| [`HttpRequest`](core-lib-python/core_lib/http/request/http_request.py)                                        | A class which contains information about the HTTP                                                                                                                       Response                                            |
| [`ApiResponse`](core-lib-python/core_lib/http/response/api_response.py)                                       | A wrapper class for Api Response                    |
| [`HttpResponse`](core-lib-python/core_lib/http/response/http_response.py)                                     | A class which contains information about the HTTP                                                                                                                       Response                                            |

## Logger
| Name                                                                             | Description                                         |
|----------------------------------------------------------------------------------|-----------------------------------------------------|
| [`EndpointLogger`](core-lib-python/core_lib/logger/endpoint_logger.py)           | A class to provide logging for an HTTP request      |

## Types
| Name                                                                                  | Description                                                                 |
|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [`SerializationFormats`](core-lib-python/core_lib/types/array_serialization_format.py)| An Enumeration of Array serialization formats                               |
| [`DateTimeFormat`](core-lib-python/core_lib/types/datetime_format.py )                | An Enumeration of Date Time formats                                         |
| [`ErrorCase`](core-lib-python/core_lib/types/error_case.py )                          |  A class to represent Exception types                                       |
| [`FileWrapper`](core-lib-python/core_lib/types/file_wrapper.py)                       | A wrapper to allow passing in content type for file uploads                 |
| [`Parameter`](core-lib-python/core_lib/types/parameter.py )                           | A class to represent information about a Parameter passed in an endpoint    |
| [`XmlAttributes`](core-lib-python/core_lib/types/xml_attributes.py )                  | A class to represent information about a XML Parameter passed in an endpoint|

## Utilities
| Name                                                                                  | Description                                                                 |
|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [`ApiHelper`](core-lib-python/core_lib/utilities/api_helper.py)              | A Helper Class with various functions associated with making an API Call             |
| [`AuthHelper`](core-lib-python/core_lib/utilities/auth_helper.py)            | A Helper Class with various functions associated with authentication in API Calls    |
| [`ComparisonHelper`](core-lib-python/core_lib/utilities/comparison_helper.py)| A Helper Class used for the comparison of expected and actual API response           |
| [` FileHelper`](core-lib-python/core_lib/utilities/file_helper.py)           | A Helper Class for files                                                             |
| [`XmlHelper`](core-lib-python/core_lib/utilities/xml_helper.py )             |A Helper class that holds utility methods for xml serialization and deserialization.  |

