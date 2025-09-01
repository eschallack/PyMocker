# PyMocker
*this library works, but is in an experimental phase. Feedback is encouraged*

PyMocker is a powerful and flexible Python library designed to generate realistic, context-aware mock data automatically. Built on top of [polyfactory](https://github.com/litestar-org/polyfactory), PyMocker extends its capabilities with intelligent field matching.

## Example

```python
from pydantic import BaseModel, constr
from pymocker.mocker import Mocker
from datetime import date
class Person(BaseModel):
    firstname: constr(max_length=8)
    birthdate: date
    EmailAddress: constr(max_length=20)
    CellPhoneNumber: constr(max_length=15)
    HomeAddress:constr(max_length=100)
    WorkAddress:constr(max_length=100)

class PersonWithStaticFirstNameFactory(Mocker):
    __model__ = Person

person = PersonWithStaticFirstNameFactory.build()
print(person)

```
```shell
firstname='John' birthdate=datetime.date(1966, 10, 6) EmailAddress='kyu@example.net' CellPhoneNumber='+1-299-454-1936' HomeAddress='566 Fisher Row' WorkAddress='4833 Deborah Highway Apt. 024'
```

## Installation

PyPi package coming soon! In the meantime, install via git:
```bash
gh repo clone eschallack/PyMocker
```
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Overriding Field Generation

You can easily override the generation for any field by defining it directly within your Mocker class:

```python
from pydantic import BaseModel, constr
from pymocker.mocker import Mocker
from datetime import date
class Person(BaseModel):
    firstname: constr(max_length=8)
    birthdate: date
    EmailAddress: constr(max_length=20)
    CellPhoneNumber: constr(max_length=15)
    HomeAddress:constr(max_length=100)
    WorkAddress:constr(max_length=100)

class PersonWithStaticFirstNameFactory(Mocker):
    __model__ = Person
    firstname="jane"
person_jane = PersonWithStaticFirstNameFactory.build()
print(person_jane)

```
```shell
firstname='John' birthdate=datetime.date(1966, 10, 6) EmailAddress='kyu@example.net' CellPhoneNumber='+1-299-454-1936' HomeAddress='566 Fisher Row' WorkAddress='4833 Deborah Highway Apt. 024'
```

### Intelligent Field Matching

PyMocker goes beyond simple name matching. For example, `EmailAddress` and `CellPhoneNumber` in the `Person` model will intelligently map to appropriate Faker methods, even with non-standard casing, thanks to PyMocker's internal ranking and similarity algorithms. You can adjust the confidence threshold for this behavior:

```python
from pydantic import BaseModel, constr
from pymocker.mocker import Mocker

class Person(BaseModel):
    firstname: constr(max_length=8)
    EmailAddress: constr(max_length=20)
    CellPhoneNumber: constr(max_length=15)

# Adjust the confidence threshold for intelligent matching.
Mocker.__confidence_threshold__ = 0.4 #.75 by default

class CustomConfigPersonMocker(Mocker):
    __model__ = Person

person_custom_config = CustomConfigPersonMocker.build()
print(person_custom_config.model_dump_json(indent=2))
```

PyMocker provides several class-level attributes on the `Mocker` class that you can override to control its behavior:

*   `__match_field_generation_on_cosine_similarity__` (bool): If `True`, uses cosine similarity to match generation methods to fields based on `__confidence_threshold__`. This is the last matching technique attempted. Defaults to `True`.
*   `__confidence_threshold__` (float): The confidence threshold for cosine similarity matching between generation methods and field names. Setting to `0` disables this behavior entirely. Defaults to `0.75`.
*   `__max_retries__` (int): The number of times Faker will attempt to generate a constraint-fulfilling value. Higher values can impact performance. Defaults to `300`.
*   `__coerce_on_fail__` (bool): If `True`, attempts to coerce the value to match constraints if Faker generation fails. Defaults to `True`.

## Supported Model Types

PyMocker seamlessly integrates with:

*   **Pydantic** (`BaseModel`)
*   **Dataclasses**
*   **TypedDicts**
*   **SQLAlchemy** 🚧 Under Construction

## Contributing

I'm just one guy, so I'd love some help improving this library. This is very early stages, so any suggestions or changes are welcome.
