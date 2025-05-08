class EndpointConfiguration:
    """Configuration for an API endpoint, including binary response handling,
    retry behavior, and request builder management.
    """

    def __init__(self):
        self._has_binary_response = None
        self._to_retry = None

    @property
    def contains_binary_response(self):
        """Indicates whether the response is expected to be binary."""
        return self._has_binary_response

    @property
    def should_retry(self):
        """Indicates whether the request should be retried on failure."""
        return self._to_retry

    def has_binary_response(self, has_binary_response):
        """Sets whether the response should be treated as binary.

        Args:
            has_binary_response (bool): True if the response is binary.

        Returns:
            EndpointConfiguration: The current instance for chaining.
        """
        self._has_binary_response = has_binary_response
        return self

    def to_retry(self, to_retry):
        """Sets whether the request should be retried on failure.

        Args:
            to_retry (bool): True if retries should be attempted.

        Returns:
            EndpointConfiguration: The current instance for chaining.
        """
        self._to_retry = to_retry
        return self
