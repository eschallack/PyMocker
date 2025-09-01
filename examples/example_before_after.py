from pydantic import BaseModel, Field
from pymocker.mocker import Mocker
from polyfactory.factories.pydantic_factory import ModelFactory
from pprint import pprint
class Person(BaseModel):
    FirstName:str= Field(max_length=8)
    EmailAddress:str= Field(max_length=20)
    CellPhoneNumber:str= Field(min_length=12,max_length=12)

# without mocker
class PersonFactory(ModelFactory[Person]):...
person = PersonFactory.build()
print(f"Polyfactory:")
pprint(person)

# with mocker
mocker=Mocker()
mocker.Config.confidence_threshold = .5
@mocker.mock()
class MockerPersonFactory(ModelFactory[Person]):...
mocker_person = MockerPersonFactory.build()
print("Polyfactory + Mocker:")
pprint(mocker_person)
