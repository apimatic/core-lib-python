from io import BufferedIOBase, TextIOWrapper

from pydantic import BaseModel, validate_call
from typing import Optional, Union, TextIO, BinaryIO

FileType = Union[TextIO, BinaryIO, TextIOWrapper, BufferedIOBase]

class FileWrapper(BaseModel):
    """A wrapper to allow passing in content type for file uploads."""

    file_stream: FileType
    content_type: Optional[str] = None

    model_config = {
        "arbitrary_types_allowed": True
    }

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, file_stream: FileType,
                 content_type: Optional[str]=None) -> None:
        super().__init__(file_stream=file_stream, content_type=content_type)
