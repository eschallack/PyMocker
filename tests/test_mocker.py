
import pytest
from pydantic import BaseModel
from dataclasses import dataclass, field
from typing import TypedDict, List

from pymocker.mocker import Mocker, MethodFinder
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.typed_dict_factory import TypedDictFactory

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

def test_mocker_creates_pydantic_factory():
    """Tests that Mocker can be subclassed to create a ModelFactory for a Pydantic model."""
    class MyPydanticModelFactory(Mocker):
        __model__ = MyPydanticModel
    assert issubclass(MyPydanticModelFactory, ModelFactory)
    assert MyPydanticModelFactory.__model__ == MyPydanticModel

def test_mocker_creates_dataclass_factory():
    """Tests that Mocker can be subclassed to create a DataclassFactory for a dataclass."""
    class MyDataclassFactory(Mocker):
        __model__ = MyDataclass
    assert issubclass(MyDataclassFactory, DataclassFactory)
    assert MyDataclassFactory.__model__ == MyDataclass

def test_mocker_creates_typed_dict_factory():
    """Tests that Mocker can be subclassed to create a TypedDictFactory for a TypedDict."""
    class MyTypedDictFactory(Mocker):
        __model__ = MyTypedDict
    assert issubclass(MyTypedDictFactory, TypedDictFactory)
    assert MyTypedDictFactory.__model__ == MyTypedDict

def test_mocker_raises_type_error_for_unsupported_type():
    """Tests that Mocker raises a TypeError for an unsupported class."""
    with pytest.raises(TypeError):
        class UnsupportedFactory(Mocker):
            __model__ = UnsupportedClass

def test_factory_builds_pydantic_instance():
    """Tests that the generated factory can build an instance of the Pydantic model."""
    class MyPydanticModelFactory(Mocker):
        __model__ = MyPydanticModel
    instance = MyPydanticModelFactory.build()
    assert isinstance(instance, MyPydanticModel)
    assert isinstance(instance.id, int)
    assert isinstance(instance.name, str)
    assert isinstance(instance.first_name, str)


def test_factory_builds_dataclass_instance():
    """Tests that the generated factory can build an instance of the dataclass."""
    class MyDataclassFactory(Mocker):
        __model__ = MyDataclass
    instance = MyDataclassFactory.build()
    assert isinstance(instance, MyDataclass)
    assert isinstance(instance.id, int)
    assert isinstance(instance.name, str)

def test_factory_builds_typed_dict_instance():
    """Tests that the generated factory can build an instance of the TypedDict."""
    class MyTypedDictFactory(Mocker):
        __model__ = MyTypedDict
    instance = MyTypedDictFactory.build()
    assert isinstance(instance, dict)
    assert "id" in instance
    assert "name" in instance
    assert isinstance(instance['id'], int)
    assert isinstance(instance['name'], str)


# 3. Tests for MethodFinder class

def test_method_finder_direct_hit():
    """Tests that get_faker_method finds a method with an exact name match."""
    method = MethodFinder.get_faker_method("name", str)
    assert callable(method)
    assert method.__name__ == "name"

def test_method_finder_segmented_hit():
    """Tests that get_faker_method finds a method by segmenting the field name."""
    method = MethodFinder.get_faker_method("first_name", str)
    assert callable(method)
    # The faker method for 'first_name' is just 'first_name'
    assert method.__name__ == "first_name"

def test_method_finder_ranked_hit():
    """
    Tests that get_faker_method finds a method using semantic ranking
    when no direct or segmented match is found.
    """
    # 'full_name' doesn't exist, but 'name' is semantically similar.
    Mocker.__confidence_threshold__ = 0.5 # Lower threshold for test
    method = MethodFinder.get_faker_method("full_name", str)
    assert callable(method)
    assert method.__name__ == "last_name"
    Mocker.__confidence_threshold__ = 0.75 # Reset threshold

def test_method_finder_returns_none_for_no_match():
    """
    Tests that get_faker_method returns None when no suitable method is found.
    """
    Mocker.__confidence_threshold__ = 0.99 # Set a high threshold
    method = MethodFinder.get_faker_method("a_very_unlikely_field_name_to_exist", str)
    assert method is None
    Mocker.__confidence_threshold__ = 0.75 # Reset threshold

def test_add_methods_to_cls_decorator():
    """
    Tests that the add_methods_to_cls decorator correctly
    attaches faker methods to the factory class.
    """
    class MyPydanticModelFactory(Mocker):
        __model__ = MyPydanticModel
    factory = MyPydanticModelFactory
    # 'name' should be found directly
    assert hasattr(factory, "name")
    assert callable(factory.name)

    # 'first_name' should be found via segmentation
    assert hasattr(factory, "first_name")
    assert callable(factory.first_name)
