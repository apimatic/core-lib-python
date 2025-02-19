from typing import Dict, BinaryIO, IO
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
import requests
from pydantic import validate_call


class FileHelper:
    """A Helper Class for files.

    Attributes:
        cache (Dict[str, BinaryIO]): Class variable which stores references to temporary files
            for file URLs so the same file isn't downloaded multiple times in a session.
    """

    cache: Dict[str, IO[bytes]] = {}

    @classmethod
    @validate_call
    def get_file(cls, url: str) -> IO[bytes]:
        """Class method to download a file from a URL (if not already downloaded) and return its file object.

        Args:
            url (str): The URL of the required file.

        Returns:
            BinaryIO: A temporary file object opened in read-binary mode.
        """
        if url not in cls.cache:
            # Download the file and store it in a named temporary file
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            temp_file = NamedTemporaryFile(delete=False, mode='w+b')  # Explicitly open in write-binary mode
            temp_file.write(response.content)
            temp_file.flush()  # Ensure all content is written to disk
            cls.cache[url] = temp_file

        # Reset the file pointer before returning the file
        cls.cache[url].seek(0)
        return cls.cache[url]
