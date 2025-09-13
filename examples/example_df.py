
from pydantic import BaseModel
from pymocker.mocker import Mocker
from polyfactory.factories.pydantic_factory import ModelFactory
import pandas as pd

class PersonModel(BaseModel):
    id:int
    firstname:str

if __name__ == '__main__':
    df = pd.DataFrame(
        columns=['id',
                 'firstname',
                 'middlename',
                 'lastname',
                 'ssn',
                 'phonenumber',
                 'address_line_1',
                 'address_line_2',
                 'company'])
    mocker=Mocker()
    rows=10
    # or go crazy!!!
    # rows=100000
    df=df.mocker.build(mocker=mocker, rows=rows)
    df.to_clipboard(index=False)