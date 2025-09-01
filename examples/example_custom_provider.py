from pydantic import BaseModel, Field
from pymocker.mocker import Mocker
from polyfactory.factories.pydantic_factory import ModelFactory
from datetime import date
from faker import Faker
from pprint import pprint
class SuperHeroProvider:
    @staticmethod
    def super_hero_name():
        return 'MockerMan'
class Hero(BaseModel):
    HeroName:str=Field(max_length=9)
    
custom_faker_mocker=Mocker()
custom_faker_mocker.Config.provider_instances = [SuperHeroProvider(), Faker(locale='en_us')]

@custom_faker_mocker.mock()
class HeroFactory(ModelFactory[Hero]):...
hero = HeroFactory.build()
pprint(hero)
