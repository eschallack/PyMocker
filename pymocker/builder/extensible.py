from __future__ import annotations

from typing import Any, Callable, TypeVar

from .coercers import coerce_value
from .validators import is_valid

T = TypeVar("T")

class GenerationError(Exception):
    """Raised when a valid value cannot be generated."""

def generate_by_rejection_sampling(
    generator: Callable[..., T],
    annotation: Any,
    constraints: dict[str, Any],
    max_retries: int = 100,
    coerce_on_fail: bool = False,
) -> T:
    """
    Generates a value by repeatedly calling a generator until it satisfies the given constraints.
    It's not great, but it works!
    Optionally fall back to forcefully coercing the last generated value if sampling fails.

    :param generator: A callable that produces values (e.g., a Faker method).
    :param annotation: The type annotation of the value to generate (e.g., int, str).
    :param constraints: A dictionary of constraints for the validator.
    :param max_retries: The maximum number of attempts before raising an exception or coercing.
    :param coerce_on_fail: If True, will coerce the last value on failure instead of raising an error.
    :raises GenerationError: If a valid value cannot be generated and coerce_on_fail is False.
    :return: A valid value that satisfies the constraints.
    """
    last_value = None
    for _ in range(max_retries):
        last_value = generator()
        if last_value is not None and is_valid(last_value, annotation, **constraints):
            return last_value

    if coerce_on_fail:
        if last_value is not None:
            return coerce_value(last_value, annotation, **constraints)

    msg = f"Could not generate a valid value for type '{annotation}' with constraints {constraints} after {max_retries} attempts."
    raise GenerationError(msg)
