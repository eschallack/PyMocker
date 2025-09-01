from __future__ import annotations
import copy
from typing import Any, Hashable, Mapping, Sequence

from polyfactory.factories.base import BaseFactory, BuildContext
from polyfactory.field_meta import FieldMeta
from polyfactory.fields import Fixture, Use
from polyfactory.utils.predicates import is_safe_subclass
from pymocker.builder.extensible import generate_by_rejection_sampling
import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Hashable,
    Mapping,
    Sequence
)
from polyfactory.exceptions import  MissingBuildKwargException
from polyfactory.field_meta import Null
from polyfactory.fields import Fixture, Ignore, PostGenerated, Require, Use
from polyfactory.utils.predicates import (
    is_safe_subclass,
)
if TYPE_CHECKING:
    from polyfactory.field_meta import FieldMeta
class PolyfactoryLogicMixin:
    """A mixin to hook into polyfactory's logic"""
    __max_retries__ = 300
    __coerce_on_fail__ = True
    __fuzzy_find_method__ = True
    
    @classmethod
    def _handle_factory_field(
        cls,
        field_value: Any,
        build_context: BuildContext,
        field_build_parameters: Any | None = None,
        field_meta: FieldMeta = None,
    ) -> Any:
        """
        Handle a value defined on the factory class itself.
        This method is an override of the one in BaseFactory to allow for custom logic.
        """
        if is_safe_subclass(field_value, BaseFactory):
            if isinstance(field_build_parameters, Mapping):
                return field_value.build(_build_context=build_context, **field_build_parameters)

            if isinstance(field_build_parameters, Sequence):
                return [
                    field_value.build(_build_context=build_context, **parameter)
                    for parameter in field_build_parameters
                ]

            return field_value.build(_build_context=build_context)

        if isinstance(field_value, Use):
            return field_value.to_value()

        if isinstance(field_value, Fixture):
            return field_value.to_value()

        if callable(field_value):
            if field_meta and getattr(field_meta, 'constraints') is not None:
                if field_meta.constraints:
                    return generate_by_rejection_sampling(
                        field_value,
                        field_meta.annotation,
                        field_meta.constraints,
                        max_retries=cls.__max_retries__,
                        coerce_on_fail=cls.__coerce_on_fail__
                        )
            return field_value()

        return field_value if isinstance(field_value, Hashable) else copy.deepcopy(field_value)
    @classmethod
    def process_kwargs(cls, **kwargs: Any) -> dict[str, Any]:
        """Process the given kwargs and generate values for the factory's model.

        :param kwargs: Any build kwargs.

        :returns: A dictionary of build results.

        """
        result, generate_post, _build_context = cls._get_initial_variables(kwargs)

        for field_meta in cls.get_model_fields():
            field_build_parameters = cls.extract_field_build_parameters(field_meta=field_meta, build_args=kwargs)
            
            if cls.should_set_field_value(field_meta, **kwargs) and not cls.should_use_default_value(field_meta):
                if hasattr(cls, field_meta.name) and not hasattr(BaseFactory, field_meta.name):
                    field_value = getattr(cls, field_meta.name)
                    if isinstance(field_value, Ignore):
                        continue

                    if isinstance(field_value, Require) and field_meta.name not in kwargs:
                        msg = f"Require kwarg {field_meta.name} is missing"
                        raise MissingBuildKwargException(msg)

                    if isinstance(field_value, PostGenerated):
                        generate_post[field_meta.name] = field_value
                        continue

                    result[field_meta.name] = cls._handle_factory_field(
                        field_value=field_value,
                        field_build_parameters=field_build_parameters,
                        build_context=_build_context,
                        field_meta=field_meta
                    )
                    continue
                
                field_result = cls.get_field_value(
                    field_meta,
                    field_build_parameters=field_build_parameters,
                    build_context=_build_context,
                )
                if field_result is Null:
                    continue

                result[field_meta.name] = field_result

        for field_name, post_generator in generate_post.items():
            result[field_name] = post_generator.to_value(field_name, result)

        return result
