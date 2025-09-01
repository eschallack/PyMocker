import sys
import os

from sympy.liealgebras.type_e import TypeE
# submodule_paths = [os.path.join(os.path.dirname(__file__), '..', 'submodules/polyfactory')]
# for submodule_path in submodule_paths:
#     if submodule_path not in sys.path:
#         sys.path.append(submodule_path)

from polyfactory.factories.base import BaseFactory
from polyfactory.factories import DataclassFactory, TypedDictFactory
from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from faker import Faker
from dataclasses import is_dataclass
from typing import get_origin, Type,Callable
from pymocker.builder.mixins import PolyfactoryLogicMixin
from pymocker.builder.rank import rank
from pymocker.builder.utils import get_return_type, segment_and_join_word

class Mocker:
    class Config:
        # - __match_field_generation_on_cosine_similarity__ -
        # If set to True, use cosine similarity to match generation methods to fields
        # based on __confidence_threshold__. This is the last in a number of matching
        # techniques Mocker will try (exact match, convert to snake case and match, exact match on type)
        # setting __confidence_threshold__ to 0 disables this behavior entirely.
        match_field_generation_on_cosine_similarity:bool = True
        
        # - confidence_threshold -
        # Confidence threshold for cosine similarity metch between generation methods and field names.
        # setting to 0 disables this behavior.
        confidence_threshold:float = 0.5
        # - max_retries -
        # The number of times faker will attempt to generate a constraint fuffilling value.
        # Higher values will greatly affect performance.
        
        max_retries:int = 300
        
        # - coerce_on_fail -
        # If set to True, coerce value to match constrains on faker generation failure.
        coerce_on_fail:bool = True
        
        provider_instances:list[object] = []
    
    def __init__(self):
        if len(self.Config.provider_instances) == 0:
            self.Config.provider_instances.append(Faker())

    def mock(self, **kwargs):
        """
        A decorator that enhances a polyfactory factory with automatic data generation.
        """
        def decorator(factory_class: Type[BaseFactory]):
            if issubclass(factory_class, PolyfactoryLogicMixin):
                new_factory_class = factory_class
            else:
                new_factory_class = type(
                    factory_class.__name__,
                    (PolyfactoryLogicMixin, factory_class),
                    {}
                )

            config_vars = [attr for attr in dir(self.Config) if not attr.startswith('__') and not attr.endswith('__')]
            for attr in config_vars:
                if not hasattr(new_factory_class, attr):
                    setattr(new_factory_class, attr, getattr(self.Config, attr))

            for key, value in kwargs.items():
                setattr(new_factory_class, f"__{key}__", value)

            self.add_methods_to_cls(new_factory_class)
            
            return new_factory_class

        return decorator
    
    def lookup_method_from_instances(self, field_name: str, field_type: Type = None, confidence_threshold: float = 0.75, rank_match=True):
        """Gets all callable methods from the instances provided to Config.
            The first condition that matches the search criteria will be returned.
            Control the search order by the index order of provider_instances.
            
            SEARCH LOGIC:
            """
        for obj in self.Config.provider_instances:
            
            if hasattr(obj, field_name):
                return getattr(obj, field_name)
            lookup_name = segment_and_join_word(field_name)
            if hasattr(obj, lookup_name):
                return getattr(obj, lookup_name)
            else:
                methods = []
                for name in dir(obj):
                    try:
                        if name.startswith('_'):
                            continue
                        func = getattr(obj, name)
                        if not callable(func):
                            continue
                        if not (get_return_type(func) == field_type or field_type is None):
                            continue

                        methods.append({
                            'name': name,
                            'func': func,
                            'type': get_return_type(func)
                        })
                    except TypeError:
                        continue
                    
                if not methods:
                    return None
                elif len(methods) == 1:
                    return methods[0]['func']
                elif rank_match == True and confidence_threshold != 0:
                    ranked_methods = rank([m['name'] for m in methods], lookup_name)
                    if ranked_methods and ranked_methods[0][1][0] >= confidence_threshold:
                        return getattr(obj, ranked_methods[0][0])
            return None

    def add_methods_to_cls(self, factory_obj: Type[BaseFactory]):
        """
        A class decorator that finds all public methods on a Faker
        instance and adds them to the decorated class.
        """
        for field_meta in factory_obj.get_model_fields():
            if hasattr(factory_obj, field_meta.name) and not hasattr(BaseFactory, field_meta.name):
                continue

            method = self.lookup_method_from_instances(
                field_meta.name,
                field_type=field_meta.annotation,
                confidence_threshold=self.Config.confidence_threshold,
                rank_match=self.Config.match_field_generation_on_cosine_similarity
            )
            if method:
                setattr(factory_obj, field_meta.name, method)
        return factory_obj