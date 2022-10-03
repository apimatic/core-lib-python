# -*- coding: utf-8 -*-
from apimatic_core.factories.http_response_factory import HttpResponseFactory


class HttpClientConfiguration(object):
    """A class used for configuring the SDK by a user.
    """

    @property
    def http_response_factory(self):
        return self._http_response_factory

    @property
    def http_client(self):
        return self._http_client

    @property
    def http_callback(self):
        return self._http_call_back

    @property
    def http_client_instance(self):
        return self._http_client_instance

    @property
    def override_http_client_configuration(self):
        return self._override_http_client_configuration

    @property
    def timeout(self):
        return self._timeout

    @property
    def max_retries(self):
        return self._max_retries

    @property
    def backoff_factor(self):
        return self._backoff_factor

    @property
    def retry_statuses(self):
        return self._retry_statuses

    @property
    def retry_methods(self):
        return self._retry_methods

    def __init__(
            self, http_client_instance,
            override_http_client_configuration, http_call_back,
            timeout, max_retries, backoff_factor,
            retry_statuses,
            retry_methods
    ):
        self._http_response_factory = HttpResponseFactory()

        # The Http Client passed from the sdk user for making requests
        self._http_client_instance = http_client_instance

        # The value which determines to override properties of the passed Http Client from the sdk user
        self._override_http_client_configuration = override_http_client_configuration

        #  The callback value that is invoked before and after an HTTP call is made to an endpoint
        self._http_call_back = http_call_back

        # The value to use for connection timeout
        self._timeout = timeout

        # The number of times to retry an endpoint call if it fails
        self._max_retries = max_retries

        # A backoff factor to apply between attempts after the second try.
        # urllib3 will sleep for:
        # `{backoff factor} * (2 ** ({number of total retries} - 1))`
        self._backoff_factor = backoff_factor

        # The http statuses on which retry is to be done
        self._retry_statuses = retry_statuses

        # The http methods on which retry is to be done
        self._retry_methods = retry_methods

        # The Http Client to use for making requests.
        self._http_client = None

    def set_http_client(self, http_client):
        self._http_client = http_client
