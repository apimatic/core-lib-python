from typing import Any, Dict, List, Union, Optional, TypeVar

from pydantic import validate_call

T = TypeVar("T")

class ComparisonHelper:
    """A Helper Class used for the comparison of expected and actual API response."""

    @staticmethod
    @validate_call
    def match_headers(
        expected_headers: Dict[str, Optional[str]],
        received_headers: Dict[str, str],
        allow_extra: bool = True
    ) -> bool:
        """Static method to compare the received headers with the expected headers.

        Args:
            expected_headers (Dict[str, Optional[str]]): A dictionary of expected headers (keys in lower case).
            received_headers (Dict[str, str]): A dictionary of headers received.
            allow_extra (bool, optional): A flag which determines if we allow extra headers.

        Returns:
            bool: True if headers match, False otherwise.
        """
        if ((len(received_headers) < len(expected_headers)) or
                ((not allow_extra) and (len(expected_headers) != len(received_headers)))):
            return False

        received_headers = {k.lower(): v for k, v in received_headers.items()}
        for e_key in expected_headers:
            if e_key not in received_headers:
                return False
            if ((expected_headers[e_key] is not None) and
                    (expected_headers[e_key] != received_headers[e_key])):
                return False

        return True

    @staticmethod
    @validate_call
    def match_body(
        expected_body: Union[Dict[str, Any], List[Any], T],
        received_body: Union[Dict[str, Any], List[Any], T],
        check_values: bool = False,
        check_order: bool = False,
        check_count: bool = False
    ) -> bool:
        """Static method to compare the received body with the expected body.

        Args:
            expected_body (Union[Dict[str, Any], List[Any], T]): The expected body.
            received_body (Union[Dict[str, Any], List[Any], T]): The received body.
            check_values (bool, optional): A flag which determines if we check values in dictionaries.
            check_order (bool, optional): A flag which determines if we check the order of array elements.
            check_count (bool, optional): A flag which determines if we check the count of array elements.

        Returns:
            bool: True if bodies match, False otherwise.
        """
        if isinstance(expected_body, dict):
            if not isinstance(received_body, dict):
                return False
            for key in expected_body:
                if key not in received_body:
                    return False
                if check_values or isinstance(expected_body[key], dict):
                    if not ComparisonHelper.match_body(expected_body[key], received_body[key],
                                                       check_values, check_order, check_count):
                        return False
        elif isinstance(expected_body, list):
            if not isinstance(received_body, list):
                return False
            if check_count and len(expected_body) != len(received_body):
                return False
            else:
                previous_matches: List[int] = []
                for i, expected_element in enumerate(expected_body):
                    matches = [j for j, received_element in enumerate(received_body)
                               if ComparisonHelper.match_body(expected_element, received_element,
                                                              check_values, check_order, check_count)]
                    if not matches:
                        return False
                    if check_order:
                        if i != 0 and all(all(y > x for y in previous_matches) for x in matches):
                            return False
                        previous_matches = matches
        elif expected_body != received_body:
            return False
        return True
