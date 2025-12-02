"""TODO."""

from typing import Annotated, Any

from pydantic import BeforeValidator
from upath import UPath


def parse_upath(value: Any) -> UPath:
    """TODO."""
    if isinstance(value, UPath):
        return value
    return UPath(str(value))


UPathField = Annotated[UPath, BeforeValidator(parse_upath)]
