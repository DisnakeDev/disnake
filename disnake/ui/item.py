# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
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

__all__ = (
    "UIComponent",
    "WrappedComponent",
    "Item",
)

I = TypeVar("I", bound="Item[Any]")  # noqa: E741
V_co = TypeVar("V_co", bound="Optional[View]", covariant=True)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..components import ActionRowChildComponent, Component
    from ..enums import ComponentType
    from ..interactions import MessageInteraction
    from ..types.components import ActionRowChildComponent as ActionRowChildComponentPayload
    from .view import View

    ItemCallbackType = Callable[[V_co, I, MessageInteraction], Coroutine[Any, Any, Any]]

ClientT = TypeVar("ClientT", bound="Client")
UIComponentT = TypeVar("UIComponentT", bound="UIComponent")


def ensure_ui_component(obj: UIComponentT, name: str = "component") -> UIComponentT:
    if not isinstance(obj, UIComponent):
        msg = f"{name} should be a valid UI component, got {type(obj).__name__}."
        raise TypeError(msg)
    return obj


class UIComponent(ABC):
    """Represents the base UI component that all UI components inherit from.

    The following classes implement this ABC:

    - :class:`disnake.ui.ActionRow`
    - :class:`disnake.ui.Button`
    - subtypes of :class:`disnake.ui.BaseSelect` (:class:`disnake.ui.ChannelSelect`, :class:`disnake.ui.MentionableSelect`, :class:`disnake.ui.RoleSelect`, :class:`disnake.ui.StringSelect`, :class:`disnake.ui.UserSelect`)
    - :class:`disnake.ui.TextInput`
    - :class:`disnake.ui.Section`
    - :class:`disnake.ui.TextDisplay`
    - :class:`disnake.ui.Thumbnail`
    - :class:`disnake.ui.MediaGallery`
    - :class:`disnake.ui.File`
    - :class:`disnake.ui.Separator`
    - :class:`disnake.ui.Container`
    - :class:`disnake.ui.Label`

    .. versionadded:: 2.11
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]]

    @property
    @abstractmethod
    def _underlying(self) -> Component: ...

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{key.lstrip('_')}={getattr(self, key)!r}" for key in self.__repr_attributes__
        )
        return f"<{type(self).__name__} {attrs}>"

    @property
    def is_v2(self) -> bool:
        return self._underlying.is_v2

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def id(self) -> int:
        """:class:`int`: The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
        """
        return self._underlying.id

    @id.setter
    def id(self, value: int) -> None:
        self._underlying.id = value

    def to_component_dict(self) -> Dict[str, Any]:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls, component: Component, /) -> Self:
        return cls()


# Essentially the same as the base `UIComponent`, with the addition of `width`.
class WrappedComponent(UIComponent):
    """Represents the base UI component that all :class:`ActionRow`\\-compatible
    UI components inherit from.

    This class adds more functionality on top of the :class:`UIComponent` base class,
    specifically for action rows.

    The following classes implement this ABC:

    - :class:`disnake.ui.Button`
    - subtypes of :class:`disnake.ui.BaseSelect` (:class:`disnake.ui.ChannelSelect`, :class:`disnake.ui.MentionableSelect`, :class:`disnake.ui.RoleSelect`, :class:`disnake.ui.StringSelect`, :class:`disnake.ui.UserSelect`)
    - :class:`disnake.ui.TextInput`

    .. versionadded:: 2.4
    """

    # the purpose of these two is just more precise typechecking compared to the base type
    if TYPE_CHECKING:

        @property
        @abstractmethod
        def _underlying(self) -> ActionRowChildComponent: ...

        def to_component_dict(self) -> ActionRowChildComponentPayload: ...

    @property
    @abstractmethod
    def width(self) -> int: ...


class Item(WrappedComponent, Generic[V_co]):
    """Represents the base UI item that all interactive UI items inherit from.

    This class adds more functionality on top of the :class:`WrappedComponent` base class.
    This functionality mostly relates to :class:`disnake.ui.View`.

    The current UI items supported are:

    - :class:`disnake.ui.Button`
    - subtypes of :class:`disnake.ui.BaseSelect` (:class:`disnake.ui.ChannelSelect`, :class:`disnake.ui.MentionableSelect`, :class:`disnake.ui.RoleSelect`, :class:`disnake.ui.StringSelect`, :class:`disnake.ui.UserSelect`)

    .. versionadded:: 2.0
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = ("row",)

    @overload
    def __init__(self: Item[None]) -> None: ...

    @overload
    def __init__(self: Item[V_co]) -> None: ...

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

    def refresh_component(self, component: ActionRowChildComponent) -> None:
        return None

    def refresh_state(self, interaction: MessageInteraction) -> None:
        return None

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
            msg = "row cannot be negative or greater than or equal to 5"
            raise ValueError(msg)

    @property
    def view(self) -> V_co:
        """Optional[:class:`View`]: The underlying view for this item."""
        return self._view

    async def callback(self, interaction: MessageInteraction[ClientT], /) -> None:
        """|coro|

        The callback associated with this UI item.

        This can be overridden by subclasses.

        Parameters
        ----------
        interaction: :class:`.MessageInteraction`
            The interaction that triggered this UI item.
        """
        pass


SelfViewT = TypeVar("SelfViewT", bound="Optional[View]")


# While the decorators don't actually return a descriptor that matches this protocol,
# this protocol ensures that type checkers don't complain about statements like `self.button.disabled = True`,
# which work as `View.__init__` replaces the handler with the item.
class DecoratedItem(Protocol[I]):
    @overload
    def __get__(self, obj: None, objtype: Type[SelfViewT]) -> ItemCallbackType[SelfViewT, I]: ...

    @overload
    def __get__(self, obj: Any, objtype: Any) -> I: ...
