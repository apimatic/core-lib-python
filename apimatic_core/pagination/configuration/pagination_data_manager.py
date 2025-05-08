# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class PaginationDataManager(ABC):
    """An interface for managing pagination in API responses.

    This class should not be instantiated directly but should be subclassed
    to provide specific pagination management logic for paginated API responses.
    """

    @abstractmethod
    def is_valid(self, paginated_data, next_req_builder):
        """Checks if the given paginated data contains a valid next page.

        Args:
            paginated_data: The paginated response data to check.
            next_req_builder: The next request builder.

        Returns:
            bool: True if the paginated data is valid and has a next page, False otherwise.
        """
        ...
