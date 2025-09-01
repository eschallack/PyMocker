
import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import FieldMeta

from pymocker.builder.mixins import PolyfactoryLogicMixin

# 1. Setup a mock model and factory
class MyModel(BaseModel):
    x: int
    y: str

class MyFactory(PolyfactoryLogicMixin, ModelFactory[MyModel]):
    __model__ = MyModel
    __max_retries__ = 300
    __coerce_on_fail__ = True

# 2. Tests for PolyfactoryLogicMixin

def test_handle_factory_field_callable_with_constraints():
    """
    Tests that a callable on the factory with constraints is handled
    by generate_by_rejection_sampling.
    """
    # Mock the rejection sampling function to see if it's called
    with patch("pymocker.builder.mixins.generate_by_rejection_sampling") as mock_generate:
        mock_generate.return_value = 123  # The value it should return

        factory = MyFactory
        factory.x = lambda: 100  # A simple callable

        # Define field metadata with constraints
        field_meta = FieldMeta(name="x", annotation=int, constraints={"ge": 100})

        # Call the method under test
        result = factory._handle_factory_field(
            field_value=factory.x,
            build_context=MagicMock(),
            field_meta=field_meta
        )

        # Assert that our mock was called correctly
        mock_generate.assert_called_once_with(
            factory.x,
            int,
            {"ge": 100},
            max_retries=factory.__max_retries__,
            coerce_on_fail=factory.__coerce_on_fail__
        )
        # Assert that the result is what our mock returned
        assert result == 123

def test_handle_factory_field_callable_no_constraints():
    """
    Tests that a callable on the factory without constraints is called directly.
    """
    with patch("pymocker.builder.mixins.generate_by_rejection_sampling") as mock_generate:
        factory = MyFactory
        # A callable that returns a fixed value
        factory.y = lambda: "hello"

        field_meta = FieldMeta(name="y", annotation=str)

        result = factory._handle_factory_field(
            field_value=factory.y,
            build_context=MagicMock(),
            field_meta=field_meta
        )

        # Ensure rejection sampling was NOT called
        mock_generate.assert_not_called()
        # The result should be from the direct call to the lambda
        assert result == "hello"

@pytest.fixture(autouse=True)
def reset_factory():
    # Reset factory attributes before each test
    if hasattr(MyFactory, 'x'):
        del MyFactory.x
    if hasattr(MyFactory, 'y'):
        del MyFactory.y

def test_process_kwargs_uses_factory_attributes():
    """
    Tests that process_kwargs correctly uses attributes defined on the factory itself.
    This is a more high-level integration test of the mixin.
    """
    # We patch the underlying method that gets the value to isolate the logic
    with patch.object(MyFactory, 'get_field_value') as mock_get_field_value:
        mock_get_field_value.return_value = "mocked_y"

        factory = MyFactory
        # Define a callable for a field on the factory
        factory.x = lambda: 99

        # Run the method that orchestrates the build
        result = factory.process_kwargs()

        # 'x' should be set from the factory's attribute (the lambda)
        assert "x" in result
        assert result["x"] == 99

        # 'y' was not defined on the factory, so get_field_value should have been called for it
        mock_get_field_value.assert_called_once()
        # Ensure the call was for the 'y' field
        called_with_field_name = mock_get_field_value.call_args[0][0].name
        assert called_with_field_name == 'y'
        assert result['y'] == 'mocked_y'

