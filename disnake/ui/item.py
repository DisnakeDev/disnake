"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

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

from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Type,
    TypeVar,
)

from ..interactions import MessageInteraction

__all__ = ("Item",)

if TYPE_CHECKING:
    from ..enums import ComponentType
    from .view import View
    from ..components import Component

I = TypeVar("I", bound="Item")
V = TypeVar("V", bound="View", covariant=True)
ItemCallbackType = Callable[[Any, I, MessageInteraction], Coroutine[Any, Any, Any]]


class Item(Generic[V]):
    """Represents the base UI item that all UI components inherit from.

    The current UI items supported are:

    - :class:`disnake.ui.Button`
    - :class:`disnake.ui.Select`

    .. versionadded:: 2.0
    """

    __original_kwargs__: Dict[str, Any]

    __item_decorated_callback__: ItemCallbackType

    __item_repr_attributes__: Tuple[str, ...] = ("row",)

    # similar to ext.commands.Command.__new__
    def __new__(cls: Type[I], *args: Any, **kwargs: Any) -> I:
        self = super().__new__(cls)
        self.__original_kwargs__ = kwargs.copy()
        return self

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

    def to_component_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    def _copy(self: I) -> I:
        # this copy method is only meant for decorator-created items
        item = self.__class__(**self.__original_kwargs__)
        item.__original_kwargs__ = self.__original_kwargs__  # discard copy created by __new__
        if hasattr(self, "__item_decorated_callback__"):
            item.__item_decorated_callback__ = self.__item_decorated_callback__
        return item

    def refresh_component(self, component: Component) -> None:
        return None

    def refresh_state(self, interaction: MessageInteraction) -> None:
        return None

    @classmethod
    def from_component(cls: Type[I], component: Component) -> I:
        return cls()

    @property
    def type(self) -> ComponentType:
        raise NotImplementedError

    def is_dispatchable(self) -> bool:
        return False

    def is_persistent(self) -> bool:
        return self._provided_custom_id

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__item_repr_attributes__)
        return f"<{self.__class__.__name__} {attrs}>"

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
    def width(self) -> int:
        return 1

    @property
    def view(self) -> Optional[V]:
        """Optional[:class:`View`]: The underlying view for this item."""
        return self._view

    async def callback(self, interaction: MessageInteraction):
        """|coro|

        The callback associated with this UI item.

        This can be overriden by subclasses.

        Parameters
        -----------
        interaction: :class:`.MessageInteraction`
            The interaction that triggered this UI item.
        """
        pass
