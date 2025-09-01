import sys
import os
submodule_paths = [os.path.join(os.path.dirname(__file__), '..', 'submodules/polyfactory')]
for submodule_path in submodule_paths:
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)

from polyfactory.factories.base import BaseFactory
from polyfactory.factories import DataclassFactory, TypedDictFactory
from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from faker import Faker
from dataclasses import is_dataclass
from typing import get_origin, Type
from pymocker.builder.mixins import PolyfactoryLogicMixin
from pymocker.builder.rank import rank
from pymocker.builder.utils import get_return_type, segment_and_join_word



class MockerMeta(type):
    def __new__(mcs, name, bases, dct):
        if dct.get("__is_base_factory__"):
            return super().__new__(mcs, name, bases, dct)

        model = dct.get('__model__')
        if not model:
            return super().__new__(mcs, name, bases, dct)

        # Determine the correct polyfactory base
        if issubclass(model, BaseModel):
            base_factory = ModelFactory
        elif is_dataclass(model):
            base_factory = DataclassFactory
        elif hasattr(model, "__table__"):
            base_factory = SQLAlchemyFactory
        elif get_origin(model) is dict or (isinstance(model, type) and issubclass(model, dict) and hasattr(model, "__annotations__")):
            base_factory = TypedDictFactory
        else:
            raise TypeError(f"Unsupported model type: {model}")

        kwargs_for_factory = {
            k: v for k, v in dct.items() 
            if k not in ('__model__', '__module__', '__qualname__')
        }

        factory_class = base_factory.create_factory(
            model,
            bases=(PolyfactoryLogicMixin,),
            **kwargs_for_factory
        )
        
        return MethodFinder.add_methods_to_cls(factory_class)

class Mocker(metaclass=MockerMeta):
    __is_base_factory__ = True

    # - __match_field_generation_on_cosine_similarity__ -
    # If set to True, use cosine similarity to match generation methods to fields
    # based on __confidence_threshold__. This is the last in a number of matching
    # techniques Mocker will try (exact match, convert to snake case and match, exact match on type)
    # setting __confidence_threshold__ to 0 disables this behavior entirely.
    __match_field_generation_on_cosine_similarity__ = True
    
    # - __confidence_threshold__ -
    # Confidence threshold for cosine similarity metch between generation methods and field names.
    # setting to 0 disables this behavior.
    __confidence_threshold__: float = 0.75
    
    # - __max_retries__ -
    # The number of times faker will attempt to generate a constraint fuffilling value.
    # Higher values will greatly affect performance.
    __max_retries__ = 300
    
    # - __coerce_on_fail__ -
    # If set to True, coerce value to match constrains on faker generation failure.
    __coerce_on_fail__ = True
    


class MethodFinder:
    @classmethod
    def get_faker_method(cls:Mocker, field_name: str, field_type: Type = None, filter_methods: list = [rank], confidence_threshold: float = 0.75, rank_match=True):
        """Gets all callable methods from a Faker instance."""
        faker = Faker()
        excluded = {'add_provider', 'get_providers', 'seed', 'seed_instance', 'seed_locale'}
        if hasattr(faker, field_name):
            return getattr(faker, field_name)

        lookup_name = segment_and_join_word(field_name)
        if hasattr(faker, lookup_name):
            return getattr(faker, lookup_name)
        else:
            methods = [
                {
                    'name': name,
                    'func': func,
                    'type': get_return_type(func)
                }
                for name in dir(faker)
                if not name.startswith('_')
                and name not in excluded
                and callable(func := getattr(faker, name))
                and (get_return_type(func) == field_type or field_type is None)
            ]
            if not methods:
                return None
            elif len(methods) == 1:
                return methods[0]['func']
            elif rank_match == True and confidence_threshold != 0:
                ranked_methods = rank([m['name'] for m in methods], lookup_name)
                if ranked_methods and ranked_methods[0][1][0] >= confidence_threshold:
                    return getattr(faker, ranked_methods[0][0])
            return None

    @classmethod
    def add_methods_to_cls(cls, factory_obj: Type[BaseFactory]):
        """
        A class decorator that finds all public methods on a Faker
        instance and adds them to the decorated class.
        """
        for field_meta in factory_obj.get_model_fields():
            if hasattr(factory_obj, field_meta.name) and not hasattr(BaseFactory, field_meta.name):
                continue

            method = cls.get_faker_method(
                field_meta.name,
                field_type=field_meta.annotation,
                filter_methods=[rank],
                confidence_threshold=Mocker.__confidence_threshold__,
                rank_match=Mocker.__match_field_generation_on_cosine_similarity__
            )
            if method:
                setattr(factory_obj, field_meta.name, method)
        return factory_obj