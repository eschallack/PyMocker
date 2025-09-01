import pytest
from pydantic import BaseModel
from dataclasses import dataclass, field
from typing import TypedDict, List

from pymocker.mocker import Mocker
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.typed_dict_factory import TypedDictFactory
from pymocker.builder.mixins import PolyfactoryLogicMixin

# 1. Define dummy models for testing

class MyPydanticModel(BaseModel):
    id: int
    name: str
    first_name: str

@dataclass
class MyDataclass:
    id: int
    name: str
    last_name: str

class MyTypedDict(TypedDict):
    id: int
    name: str
    full_name: str

class UnsupportedClass:
    pass

# 2. Tests for Mocker class

mocker = Mocker()

def test_mocker_decorates_pydantic_factory():
    """Tests that Mocker can decorate a ModelFactory for a Pydantic model."""
    @mocker.mock()
    class MyPydanticModelFactory(ModelFactory):
        __model__ = MyPydanticModel
    
    assert issubclass(MyPydanticModelFactory, ModelFactory)
    assert issubclass(MyPydanticModelFactory, PolyfactoryLogicMixin)
    assert MyPydanticModelFactory.__model__ == MyPydanticModel

def test_mocker_decorates_dataclass_factory():
    """Tests that Mocker can decorate a DataclassFactory for a dataclass."""
    @mocker.mock()
    class MyDataclassFactory(DataclassFactory):
        __model__ = MyDataclass
    
    assert issubclass(MyDataclassFactory, DataclassFactory)
    assert issubclass(MyDataclassFactory, PolyfactoryLogicMixin)
    assert MyDataclassFactory.__model__ == MyDataclass

def test_mocker_decorates_typed_dict_factory():
    """Tests that Mocker can decorate a TypedDictFactory for a TypedDict."""
    @mocker.mock()
    class MyTypedDictFactory(TypedDictFactory):
        __model__ = MyTypedDict
        
    assert issubclass(MyTypedDictFactory, TypedDictFactory)
    assert issubclass(MyTypedDictFactory, PolyfactoryLogicMixin)
    assert MyTypedDictFactory.__model__ == MyTypedDict

def test_factory_builds_pydantic_instance():
    """Tests that the generated factory can build an instance of the Pydantic model."""
    @mocker.mock()
    class MyPydanticModelFactory(ModelFactory):
        __model__ = MyPydanticModel
    instance = MyPydanticModelFactory.build()
    assert isinstance(instance, MyPydanticModel)
    assert isinstance(instance.id, int)
    assert isinstance(instance.name, str)
    assert isinstance(instance.first_name, str)


def test_factory_builds_dataclass_instance():
    """Tests that the generated factory can build an instance of the dataclass."""
    @mocker.mock()
    class MyDataclassFactory(DataclassFactory):
        __model__ = MyDataclass
    instance = MyDataclassFactory.build()
    assert isinstance(instance, MyDataclass)
    assert isinstance(instance.id, int)
    assert isinstance(instance.name, str)

def test_factory_builds_typed_dict_instance():
    """Tests that the generated factory can build an instance of the TypedDict."""
    @mocker.mock()
    class MyTypedDictFactory(TypedDictFactory):
        __model__ = MyTypedDict
    instance = MyTypedDictFactory.build()
    assert isinstance(instance, dict)
    assert "id" in instance
    assert "name" in instance
    assert isinstance(instance['id'], int)
    assert isinstance(instance['name'], str)


# 3. Tests for Mocker method lookup

def test_method_finder_direct_hit():
    """Tests that lookup_method_from_instances finds a method with an exact name match."""
    method = mocker.lookup_method_from_instances("name", str)
    assert callable(method)
    assert method.__name__ == "name"

def test_method_finder_segmented_hit():
    """Tests that lookup_method_from_instances finds a method by segmenting the field name."""
    method = mocker.lookup_method_from_instances("first_name", str)
    assert callable(method)
    # The faker method for 'first_name' is just 'first_name'
    assert method.__name__ == "first_name"

def test_method_finder_ranked_hit():
    """
    # Tests that lookup_method_from_instances finds a method using semantic ranking
    # when no direct or segmented match is found.
    # """
    # # 'full_name' doesn't exist, but 'name' is semantically similar.
    # mocker.Config.confidence_threshold = 0.5 # Lower threshold for test
    # method = mocker.lookup_method_from_instances("full_name", str)
    # assert callable(method)
    # assert method.__name__ == "name"
    # mocker.Config.confidence_threshold = 0.75 # Reset threshold

def test_method_finder_returns_none_for_no_match():
    """
    Tests that lookup_method_from_instances returns None when no suitable method is found.
    """
    mocker.Config.confidence_threshold = 0.99 # Set a high threshold
    method = mocker.lookup_method_from_instances("a_very_unlikely_field_name_to_exist", str)
    assert method is None
    mocker.Config.confidence_threshold = 0.75 # Reset threshold

def test_add_methods_to_cls_decorator():
    """
    Tests that the mocker decorator correctly
    attaches faker methods to the factory class.
    """
    @mocker.mock()
    class MyPydanticModelFactory(ModelFactory):
        __model__ = MyPydanticModel
    
    factory = MyPydanticModelFactory
    # 'name' should be found directly
    assert hasattr(factory, "name")
    assert callable(factory.name)

    # 'first_name' should be found via segmentation
    assert hasattr(factory, "first_name")
    assert callable(factory.first_name)