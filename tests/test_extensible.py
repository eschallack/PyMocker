
import pytest
from pymocker.builder.extensible import generate_by_rejection_sampling, GenerationError

# A simple generator that returns incrementing integers
class Counter:
    def __init__(self):
        self.val = 0
    def __call__(self):
        self.val += 1
        return self.val

def test_rejection_sampling_success():
    """Tests that the function returns a valid value when the generator succeeds."""
    generator = lambda: 5
    # A constraint that is immediately satisfied
    value = generate_by_rejection_sampling(generator, int, {"ge": 5})
    assert value == 5

def test_rejection_sampling_retries_and_succeeds():
    """Tests that the function retries until a valid value is found."""
    generator = Counter()
    # The generator will be called 5 times (1, 2, 3, 4, 5)
    value = generate_by_rejection_sampling(generator, int, {"ge": 5})
    assert value == 5

def test_rejection_sampling_fails_and_raises_error():
    """Tests that a GenerationError is raised if no valid value is found."""
    generator = lambda: 1
    with pytest.raises(GenerationError):
        generate_by_rejection_sampling(generator, int, {"ge": 5}, max_retries=10)

def test_rejection_sampling_fails_and_coerces():
    """Tests that the last value is coerced when sampling fails and coerce_on_fail is True."""
    generator = lambda: 1
    # The last generated value (1) will be coerced to be >= 5
    value = generate_by_rejection_sampling(
        generator, int, {"ge": 5}, max_retries=10, coerce_on_fail=True
    )
    assert value == 5

def test_rejection_sampling_with_no_constraints():
    """Tests that the first value is returned when there are no constraints."""
    generator = lambda: 123
    value = generate_by_rejection_sampling(generator, int, {})
    assert value == 123

def test_rejection_sampling_coerce_on_fail_with_none():
    """Tests that GenerationError is raised if coercion is attempted on a None value."""
    # This can happen if the generator produces None, which is an edge case.
    generator = lambda: None
    with pytest.raises(GenerationError):
        generate_by_rejection_sampling(
            generator, int, {"ge": 5}, max_retries=10, coerce_on_fail=True
        )
