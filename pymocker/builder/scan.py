import sys
import os
import inspect as insp
from typing import get_type_hints, Type, ForwardRef, get_origin
from faker import Faker
from pydantic.v1.fields import ModelField
class MockerInspector:
    """Methods for discovering types of functions, classes
    """
    def scan_methods(cls, filter_on:Type=None):
        """Scan a base class for all methods and capture their return types."""
        instance = cls()
        results = {}
        exclude_attrs = ['add_provider', 'get_providers','get_']
        for attr in dir(instance):
            if attr.startswith("_") or attr in exclude_attrs:
                continue
            try:
                member = getattr(instance, attr)
            except TypeError:
                continue
            if insp.isfunction(member) or insp.ismethod(member):
                try:
                    hints = get_type_hints(member)
                    ret_type = hints.get("return", insp.signature(member).return_annotation)
                except Exception:
                    ret_type = insp.signature(member).return_annotation
                if ret_type is insp._empty or ret_type is type(None):
                    break
                if not filter_on:
                    results[member] = ret_type
                elif filter_on and ret_type == filter_on:
                    results[member] = ret_type
        return results
    def get_base_type(field:ModelField):
        try:
            return get_origin(field.type_)
        except AttributeError:
            return get_origin(field.annotation)