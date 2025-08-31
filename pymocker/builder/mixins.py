import copy
from typing import Any, Hashable, Mapping, Sequence

from polyfactory.factories.base import BaseFactory, BuildContext
from polyfactory.field_meta import FieldMeta
from polyfactory.fields import Fixture, Use
from polyfactory.utils.predicates import is_safe_subclass
from pymocker.builder.extensible import generate_by_rejection_sampling

class PolyfactoryLogicMixin:
    """A mixin to hook into polyfactory's logic"""
    __max_retries__ = 300
    __coerce_on_fail__ = True
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
        print("we r in da system")
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
