# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from ...components import AnySelectMenu, SelectDefaultValue
from ...enums import ComponentType, SelectDefaultValueType
from ...object import Object
from ...utils import MISSING, humanize_list
from ..item import DecoratedItem, Item

__all__ = ("BaseSelect",)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Self

    from ...abc import Snowflake
    from ...interactions import MessageInteraction
    from ..item import ItemCallbackType
    from ..view import View

else:
    ParamSpec = TypeVar


S_co = TypeVar("S_co", bound="BaseSelect", covariant=True)
V_co = TypeVar("V_co", bound="Optional[View]", covariant=True)
SelectMenuT = TypeVar("SelectMenuT", bound=AnySelectMenu)
SelectValueT = TypeVar("SelectValueT")
P = ParamSpec("P")

SelectDefaultValueMultiInputType = Union[SelectValueT, SelectDefaultValue]
# almost the same as above, but with `Object`; used for selects where the type isn't ambiguous (i.e. all except mentionable select)
SelectDefaultValueInputType = Union[SelectDefaultValueMultiInputType[SelectValueT], Object]


class BaseSelect(Generic[SelectMenuT, SelectValueT, V_co], Item[V_co], ABC):
    """Represents an abstract UI select menu.

    This is usually represented as a drop down menu.

    This isn't meant to be used directly, instead use one of the concrete select menu types:

    - :class:`disnake.ui.StringSelect`
    - :class:`disnake.ui.UserSelect`
    - :class:`disnake.ui.RoleSelect`
    - :class:`disnake.ui.MentionableSelect`
    - :class:`disnake.ui.ChannelSelect`

    .. versionadded:: 2.7
    """

    __repr_attributes__: Tuple[str, ...] = (
        "placeholder",
        "min_values",
        "max_values",
        "disabled",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from WrappedComponent
    _underlying: SelectMenuT = MISSING

    # Subclasses are expected to set this
    _default_value_type_map: ClassVar[Mapping[SelectDefaultValueType, Tuple[Type[Snowflake], ...]]]

    def __init__(
        self,
        underlying_type: Type[SelectMenuT],
        component_type: ComponentType,
        *,
        custom_id: str,
        placeholder: Optional[str],
        min_values: int,
        max_values: int,
        disabled: bool,
        default_values: Optional[Sequence[SelectDefaultValueInputType[SelectValueT]]],
        row: Optional[int],
    ) -> None:
        super().__init__()
        self._selected_values: List[SelectValueT] = []
        self._provided_custom_id = custom_id is not MISSING
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = underlying_type._raw_construct(
            custom_id=custom_id,
            type=component_type,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            default_values=self._transform_default_values(default_values) if default_values else [],
        )
        self.row = row

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the select menu that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("custom_id must be None or str")

        self._underlying.custom_id = value

    @property
    def placeholder(self) -> Optional[str]:
        """Optional[:class:`str`]: The placeholder text that is shown if nothing is selected, if any."""
        return self._underlying.placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("placeholder must be None or str")

        self._underlying.placeholder = value

    @property
    def min_values(self) -> int:
        """:class:`int`: The minimum number of items that must be chosen for this select menu."""
        return self._underlying.min_values

    @min_values.setter
    def min_values(self, value: int) -> None:
        self._underlying.min_values = int(value)

    @property
    def max_values(self) -> int:
        """:class:`int`: The maximum number of items that must be chosen for this select menu."""
        return self._underlying.max_values

    @max_values.setter
    def max_values(self, value: int) -> None:
        self._underlying.max_values = int(value)

    @property
    def disabled(self) -> bool:
        """:class:`bool`: Whether the select menu is disabled."""
        return self._underlying.disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._underlying.disabled = bool(value)

    @property
    def default_values(self) -> List[SelectDefaultValue]:
        """List[:class:`.SelectDefaultValue`]: The list of values that are selected by default.
        Only available for auto-populated select menus.
        """
        return self._underlying.default_values

    @default_values.setter
    def default_values(
        self, value: Optional[Sequence[SelectDefaultValueInputType[SelectValueT]]]
    ) -> None:
        self._underlying.default_values = self._transform_default_values(value) if value else []

    @property
    def values(self) -> List[SelectValueT]:
        return self._selected_values

    @property
    def width(self) -> int:
        return 5

    def refresh_component(self, component: SelectMenuT) -> None:
        self._underlying = component

    def refresh_state(self, interaction: MessageInteraction) -> None:
        self._selected_values = interaction.resolved_values  # type: ignore

    @classmethod
    @abstractmethod
    def from_component(cls, component: SelectMenuT) -> Self:
        raise NotImplementedError

    def is_dispatchable(self) -> bool:
        """Whether the select menu is dispatchable. This will always return ``True``.

        :return type: :class:`bool`
        """
        return True

    @classmethod
    def _transform_default_values(
        cls, values: Sequence[SelectDefaultValueInputType[SelectValueT]]
    ) -> List[SelectDefaultValue]:
        result: List[SelectDefaultValue] = []

        for value in values:
            # If we have a SelectDefaultValue, just use it as-is
            if isinstance(value, SelectDefaultValue):
                if value.type not in cls._default_value_type_map:
                    allowed_types = [str(t) for t in cls._default_value_type_map]
                    raise ValueError(
                        f"SelectDefaultValue.type should be {humanize_list(allowed_types, 'or')}, not {value.type}"
                    )
                result.append(value)
                continue

            # Otherwise, look through the list of allowed input types and
            # get the associated SelectDefaultValueType
            for (
                value_type,  # noqa: B007  # we use value_type outside of the loop
                types,
            ) in cls._default_value_type_map.items():
                if isinstance(value, types):
                    break
            else:
                allowed_types = [
                    t.__name__ for ts in cls._default_value_type_map.values() for t in ts
                ]
                allowed_types.append(SelectDefaultValue.__name__)
                raise TypeError(
                    f"Expected type of default value to be {humanize_list(allowed_types, 'or')}, not {type(value)!r}"
                )

            result.append(SelectDefaultValue(value.id, value_type))

        return result


def _create_decorator(
    # FIXME(3.0): rename `cls` parameter to more closely represent any callable argument type
    cls: Callable[P, S_co],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]:
    if args:
        # the `*args` def above is just to satisfy the typechecker
        raise RuntimeError("expected no *args")

    if not callable(cls):
        raise TypeError("cls argument must be callable")

    def decorator(func: ItemCallbackType[V_co, S_co]) -> DecoratedItem[S_co]:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("select function must be a coroutine function")

        func.__discord_ui_model_type__ = cls
        func.__discord_ui_model_kwargs__ = kwargs
        return func  # type: ignore

    return decorator
