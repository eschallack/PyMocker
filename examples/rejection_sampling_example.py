from faker import Faker

from pymocker.builder.extensible import GenerationError, generate_by_rejection_sampling
from pymocker.builder.validators import is_valid

def run_successful_generation_example():
    """Shows a standard successful generation using rejection sampling."""
    print("--- Running Example 1: Successful Generation ---")
    faker = Faker()
    annotation = int
    constraints = {"gt": 1000, "le": 1100, "multiple_of": 7}
    generator = lambda: faker.pyint(min_value=1000, max_value=1100)

    print(f"Attempting to generate a(n) '{annotation.__name__}' with constraints: {constraints}")
    try:
        valid_number = generate_by_rejection_sampling(
            generator=generator,
            annotation=annotation,
            constraints=constraints,
            max_retries=500,
        )
        print(f"✅ Success! Generated valid number: {valid_number}")
        assert is_valid(valid_number, annotation=annotation, **constraints)
    except GenerationError as e:
        print(f"❌ Failed to generate a valid number: {e}")


def run_coercion_fallback_example():
    """Shows the coercion fallback in action when generation is difficult."""
    print("--- Running Example 2: Coercion on Failure ---")
    faker = Faker()
    annotation = int
    # These constraints are very specific and unlikely to be met by random generation.
    constraints = {"ge": 999, "le": 1001, "multiple_of": 100}
    generator = faker.pyint

    print(f"Attempting to generate a(n) '{annotation.__name__}' with difficult constraints: {constraints}")
    print("This will likely fail sampling and trigger coercion.")
    
    # This time, we enable the coercion fallback
    coerced_number = generate_by_rejection_sampling(
        generator=generator,
        annotation=annotation,
        constraints=constraints,
        max_retries=100, # Lower retries to ensure fallback is triggered
        coerce_on_fail=True,
    )

    print(f"✅ Success! Coerced value: {coerced_number}")
    # We can check that the coerced number is now valid.
    assert is_valid(coerced_number, annotation=annotation, **constraints)
    print("Verified that the coerced value is valid.")

if __name__ == "__main__":
    run_successful_generation_example()
    run_coercion_fallback_example()
