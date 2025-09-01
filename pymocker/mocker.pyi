from polyfactory.factories import DataclassFactory as DataclassFactory, TypedDictFactory as TypedDictFactory
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.pydantic_factory import ModelFactory as ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory as SQLAlchemyFactory
from pydantic.fields import Undefined
from pydantic.v1 import BaseModel as BaseModelV1
from pymocker.builder.mixins import PolyfactoryLogicMixin as PolyfactoryLogicMixin
from pymocker.builder.rank import rank as rank
from pymocker.builder.utils import get_return_type as get_return_type, segment_and_join_word as segment_and_join_word
from sympy.liealgebras.type_e import TypeE as TypeE

BaseModelV2 = BaseModelV1
UndefinedV2 = Undefined

def add_passthrough_args_to_object_method(obj: object, attr_name) -> object: ...

class Mocker:
    class Config:
        match_field_generation_on_cosine_similarity: bool
        confidence_threshold: float
        max_retries: int
        coerce_on_fail: bool
        provider_instances: list[object]
    def __init__(self) -> None: ...
    def mock(self, **kwargs): ...
    def lookup_method_from_instances(self, field_name: str, field_type: type = None, confidence_threshold: float = 0.75, rank_match: bool = True): ...
    def add_methods_to_cls(self, obj: type[BaseFactory]): ...
