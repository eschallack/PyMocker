import sys
import os
submodule_paths = [os.path.join(os.path.dirname(__file__), '..', 'submodules/polyfactory')]
for submodule_path in submodule_paths:
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)
from pydantic import BaseModel, constr

from pymocker.builder.mixins import PolyfactoryLogicMixin
from pymocker import Mocker

class Person(BaseModel):
    # first_name:constr(max_length=5)
    firstname:constr(max_length=8)
    EmailAddress:constr(max_length=20)
    CellPhoneNumber:constr(max_length=15)
    # last_name:constr(max_length=5)

peeFactory=Mocker.add(Person)
inst=peeFactory.build()
print(inst)

