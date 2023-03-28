# apimatic-core
[![PyPI][pypi-version]][apimatic-core-pypi-url]
[![Tests][test-badge]][test-url]
[![Test Coverage][test-coverage-url]][code-climate-url]
[![Licence][license-badge]][license-url]

## Introduction
The APIMatic Core libraries provide a stable runtime that powers all the functionality of SDKs. This includes functionality like the ability to create HTTP requests, handle responses, apply authentication schemes, convert API responses back to object instances, and validate user and server data.


## Installation
You will need Python 3.7-3.11 to support this package.

Simply run the command below to install the core library in your SDK. The core library will be added as a dependency your SDK.

```php
pip install apimatic-core
```
## API Call Classes
| Name                                                        | Description                                                           |
|-------------------------------------------------------------|-----------------------------------------------------------------------|
| [`RequestBuilder`](apimatic_core/request_builder.py)        | A builder class used to build an API Request                          |
| [`APICall`](apimatic_core/api_call.py)                      | A class used to create an API Call object                             |
| [`ResponseHandler`](apimatic_core/response_handler.py )     | Used to handle the response returned by the server                    |


## Authentication
| Name                                                               | Description                                                                          |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| [`HeaderAuth`](apimatic_core/authentication/header_auth.py)        | A class supports HTTP authentication through HTTP Headers                            |
| [`QueryAuth`](apimatic_core/authentication/query_auth.py)          | A class supports HTTP authentication through query parameters                        |
| [`AuthGroup`](apimatic_core/authentication/multiple/auth_group.py) | A helper class to support  multiple authentication operation                         |
| [`And`](apimatic_core/authentication/multiple/and_auth_group.py)   | A helper class to support AND operation between multiple authentication types        |
| [`Or`](apimatic_core/authentication/multiple/or_auth_group.py)     | A helper class to support OR operation between multiple authentication  types        |
| [`Single`](apimatic_core/authentication/multiple/single_auth.py)   | A helper class to support single authentication                                      |


## Configurations
| Name                                                                             | Description                                                                          |
|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| [`EndpointConfiguration`](apimatic_core/configurations/endpoint_configuration.py)| A class which hold the possible configurations for an endpoint                       |
| [`GlobalConfiguration`](apimatic_core/configurations/global_configuration.py )   | A class which hold the global configuration properties to make a successful Api Call |

## Decorators
| Name                                                         | Description                                                                          |
|--------------------------------------------------------------|--------------------------------------------------------------------------------------|
| [`LazyProperty`](apimatic_core/decorators/lazy_property.py)  | A decorator class for lazy instantiation                                             |

## Factories
| Name                                                                      | Description                                                                 |
|---------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [`HttpResponseFactory`](apimatic_core/factories/http_response_factory.py) | A factory class to create an HTTP Response                                  |

## HTTP
| Name                                                                                        | Description                                                 |
|---------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| [`HttpCallBack`](apimatic_core/factories/http_response_factory.py)                          | A factory class to create an HTTP Response                  |
| [`HttpClientConfiguration`](apimatic_core/http/configurations/http_client_configuration.py) | A class used for configuring the SDK by a user              |
| [`HttpRequest`](apimatic_core/http/request/http_request.py)                                 | A class which contains information about the HTTP Response  |
| [`ApiResponse`](apimatic_core/http/response/api_response.py)                                | A wrapper class for Api Response                            |
| [`HttpResponse`](apimatic_core/http/response/http_response.py)                              | A class which contains information about the HTTP Response  |

## Logger
| Name                                                             | Description                                         |
|------------------------------------------------------------------|-----------------------------------------------------|
| [`EndpointLogger`](apimatic_core/logger/endpoint_logger.py)      | A class to provide logging for an HTTP request      |

## Types
| Name                                                                         | Description                                                                  |
|------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| [`SerializationFormats`](apimatic_core/types/array_serialization_format.py)  | An Enumeration of Array serialization formats                                |
| [`DateTimeFormat`](apimatic_core/types/datetime_format.py )                  | An Enumeration of Date Time formats                                          |
| [`ErrorCase`](apimatic_core/types/error_case.py )                            | A class to represent Exception types                                         |
| [`FileWrapper`](apimatic_core/types/file_wrapper.py)                         | A wrapper to allow passing in content type for file uploads                  |
| [`Parameter`](apimatic_core/types/parameter.py )                             | A class to represent information about a Parameter passed in an endpoint     |
| [`XmlAttributes`](apimatic_core/types/xml_attributes.py )                    | A class to represent information about a XML Parameter passed in an endpoint |

## Utilities
| Name                                                               | Description                                                                          |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| [`ApiHelper`](apimatic_core/utilities/api_helper.py)               | A Helper Class with various functions associated with making an API Call             |
| [`AuthHelper`](apimatic_core/utilities/auth_helper.py)             | A Helper Class with various functions associated with authentication in API Calls    |
| [`ComparisonHelper`](apimatic_core/utilities/comparison_helper.py) | A Helper Class used for the comparison of expected and actual API response           |
| [` FileHelper`](apimatic_core/utilities/file_helper.py)            | A Helper Class for files                                                             |
| [`XmlHelper`](apimatic_core/utilities/xml_helper.py )              | A Helper class that holds utility methods for xml serialization and deserialization. |

## Links
* [apimatic-core-interfaces](https://pypi.org/project/apimatic-core-interfaces/)


[pypi-version]: https://img.shields.io/pypi/v/apimatic-core
[apimatic-core-pypi-url]: https://pypi.org/project/apimatic-core/
[test-badge]: https://github.com/apimatic/core-lib-python/actions/workflows/test-runner.yml/badge.svg
[test-url]: https://github.com/apimatic/core-lib-python/actions/workflows/test-runner.yml
[code-climate-url]: https://codeclimate.com/github/apimatic/core-lib-python
[maintainability-url]: https://api.codeclimate.com/v1/badges/32e7abfdd4d27613ae76/maintainability
[test-coverage-url]: https://api.codeclimate.com/v1/badges/32e7abfdd4d27613ae76/test_coverage
[license-badge]: https://img.shields.io/badge/licence-MIT-blue
[license-url]: LICENSE
