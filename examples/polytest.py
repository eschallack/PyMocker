import sys
import os
submodule_paths = [os.path.join(os.path.dirname(__file__), '..', 'submodules/polyfactory')]
for submodule_path in submodule_paths:
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)
from pydantic import BaseModel, constr
from pymocker.mocker import Mocker
from datetime import date
class Person(BaseModel):
    firstname: constr(max_length=8)
    birthdate: date
    EmailAddress: constr(max_length=20)
    CellPhoneNumber: constr(max_length=15)
    HomeAddress:constr(max_length=100)
    WorkAddress:constr(max_length=100)

Mocker.__confidence_threshold__ = .75
class PersonWithStaticFirstNameFactory(Mocker):
    __model__ = Person
    firstname = "Jane"
person_jane = PersonWithStaticFirstNameFactory.build()
print(person_jane)
