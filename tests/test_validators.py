
import pytest
from decimal import Decimal
from datetime import date
from uuid import UUID, uuid4
from pathlib import Path
from typing import List, Set, FrozenSet, Dict

from pymocker.builder.validators import (
    is_valid_int,
    is_valid_float,
    is_valid_decimal,
    is_valid_string,
    is_valid_bytes,
    is_valid_collection,
    is_valid_mapping,
    is_valid_date,
    is_valid_uuid,
    is_valid_path,
    is_valid
)

# --- Integer Validators ---
def test_is_valid_int():
    assert is_valid_int(10, ge=5, lt=15, multiple_of=2)
    assert not is_valid_int(10, ge=12)
    assert not is_valid_int(10, lt=10)
    assert not is_valid_int(10, multiple_of=3)

# --- Float Validators ---
def test_is_valid_float():
    assert is_valid_float(10.5, gt=10.0, le=11.0)
    assert not is_valid_float(10.5, multiple_of=2.0)

# --- Decimal Validators ---
def test_is_valid_decimal():
    assert is_valid_decimal(Decimal("10.55"), max_digits=4, decimal_places=2)
    assert not is_valid_decimal(Decimal("10.555"), decimal_places=2)
    assert not is_valid_decimal(Decimal("12345"), max_digits=4)

# --- String Validators ---
def test_is_valid_string():
    assert is_valid_string("hello", min_length=3, max_length=5)
    assert is_valid_string("HELLO", upper_case=True)
    assert is_valid_string("hello", lower_case=True)
    assert is_valid_string("123-abc", pattern=r"^\d{3}-\w{3}$")
    assert not is_valid_string("hi", min_length=3)
    assert not is_valid_string("Hello", lower_case=True)

# --- Bytes Validators ---
def test_is_valid_bytes():
    assert is_valid_bytes(b"hello", min_length=5)
    assert not is_valid_bytes(b"HELLO", lower_case=True)

# --- Collection Validators ---
def test_is_valid_collection():
    assert is_valid_collection([1, 2, 3], min_items=3, max_items=5)
    assert is_valid_collection({1, 2, 3}, unique_items=True)
    assert not is_valid_collection([1, 1, 2], unique_items=True)
    assert not is_valid_collection([1], min_items=2)

# --- Mapping Validators ---
def test_is_valid_mapping():
    assert is_valid_mapping({'a': 1, 'b': 2}, min_items=2)
    assert not is_valid_mapping({'a': 1}, min_items=2)

# --- Date Validators ---
def test_is_valid_date():
    today = date.today()
    assert is_valid_date(today, ge=today)
    assert not is_valid_date(today, gt=today)

# --- UUID Validators ---
def test_is_valid_uuid():
    u = uuid4()
    assert is_valid_uuid(u, version=4)
    assert not is_valid_uuid(u, version=1)

# --- Path Validators ---
def test_is_valid_path(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = tmp_path / "test.file"
    p.touch()

    assert is_valid_path(d, constraint="dir")
    assert is_valid_path(p, constraint="file")
    assert is_valid_path(tmp_path / "new_file", constraint="new")
    assert not is_valid_path(p, constraint="dir")

# --- Dynamic Validator ---
def test_is_valid_dynamic():
    assert is_valid(10, int, ge=5)
    assert not is_valid("hi", str, min_length=3)
    assert is_valid([1, 2], List[int], max_items=2)
    # Test unhandled type
    assert is_valid(True, bool) is True
