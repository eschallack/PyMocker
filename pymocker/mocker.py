import sys
import os

from polyfactory.factories.base import BaseFactory
try:
    # pydantic v1
    from pydantic import BaseModel as BaseModelV1

    # Keep this import last to prevent warnings from pydantic if pydantic v2
    # is installed.
    from pydantic.fields import (  # type: ignore[attr-defined]
        Undefined,  # pyright: ignore[attr-defined,reportAttributeAccessIssue]
    )

    # prevent unbound variable warnings
    BaseModelV2 = BaseModelV1
    UndefinedV2 = Undefined
except ImportError:
    # pydantic v2

    # v2 specific imports
    from pydantic_core import PydanticUndefined as UndefinedV2
    from pydantic.v1 import BaseModel as BaseModelV1  # type: ignore[assignment]
from faker import Faker
from typing import Type
from pymocker.builder.mixins import PolyfactoryLogicMixin
from pymocker.builder.rank import rank
from pymocker.builder.utils import get_return_type, segment_and_join_word
import types
from functools import wraps

def add_passthrough_args_to_object_method(obj:object, attr_name) -> object:
    attr = getattr(obj, attr_name)
    if isinstance(attr, types.MethodType):
        method = attr
        @wraps(method)
        def wrapper(*args,**kwargs):
            return method()
        setattr(obj,attr_name,wrapper)
    return obj
class Mocker:
    class Config:
        
        # - __match_field_generation_on_cosine_similarity__ -
        # If set to True, use cosine similarity to match generation methods to fields
        # based on __confidence_threshold__. This is the last in a number of matching
        # techniques Mocker will try (exact match, convert to snake case and match, exact match on type)
        # setting __confidence_threshold__ to 0 disables this behavior entirely.
        match_field_generation_on_cosine_similarity:bool = True
        
        # - confidence_threshold -
        # Confidence threshold for cosine similarity metch between generation methods and field names.
        # setting to 0 disables this behavior.
        confidence_threshold:float = 0.5
        
        # - max_retries -
        # The number of times faker will attempt to generate a constraint fuffilling value.
        # Higher values will greatly affect performance.
        max_retries:int = 300
        
        # - coerce_on_fail -
        # If set to True, coerce value to match constrains on faker generation failure.
        coerce_on_fail:bool = True
        
        provider_instances:list[object] = [Faker()]
    
    def __init__(self):
        pass
    def mock(self, **kwargs):
        """
        A decorator that enhances a polyfactory factory with automatic data generation.
        """
        def decorator(factory_class: Type[BaseFactory]):
            if issubclass(factory_class, PolyfactoryLogicMixin):
                new_factory_class = factory_class
            else:
                new_factory_class = type(
                    factory_class.__name__,
                    (PolyfactoryLogicMixin, factory_class),
                    {}
                )

            config_vars = [attr for attr in dir(self.Config) if not attr.startswith('__') and not attr.endswith('__')]
            for attr in config_vars:
                if not hasattr(new_factory_class, attr):
                    setattr(new_factory_class, attr, getattr(self.Config, attr))

            for key, value in kwargs.items():
                setattr(new_factory_class, f"__{key}__", value)

            self.add_methods_to_cls(new_factory_class)
            
            return new_factory_class

        return decorator
    
    def lookup_method_from_instances(self, field_name: str, field_type: Type = None, confidence_threshold: float = 0.75, rank_match=True):
        """
        Gets all callable methods from the instances provided to Config.
        The first condition that matches the search criteria will be returned.
        Control the search order by the index order of provider_instances.

        SEARCH LOGIC is rule-based:
        1. Exact match on field_name.
        2. Match on snake_cased field_name.
        3. Match based on cosine similarity of field name and method names.
        """
        def _find_exact_match(obj, name):
            if hasattr(obj, name):
                return getattr(obj, name)
            return None

        def _find_snake_case_match(obj, name):
            lookup_name = segment_and_join_word(name)
            if hasattr(obj, lookup_name):
                return getattr(obj, lookup_name)
            return None

        def _find_cosine_similarity_match(obj, name, f_type, conf_thresh, r_match):
            if not (r_match and conf_thresh > 0):
                return None

            lookup_name = segment_and_join_word(name)
            methods = []
            obj_method_names = [method_name for method_name in dir(obj) if not method_name.startswith('_')]
            for method_name in obj_method_names:
                try:
                    func = getattr(obj, method_name)
                    if not callable(func):
                        continue
                    
                    rtype = get_return_type(func, find_by_executing_method=True)
                    if not (rtype == f_type or f_type is None):
                        continue

                    methods.append({'name': method_name})
                except TypeError:
                    continue

            if not methods:
                return None

            ranked_methods = rank([m['name'] for m in methods], lookup_name)
            if ranked_methods and ranked_methods[0][1][0] >= conf_thresh:
                return getattr(obj, ranked_methods[0][0])
            
            return None

        rules = [
            lambda obj: _find_exact_match(obj, field_name),
            lambda obj: _find_snake_case_match(obj, field_name),
            lambda obj: _find_cosine_similarity_match(obj, field_name, field_type, confidence_threshold, rank_match)
        ]

        for obj in self.Config.provider_instances:
            for rule in rules:
                method = rule(obj)
                if method:
                    return method
        return None

    def add_methods_to_cls(self, obj: Type[BaseFactory]):
        """
        A class decorator that finds all public methods on a Faker
        instance and adds them to the decorated class.
        """
        obj=obj
        mfs = obj.get_model_fields()
        for field_meta in mfs:
            if hasattr(obj, field_meta.name) and not hasattr(BaseFactory, field_meta.name):
                continue

            method = self.lookup_method_from_instances(
                field_meta.name,
                field_type=field_meta.annotation,
                confidence_threshold=self.Config.confidence_threshold,
                rank_match=self.Config.match_field_generation_on_cosine_similarity
            )
            if method:
                setattr(obj, field_meta.name, method)
        return obj
