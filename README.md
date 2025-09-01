# PyMocker
*this library works, but is in an experimental phase. Feedback is encouraged*
PyMocker is a powerful and flexible Python library designed to generate realistic, context-aware mock data automatically. Built on top of [polyfactory](https://github.com/litestar-org/polyfactory), PyMocker extends its capabilities with intelligent field matching.

# Example:

```python
class Person(BaseModel):
    FirstName:str= Field(max_length=8)
    EmailAddress:str= Field(max_length=20)
    CellPhoneNumber:str= Field(min_length=12,max_length=12)

# without mocker
class PersonFactory(ModelFactory[Person]):...
person = PersonFactory.build()
print(f"Polyfactory:")
pprint(person)

# with mocker
mocker=Mocker()
mocker.Config.confidence_threshold = .5
@mocker.mock()
class MockerPersonFactory(ModelFactory[Person]):...
mocker_person = MockerPersonFactory.build()
print("Polyfactory + Mocker:")
pprint(mocker_person)
```
```shell
Polyfactory:
Person(FirstName='48a40717', EmailAddress='1a5a1a37', CellPhoneNumber='6185d0d7c109')
Polyfactory + Mocker:
Person(FirstName='Ashley', EmailAddress='tbutler@example.net', CellPhoneNumber='429-860-3379')
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
### Intelligent Field Matching

PyMocker's internal ranking and similarity algorithms use a number of techniques to match fields to methods, including cosine similarity. You can adjust the confidence threshold for this behavior:

```python
...
mocker=Mocker()
Mocker.confidence_threshold = 0.75 #.5 by default. higher means the model must be more confident to match
@mocker.mock()
...
```
### Adding and customizing Providers
By default, PyMocker will use a Faker instance as its sole method provider. Configure your faker instance and add custom classes by adding it directly to Mocker's provider_instances.

```python
...
class SuperHeroProvider:
    @staticmethod
    def super_hero_name():
        return 'MockerMan'
class Hero(BaseModel):
    HeroName:str=Field(max_length=9)
    
custom_faker_mocker=Mocker()
custom_faker_mocker.Config.provider_instances = [SuperHeroProvider(), Faker(locale='en_us')]

@custom_faker_mocker.mock()
...

```
```shell
Hero(HeroName='MockerMan')
```

### Intelligent Field Matching

PyMocker uses a number of matching rules to match methods to fields, including cosine similarity.
Configure this behavior like so:
```python
#Control the Confidence threshold of similarity matching, .5 by default
mocker.confidence_threshold = 0.75
```
**Note**: Cosine Similarity is not perfect, and at times, may produce undesired results.
You can disable this behavior entirely by setting match_field_generation_on_cosine_similarity to False
```python
mocker.match_field_generation_on_cosine_similarity = False
# a confidence threshold of 0 also disables the behavior
mocker.confidence_threshold = 0
```
When disabled, PyMocker still uses word segmentation to discover matches for you. If no method is found,
PyMocker defaults to PolyFactory's behavior

Other configurable attributes:
*   `max_retries` (int): The number of times a method will attempt to generate a constraint-fulfilling value. Higher values can impact performance. Defaults to `300`.
*   `coerce_on_fail` (bool): If `True`, attempts to coerce the value to match constraints if Faker generation fails. Defaults to `True`. When set to `False`, PyMocker will default to a PolyFactory generated value

## Supported Model Types

PyMocker seamlessly integrates with all PolyFactory Factories, except for SQLAlchemy - there's currently an issue
with pk/fk relationships, so your milage may vary

## Contributing

I'm just one guy, so I'd love some help improving this library. This is very early stages, so any suggestions or changes are welcome.
