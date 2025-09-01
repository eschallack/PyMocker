
import pytest
from decimal import Decimal
from datetime import date, timedelta
from uuid import UUID, uuid4, NAMESPACE_DNS
from pathlib import Path
from typing import List, Set, FrozenSet, Dict, Any, Collection

from pymocker.builder.coercers import (
    coerce_int,
    coerce_float,
    coerce_decimal,
    coerce_string,
    coerce_bytes,
    coerce_collection,
    coerce_mapping,
    coerce_date,
    coerce_uuid,
    coerce_path,
    coerce_value,
    _coerce_numeric
)

# Tests for _coerce_numeric
def test_coerce_numeric_no_constraints():
    assert _coerce_numeric(10, None, None, None, None) == 10

def test_coerce_numeric_ge():
    assert _coerce_numeric(5, ge=10) == 10

def test_coerce_numeric_gt():
    assert _coerce_numeric(10, gt=10) > 10

def test_coerce_numeric_le():
    assert _coerce_numeric(15, le=10) == 10

def test_coerce_numeric_lt():
    assert _coerce_numeric(10, lt=10) < 10

# Tests for coerce_int
def test_coerce_int_multiple_of():
    assert coerce_int(13, multiple_of=5) == 15
    assert coerce_int(12, multiple_of=5) == 10

def test_coerce_int_conflicting_constraints():
    with pytest.raises(ValueError):
        coerce_int(5, ge=10, le=8)

# Tests for coerce_float
def test_coerce_float_multiple_of():
    assert coerce_float(13.0, multiple_of=5.0) == 15.0
    assert abs(coerce_float(12.4, multiple_of=2.5) - 12.5) < 1e-9

# Tests for coerce_decimal
def test_coerce_decimal_places():
    assert coerce_decimal(Decimal("12.3456"), decimal_places=2) == Decimal("12.35")

def test_coerce_decimal_multiple_of():
    assert coerce_decimal(Decimal("13"), multiple_of=Decimal("5")) == Decimal("15")

# Tests for coerce_string
def test_coerce_string_min_max_length():
    assert len(coerce_string("abc", min_length=5)) == 5
    assert len(coerce_string("abcdef", max_length=4)) == 4

def test_coerce_string_case():
    assert coerce_string("AbC", lower_case=True) == "abc"
    assert coerce_string("AbC", upper_case=True) == "ABC"

# Tests for coerce_bytes
def test_coerce_bytes_min_max_length():
    assert len(coerce_bytes(b"abc", min_length=5)) == 5
    assert len(coerce_bytes(b"abcdef", max_length=4)) == 4

# Tests for coerce_collection
def test_coerce_collection_min_max_items():
    assert len(coerce_collection([1, 2], min_items=4)) == 4
    assert len(coerce_collection([1, 2, 3, 4], max_items=2)) == 2

def test_coerce_collection_unique_items():
    assert len(coerce_collection([1, 2, 2, 3], unique_items=True)) == 3

def test_coerce_collection_type_preservation():
    assert isinstance(coerce_collection({1, 2}, min_items=3), set)
    assert isinstance(coerce_collection(frozenset([1, 2]), max_items=1), frozenset)

# Tests for coerce_mapping
def test_coerce_mapping_min_max_items():
    assert len(coerce_mapping({'a': 1}, min_items=3)) == 3
    assert len(coerce_mapping({'a': 1, 'b': 2, 'c': 3}, max_items=1)) == 1

# Tests for coerce_date
def test_coerce_date_constraints():
    today = date.today()
    assert coerce_date(today - timedelta(days=5), ge=today) == today
    assert coerce_date(today + timedelta(days=5), le=today) == today

# Tests for coerce_uuid
def test_coerce_uuid_version():
    u = uuid4()
    assert coerce_uuid(u, version=1).version == 1
    assert coerce_uuid(u, version=4).version == 4

# Tests for coerce_path
def test_coerce_path_no_modification():
    p = Path("/tmp/file")
    assert coerce_path(p) == p

# Tests for coerce_value (dynamic dispatcher)
def test_coerce_value_dynamic_dispatch():
    assert isinstance(coerce_value(12, int, multiple_of=5), int)
    assert isinstance(coerce_value("abc", str, min_length=5), str)
    assert isinstance(coerce_value([1, 2, 2], List[int], unique_items=True), list)
    assert isinstance(coerce_value(12.5, float, ge=15.0), float)
    # Test no-op for unhandled type
    assert coerce_value(True, bool) is True
