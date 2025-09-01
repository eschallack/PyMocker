from __future__ import annotations

import inspect
import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Collection, Literal, Mapping, Pattern, get_origin
from uuid import UUID

# Re-use existing validation logic where possible from polyfactory
from polyfactory.value_generators.constrained_numbers import passes_pydantic_multiple_validator

def is_valid_int(
    value: int,
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
    multiple_of: int | None = None,
) -> bool:
    """Checks if an integer value satisfies the given constraints."""
    if gt is not None and not value > gt: return False
    if ge is not None and not value >= ge: return False
    if lt is not None and not value < lt: return False
    if le is not None and not value <= le: return False
    if multiple_of is not None and not passes_pydantic_multiple_validator(value, multiple_of): return False
    return True

def is_valid_float(
    value: float,
    gt: float | None = None,
    ge: float | None = None,
    lt: float | None = None,
    le: float | None = None,
    multiple_of: float | None = None,
) -> bool:
    """Checks if a float value satisfies the given constraints."""
    if gt is not None and not value > gt: return False
    if ge is not None and not value >= ge: return False
    if lt is not None and not value < lt: return False
    if le is not None and not value <= le: return False
    if multiple_of is not None and not passes_pydantic_multiple_validator(value, multiple_of): return False
    return True

def is_valid_decimal(
    value: Decimal,
    gt: Decimal | None = None,
    ge: Decimal | None = None,
    lt: Decimal | None = None,
    le: Decimal | None = None,
    multiple_of: Decimal | None = None,
    max_digits: int | None = None,
    decimal_places: int | None = None,
) -> bool:
    """Checks if a Decimal value satisfies the given constraints."""
    if gt is not None and not value > gt: return False
    if ge is not None and not value >= ge: return False
    if lt is not None and not value < lt: return False
    if le is not None and not value <= le: return False
    if multiple_of is not None and not passes_pydantic_multiple_validator(value, multiple_of): return False

    if max_digits is not None or decimal_places is not None:
        sign, digits, exponent = value.as_tuple()
        
        if decimal_places is not None:
            if -exponent > decimal_places: return False
        
        if max_digits is not None:
            num_digits = len(digits)
            if num_digits > max_digits: return False
            if decimal_places is not None and (num_digits - decimal_places) > (max_digits - decimal_places): return False

    return True

def is_valid_string(
    value: str,
    min_length: int | None = None,
    max_length: int | None = None,
    lower_case: bool = False,
    upper_case: bool = False,
    pattern: str | Pattern | None = None,
) -> bool:
    """Checks if a string value satisfies the given constraints."""
    if min_length is not None and len(value) < min_length: return False
    if max_length is not None and len(value) > max_length: return False
    if lower_case and not value.islower(): return False
    if upper_case and not value.isupper(): return False
    if pattern and not re.match(pattern, value): return False
    return True

def is_valid_bytes(
    value: bytes,
    min_length: int | None = None,
    max_length: int | None = None,
    lower_case: bool = False,
    upper_case: bool = False,
) -> bool:
    """Checks if a bytes value satisfies the given constraints."""
    if min_length is not None and len(value) < min_length: return False
    if max_length is not None and len(value) > max_length: return False
    # Note: islower/isupper on bytes only works for ASCII
    if lower_case and not value.islower(): return False
    if upper_case and not value.isupper(): return False
    return True

def is_valid_collection(
    value: Collection[Any],
    min_items: int | None = None,
    max_items: int | None = None,
    unique_items: bool = False,
) -> bool:
    """Checks if a collection (list, set, frozenset) satisfies the given constraints."""
    if min_items is not None and len(value) < min_items: return False
    if max_items is not None and len(value) > max_items: return False
    if unique_items and len(set(value)) != len(value): return False
    return True

def is_valid_mapping(
    value: Mapping[Any, Any],
    min_items: int | None = None,
    max_items: int | None = None,
) -> bool:
    """Checks if a mapping (dict) satisfies the given constraints."""
    if min_items is not None and len(value) < min_items: return False
    if max_items is not None and len(value) > max_items: return False
    return True

def is_valid_date(
    value: date,
    gt: date | None = None,
    ge: date | None = None,
    lt: date | None = None,
    le: date | None = None,
) -> bool:
    """Checks if a date value satisfies the given constraints."""
    if gt is not None and not value > gt: return False
    if ge is not None and not value >= ge: return False
    if lt is not None and not value < lt: return False
    if le is not None and not value <= le: return False
    return True

def is_valid_uuid(
    value: UUID,
    version: Literal[1, 3, 4, 5] | None = None,
) -> bool:
    """Checks if a UUID value satisfies the given constraints."""
    if version is not None and value.version != version: return False
    return True

def is_valid_path(
    value: Path,
    constraint: Literal["file", "dir", "new"] | None = None,
) -> bool:
    """Checks if a Path value satisfies the given constraints."""
    if constraint == "file":
        return value.is_file()
    if constraint == "dir":
        return value.is_dir()
    if constraint == "new":
        return not value.exists()
    return True

VALIDATOR_MAP = {
    int: is_valid_int,
    float: is_valid_float,
    Decimal: is_valid_decimal,
    str: is_valid_string,
    bytes: is_valid_bytes,
    list: is_valid_collection,
    set: is_valid_collection,
    frozenset: is_valid_collection,
    dict: is_valid_mapping,
    date: is_valid_date,
    UUID: is_valid_uuid,
    Path: is_valid_path,
}

def is_valid(value: Any, annotation: Any, **constraints: Any) -> bool:
    """
    Dynamically selects and applies the correct validator for a given type annotation.

    :param value: The value to validate.
    :param annotation: The type annotation (e.g., int, list[str]).
    :param constraints: The keyword arguments for the constraints to check.
    :return: True if the value is valid, False otherwise.
    """
    origin_type = get_origin(annotation) or annotation
    validator = VALIDATOR_MAP.get(origin_type)

    if validator:
        # Filter constraints to only those relevant for the specific validator
        # to prevent passing an invalid keyword argument.
        sig = inspect.signature(validator)
        valid_keys = {p.name for p in sig.parameters.values()}
        relevant_constraints = {k: v for k, v in constraints.items() if k in valid_keys}
        
        return validator(value, **relevant_constraints)
    return True

