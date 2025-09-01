from typing import TypeVar
from polyfactory.factories.base import BaseFactory

T = TypeVar("T")

class Mocker(BaseFactory[T]):
    # Default settings that can be overridden in subclasses
    __fuzzy_find__: bool
    __max_retries__: int
    __coerce_on_fail__: bool
    __confidence_threshold__: float