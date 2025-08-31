import sys
import os
submodule_paths = [os.path.join(os.path.dirname(__file__), '..', 'submodules/polyfactory')]
for submodule_path in submodule_paths:
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)
from polyfactory import BaseFactory
from polyfactory.factories import DataclassFactory, TypedDictFactory
from pydantic import BaseModel
from pprint import pprint
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from datetime import date
from pydantic import BaseModel, constr
from enum import Enum
from faker import Faker
from dataclasses import is_dataclass
from typing import get_origin
from pymocker.builder.mixins import PolyfactoryLogicMixin
class Mocker:
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

        @add_faker_methods
        class _Factory(PolyfactoryLogicMixin,base_factory[cls]):  # type: ignore
            __model__ = cls

        _Factory.__name__ = factory_name

        setattr(Mocker, factory_name, _Factory)
        return getattr(Mocker,factory_name)
    
def add_faker_methods(cls):
    """
    A class decorator that finds all public methods on a Faker
    instance and adds them to the decorated class.
    """
    _faker = Faker()
    for name in dir(_faker):
        if not name.startswith('_') and not name.startswith('seed') and callable(getattr(_faker, name)):
            attr = getattr(_faker, name)
            setattr(cls, name, attr)
    return cls

class pee(BaseModel):
    first_name:constr(max_length=5)
    last_name:constr(max_length=5)

peeFactory=Mocker.add(pee)
inst=peeFactory.build()
print(inst)
# person_instance = PersonFactory.build()
# pprint(person_instance)

