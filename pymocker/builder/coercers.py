from __future__ import annotations

import inspect
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Collection, get_origin, Type, TypeVar
from uuid import UUID, uuid1, uuid3, uuid4, uuid5, NAMESPACE_DNS

T = TypeVar("T")


def _coerce_numeric(value: T, gt: T | None = None, ge: T | None = None, lt: T | None = None, le: T | None = None) -> T:
    """Helper to apply boundary constraints to any numeric type."""
    if ge is not None and value < ge: value = ge
    if gt is not None and value <= gt: value = gt + (1 if isinstance(value, int) else type(value)("1e-9"))
    if le is not None and value > le: value = le
    if lt is not None and value >= lt: value = lt - (1 if isinstance(value, int) else type(value)("1e-9"))
    return value

def coerce_int(value: int, gt: int | None = None, ge: int | None = None, lt: int | None = None, le: int | None = None, multiple_of: int | None = None) -> int:
    """Applies constraints to an integer value."""
    value = _coerce_numeric(value, gt, ge, lt, le)
    
    if multiple_of is not None and value % multiple_of != 0:
        value = round(value / multiple_of) * multiple_of
        # Re-check bounds after applying multiple_of
        value = _coerce_numeric(value, gt, ge, lt, le)

    if (ge is not None and value < ge) or (gt is not None and value <= gt) or \
       (le is not None and value > le) or (lt is not None and value >= lt):
        raise ValueError(f"Cannot coerce int to satisfy conflicting constraints: gt={gt}, ge={ge}, lt={lt}, le={le}")
        
    return value

def coerce_float(value: float, gt: float | None = None, ge: float | None = None, lt: float | None = None, le: float | None = None, multiple_of: float | None = None) -> float:
    """Applies constraints to a float value."""
    value = _coerce_numeric(value, gt, ge, lt, le)

    if multiple_of is not None:
        mod = value % multiple_of
        if not (abs(mod) < 1e-9 or abs(mod - multiple_of) < 1e-9):
             value = round(value / multiple_of) * multiple_of
             value = _coerce_numeric(value, gt, ge, lt, le)
    
    if (ge is not None and value < ge) or (gt is not None and value <= gt) or \
       (le is not None and value > le) or (lt is not None and value >= lt):
        raise ValueError(f"Cannot coerce float to satisfy conflicting constraints: gt={gt}, ge={ge}, lt={lt}, le={le}")

    return value

def coerce_decimal(value: Decimal, gt: Decimal | None = None, ge: Decimal | None = None, lt: Decimal | None = None, le: Decimal | None = None, multiple_of: Decimal | None = None, decimal_places: int | None = None, **kwargs) -> Decimal:
    """Applies constraints to a Decimal value."""
    if decimal_places is not None:
        value = value.quantize(Decimal('1e-' + str(decimal_places)))

    value = _coerce_numeric(value, gt, ge, lt, le)

    if multiple_of is not None and value % multiple_of != 0:
        value = (value / multiple_of).to_integral_value(rounding="ROUND_HALF_UP") * multiple_of
        value = _coerce_numeric(value, gt, ge, lt, le)

    if (ge is not None and value < ge) or (gt is not None and value <= gt) or \
       (le is not None and value > le) or (lt is not None and value >= lt):
        raise ValueError(f"Cannot coerce Decimal to satisfy conflicting constraints: gt={gt}, ge={ge}, lt={lt}, le={le}")

    return value

def coerce_string(value: str, min_length: int | None = None, max_length: int | None = None, lower_case: bool = False, upper_case: bool = False, **kwargs) -> str:
    """Applies constraints to a string value. Note: pattern coercion is not supported."""
    if lower_case: value = value.lower()
    if upper_case: value = value.upper()

    if min_length is not None and len(value) < min_length:
        value = value.ljust(min_length, '#')
    if max_length is not None and len(value) > max_length:
        value = value[:max_length]
    return value

def coerce_bytes(value: bytes, min_length: int | None = None, max_length: int | None = None, lower_case: bool = False, upper_case: bool = False, **kwargs) -> bytes:
    """Applies constraints to a bytes value."""
    if lower_case: value = value.lower()
    if upper_case: value = value.upper()

    if min_length is not None and len(value) < min_length:
        value += b'#' * (min_length - len(value))
    if max_length is not None and len(value) > max_length:
        value = value[:max_length]
    return value

def coerce_collection(value: Collection[Any], min_items: int | None = None, max_items: int | None = None, unique_items: bool = False, **kwargs) -> Collection[Any]:
    """Applies constraints to a collection."""
    original_type = type(value)
    value_list = list(value)

    if unique_items:
        value_list = list(dict.fromkeys(value_list))

    if min_items is not None and len(value_list) < min_items:
        filler = [value_list[-1]] if value_list else [None]
        value_list.extend(filler * (min_items - len(value_list)))
    
    if max_items is not None and len(value_list) > max_items:
        value_list = value_list[:max_items]

    if original_type is set: return set(value_list)
    if original_type is frozenset: return frozenset(value_list)
    return value_list

def coerce_mapping(value: dict[Any, Any], min_items: int | None = None, max_items: int | None = None, **kwargs) -> dict[Any, Any]:
    """Applies constraints to a mapping."""
    if min_items is not None and len(value) < min_items:
        for i in range(min_items - len(value)):
            value[f"coerced_key_{i}"] = None
    
    if max_items is not None and len(value) > max_items:
        value = dict(list(value.items())[:max_items])
        
    return value

def coerce_date(value: date, gt: date | None = None, ge: date | None = None, lt: date | None = None, le: date | None = None, **kwargs) -> date:
    """Applies constraints to a date value."""
    if ge is not None and value < ge: return ge
    if gt is not None and value <= gt: return gt + timedelta(days=1)
    if le is not None and value > le: return le
    if lt is not None and value >= lt: return lt - timedelta(days=1)
    return value

def coerce_uuid(value: UUID, version: int | None = None, **kwargs) -> UUID:
    """Coerces a UUID to a specific version by generating a new one."""
    if version is not None and value.version != version:
        if version == 1: return uuid1()
        if version == 3: return uuid3(NAMESPACE_DNS, str(value))
        if version == 4: return uuid4()
        if version == 5: return uuid5(NAMESPACE_DNS, str(value))
    return value

def coerce_path(value: Path, **kwargs) -> Path:
    """Path coercion is complex and potentially unsafe. This function does not modify the path."""
    return value

COERCER_MAP = {
    int: coerce_int,
    float: coerce_float,
    Decimal: coerce_decimal,
    str: coerce_string,
    bytes: coerce_bytes,
    list: coerce_collection,
    set: coerce_collection,
    frozenset: coerce_collection,
    dict: coerce_mapping,
    date: coerce_date,
    UUID: coerce_uuid,
    Path: coerce_path,
}

def coerce_value(value: Any, annotation: Any, **constraints: Any) -> Any:
    """
    Dynamically selects and applies the correct coercer for a given type annotation.
    If no coercer is found, it returns the original value.
    """
    origin_type = get_origin(annotation) or annotation
    
    # Special case for Collection since it's not a concrete type
    if origin_type is Collection:
        origin_type = type(value)

    coercer = COERCER_MAP.get(origin_type)

    if coercer:
        sig = inspect.signature(coercer)
        valid_keys = {p.name for p in sig.parameters.values()}
        relevant_constraints = {k: v for k, v in constraints.items() if k in valid_keys}
        return coercer(value, **relevant_constraints)
    
    return value
