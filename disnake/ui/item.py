# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Generic,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    overload,
)

__all__ = ("Item", "WrappedComponent")

ItemT = TypeVar("ItemT", bound="Item")
V_co = TypeVar("V_co", bound="Optional[View]", covariant=True)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Self

    from ..components import NestedComponent
    from ..enums import ComponentType
    from ..interactions import MessageInteraction
    from ..types.components import Component as ComponentPayload
    from .view import View

    ItemCallbackType = Callable[[Any, ItemT, MessageInteraction], Coroutine[Any, Any, Any]]

else:
    ParamSpec = TypeVar


class WrappedComponent(ABC):
    """Represents the base UI component that all UI components inherit from.

    The following classes implement this ABC:

    - :class:`disnake.ui.Button`
    - subtypes of :class:`disnake.ui.BaseSelect` (:class:`disnake.ui.ChannelSelect`, :class:`disnake.ui.MentionableSelect`, :class:`disnake.ui.RoleSelect`, :class:`disnake.ui.StringSelect`, :class:`disnake.ui.UserSelect`)
    - :class:`disnake.ui.TextInput`

    .. versionadded:: 2.4
    """

    __repr_attributes__: Tuple[str, ...]

    @property
    @abstractmethod
    def _underlying(self) -> NestedComponent:
        ...

    @property
    @abstractmethod
    def width(self) -> int:
        ...

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_attributes__)
        return f"<{type(self).__name__} {attrs}>"

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def to_component_dict(self) -> ComponentPayload:
        return self._underlying.to_dict()


class Item(WrappedComponent, Generic[V_co]):
    """Represents the base UI item that all UI items inherit from.

    This class adds more functionality on top of the :class:`WrappedComponent` base class.
    This functionality mostly relates to :class:`disnake.ui.View`.

    The current UI items supported are:

    - :class:`disnake.ui.Button`
    - subtypes of :class:`disnake.ui.BaseSelect` (:class:`disnake.ui.ChannelSelect`, :class:`disnake.ui.MentionableSelect`, :class:`disnake.ui.RoleSelect`, :class:`disnake.ui.StringSelect`, :class:`disnake.ui.UserSelect`)

    .. versionadded:: 2.0
    """

    __repr_attributes__: Tuple[str, ...] = ("row",)

    @overload
    def __init__(self: Item[None]) -> None:
        ...

    @overload
    def __init__(self: Item[V_co]) -> None:
        ...

    def __init__(self) -> None:
        self._view: V_co = None  # type: ignore
        self._row: Optional[int] = None
        self._rendered_row: Optional[int] = None
        # This works mostly well but there is a gotcha with
        # the interaction with from_component, since that technically provides
        # a custom_id most dispatchable items would get this set to True even though
        # it might not be provided by the library user. However, this edge case doesn't
        # actually affect the intended purpose of this check because from_component is
        # only called upon edit and we're mainly interested during initial creation time.
        self._provided_custom_id: bool = False

    def refresh_component(self, component: NestedComponent) -> None:
        return None

    def refresh_state(self, interaction: MessageInteraction) -> None:
        return None

    @classmethod
    def from_component(cls, component: NestedComponent) -> Self:
        return cls()

    def is_dispatchable(self) -> bool:
        return False

    def is_persistent(self) -> bool:
        return self._provided_custom_id

    @property
    def row(self) -> Optional[int]:
        return self._row

    @row.setter
    def row(self, value: Optional[int]) -> None:
        if value is None:
            self._row = None
        elif 5 > value >= 0:
            self._row = value
        else:
            raise ValueError("row cannot be negative or greater than or equal to 5")

    @property
    def view(self) -> V_co:
        """Optional[:class:`View`]: The underlying view for this item."""
        return self._view

    async def callback(self, interaction: MessageInteraction, /) -> None:
        """|coro|

        The callback associated with this UI item.

        This can be overriden by subclasses.

        Parameters
        ----------
        interaction: :class:`.MessageInteraction`
            The interaction that triggered this UI item.
        """
        pass


I_co = TypeVar("I_co", bound=Item, covariant=True)


# while the decorators don't actually return a descriptor that matches this protocol,
# this protocol ensures that type checkers don't complain about statements like `self.button.disabled = True`,
# which work as `View.__init__` replaces the handler with the item
class DecoratedItem(Protocol[I_co]):
    @overload
    def __get__(self, obj: None, objtype: Any) -> ItemCallbackType:
        ...

    @overload
    def __get__(self, obj: Any, objtype: Any) -> I_co:
        ...


T_co = TypeVar("T_co", covariant=True)
P = ParamSpec("P")


class Object(Protocol[T_co, P]):
    def __new__(cls) -> T_co:
        ...

    def __init__(*args: P.args, **kwargs: P.kwargs) -> None:
        ...
