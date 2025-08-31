
import sys
import os
submodule_paths = [os.path.join(os.path.dirname(__file__), '..', 'submodules/polyfactory')]
for submodule_path in submodule_paths:
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)
from polyfactory import BaseFactory
from polyfactory.factories import DataclassFactory, TypedDictFactory
from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from pydantic import BaseModel
from faker import Faker
from dataclasses import is_dataclass
from typing import get_origin
from pymocker.builder.mixins import PolyfactoryLogicMixin
from typing import Callable, Type, Any
from pymocker.builder.rank import rank
from pymocker.builder.utils import to_snake_case, get_return_type, segment_and_join_word
class Mocker:
    __fuzzy_find_method__ = True
    __max_retries__ = 300
    __coerce_on_fail__ = True
    @staticmethod
    def add(cls) -> BaseFactory:
        if issubclass(cls, BaseModel):
            base_factory = ModelFactory
        elif is_dataclass(cls):
            base_factory = DataclassFactory
        elif get_origin(cls) is dict or (isinstance(cls, type) and issubclass(cls, dict) and hasattr(cls, "__annotations__")):
            base_factory = TypedDictFactory
        elif hasattr(cls, "__table__"):  # SQLAlchemy declarative
            base_factory = SQLAlchemyFactory
        else:
            raise TypeError(f"Unsupported class type for factory: {cls}")

        factory_name = f"{cls.__name__}Factory"

        @MethodFinder.add_faker_methods_to_class
        class _Factory(PolyfactoryLogicMixin,base_factory[cls]):  # type: ignore
            __model__ = cls

        _Factory.__name__ = factory_name

        setattr(Mocker, factory_name, _Factory)
        return getattr(Mocker,factory_name)

class MethodFinder:
    __confidence_threshold__:str=.75 # between 0 and 1
    __method_return_annotation_matches_field_type__:True #
    method_map:dict
    model_obj:BaseModel
    @classmethod
    def get_faker_method(cls,field_name:str,field_type:Type=None, filter_methods:list=[rank]):
        """Gets all callable methods from a Faker instance."""
        faker = Faker()
        excluded = {'add_provider', 'get_providers', 'seed', 'seed_instance', 'seed_locale'}
        if hasattr(faker, field_name):
            return getattr(faker, field_name)
        
        lookup_name=segment_and_join_word(field_name)
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
            if methods == 0:
                return None
            elif len(methods) == 1:
                return methods[0]
            else:
                ranked_methods = rank([m['name'] for m in methods], lookup_name)
                if ranked_methods[0][1][0]>=cls.__confidence_threshold__:
                    return getattr(faker, ranked_methods[0][0])
            return None
    @classmethod
    def add_faker_methods_to_class(cls,factory_obj:BaseFactory):
        """
        A class decorator that finds all public methods on a Faker
        instance and adds them to the decorated class.
        """
        for i, field_meta in  enumerate(factory_obj.get_model_fields()):
            method=cls.get_faker_method(field_meta.name,
                                         field_type=field_meta.annotation,
                                         filter_methods=[rank])
            if method:
                setattr(factory_obj, field_meta.name, method)
        return factory_obj