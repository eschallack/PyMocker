
from pydantic import BaseModel, Field
from pymocker.mocker import Mocker
from polyfactory.factories.pydantic_factory import ModelFactory
from datetime import date
from faker import Faker
from pprint import pprint
import pandas as pd

class PersonModel(BaseModel):
    id:int
    firstname:str

if __name__ == '__main__':
    df = pd.read_excel(r'examples/data/testing.xlsx')
    mocker=Mocker()
    df.mocker.create(mocker)
    
    print(pyd)