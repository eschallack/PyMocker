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
from pymocker import Mocker

class Person(BaseModel):
    first_name:constr(max_length=5)
    last_name:constr(max_length=5)

peeFactory=Mocker.add(Person)
inst=peeFactory.build()
print(inst)
# person_instance = PersonFactory.build()
# pprint(person_instance)

