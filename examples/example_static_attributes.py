from pydantic import BaseModel, Field
from pymocker.mocker import Mocker
from datetime import date
from polyfactory.factories.pydantic_factory import ModelFactory
class Person(BaseModel):
    firstname:str = Field(max_length=8)
    EmailAddress:str = Field(max_length=20)
    CellPhoneNumber:str = Field(max_length=15)
    HomeAddress:str = Field(max_length=100)
    WorkAddress:str = Field(max_length=100)

mocker=Mocker()
@mocker.mock()
class PersonFactory(ModelFactory[Person]):
    firstname="jane"
    
person_jane = PersonFactory.build()
print(person_jane)

