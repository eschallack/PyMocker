from pydantic import BaseModel, constr
from pymocker.mocker import Mocker
from datetime import date
from polyfactory.factories.pydantic_factory import ModelFactory
class Person(BaseModel):
    firstname: constr(max_length=8)
    EmailAddress: constr(max_length=20)
    CellPhoneNumber: constr(max_length=15)
    HomeAddress:constr(max_length=100)
    WorkAddress:constr(max_length=100)

mocker=Mocker()
@mocker.mock()
class PersonFactory(ModelFactory[Person]):
    firstname="jane"
    
person_jane = PersonFactory.build()
print(person_jane)