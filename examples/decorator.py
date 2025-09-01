from pydantic import BaseModel, constr
from pymocker.mocker import Mocker
from polyfactory.factories.pydantic_factory import ModelFactory
from datetime import date
class Person(BaseModel):
    firstname: constr(max_length=8)
    birthdate: date
    emailaddress: constr(max_length=20)
    CellPhoneNumber: constr(max_length=15)
    HomeAddress:constr(max_length=100)
    WorkAddress:constr(max_length=100)

# Mocker.__confidence_threshold__ = .75
mocker=Mocker()
mocker.Config.confidence_threshold = .5
@mocker.mock()
class PersonWithStaticFirstNameFactory(ModelFactory[Person]):...
person = PersonWithStaticFirstNameFactory.build()
print(person)
