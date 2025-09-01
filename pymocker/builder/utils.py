import re
import inspect
from typing import Any
from wordsegment import load, segment
load()

def segment_and_join_word(word:str, sep:str='_'):
    return sep.join(segment(word)).lower()

def get_return_type(func: callable,find_by_executing_method=False) -> Any:
    """A helper to safely get the return type annotation of a function."""
    try:
        sig = inspect.signature(func)
        rtype=sig.return_annotation
        if rtype is sig.empty and not find_by_executing_method:
            rtype=Any
        elif rtype is sig.empty and find_by_executing_method:
            rtype=type(func())
        return rtype
    except (ValueError, TypeError):
        return Any
    
def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()