"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    overload,
)

__all__ = ("Item", "WrappedComponent")

I = TypeVar("I", bound="Item")
V = TypeVar("V", bound="View", covariant=True)

if TYPE_CHECKING:
    from ..components import NestedComponent
    from ..enums import ComponentType
    from ..interactions import MessageInteraction
    from ..types.components import Component as ComponentPayload
    from .view import View

    ItemCallbackType = Callable[[Any, I, MessageInteraction], Coroutine[Any, Any, Any]]


class WrappedComponent(ABC):
    """Represents the base UI component that all UI components inherit from.

    The current UI components supported are:

    - :class:`disnake.ui.Button`
    - :class:`disnake.ui.Select`
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
        return f"<{self.__class__.__name__} {attrs}>"

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def to_component_dict(self) -> ComponentPayload:
        return self._underlying.to_dict()


class Item(WrappedComponent, Generic[V]):
    """Represents the base UI item that all UI items inherit from.

    This class adds more functionality on top of the :class:`WrappedComponent` base class.
    This functionality mostly relates to :class:`disnake.ui.View`.

    The current UI items supported are:

    - :class:`disnake.ui.Button`
    - :class:`disnake.ui.Select`

    .. versionadded:: 2.0
    """

    __repr_attributes__: Tuple[str, ...] = ("row",)

    def __init__(self):
        self._view: Optional[V] = None
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
    def from_component(cls: Type[I], component: NestedComponent) -> I:
        return cls()

    def is_dispatchable(self) -> bool:
        return False

    def is_persistent(self) -> bool:
        return self._provided_custom_id

    @property
    def row(self) -> Optional[int]:
        return self._row

    @row.setter
    def row(self, value: Optional[int]):
        if value is None:
            self._row = None
        elif 5 > value >= 0:
            self._row = value
        else:
            raise ValueError("row cannot be negative or greater than or equal to 5")

    @property
    def view(self) -> Optional[V]:
        """Optional[:class:`View`]: The underlying view for this item."""
        return self._view

    async def callback(self, interaction: MessageInteraction):
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
