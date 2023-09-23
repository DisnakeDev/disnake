# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Type, TypeVar, overload

from ...components import ChannelSelectMenu
from ...enums import ChannelType, ComponentType
from ...utils import MISSING
from .base import BaseSelect, P, V_co, _create_decorator

if TYPE_CHECKING:
    from typing_extensions import Self

    from ...interactions.base import InteractionChannel
    from ..item import DecoratedItem, ItemCallbackType, Object


__all__ = (
    "ChannelSelect",
    "channel_select",
)


class ChannelSelect(BaseSelect[ChannelSelectMenu, "InteractionChannel", V_co]):
    """Represents a UI channel select menu.

    This is usually represented as a drop down menu.

    In order to get the selected items that the user has chosen, use :attr:`.values`.

    .. versionadded:: 2.7

    Parameters
    ----------
    custom_id: :class:`str`
        The ID of the select menu that gets received during an interaction.
        If not given then one is generated for you.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select is disabled.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    channel_types: Optional[List[:class:`.ChannelType`]]
        The list of channel types that can be selected in this select menu.
        Defaults to all types (i.e. ``None``).

    Attributes
    ----------
    values: List[Union[:class:`.abc.GuildChannel`, :class:`.Thread`, :class:`.PartialMessageable`]]
        A list of channels that have been selected by the user.
    """

    __repr_attributes__: Tuple[str, ...] = BaseSelect.__repr_attributes__ + ("channel_types",)

    @overload
    def __init__(
        self: ChannelSelect[None],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        channel_types: Optional[List[ChannelType]] = None,
        row: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self: ChannelSelect[V_co],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        channel_types: Optional[List[ChannelType]] = None,
        row: Optional[int] = None,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        channel_types: Optional[List[ChannelType]] = None,
        row: Optional[int] = None,
    ) -> None:
        super().__init__(
            ChannelSelectMenu,
            ComponentType.channel_select,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )
        self._underlying.channel_types = channel_types or None

    @classmethod
    def from_component(cls, component: ChannelSelectMenu) -> Self:
        return cls(
            custom_id=component.custom_id,
            placeholder=component.placeholder,
            min_values=component.min_values,
            max_values=component.max_values,
            disabled=component.disabled,
            channel_types=component.channel_types,
            row=None,
        )

    @property
    def channel_types(self) -> Optional[List[ChannelType]]:
        """Optional[List[:class:`disnake.ChannelType`]]: A list of channel types that can be selected in this select menu."""
        return self._underlying.channel_types

    @channel_types.setter
    def channel_types(self, value: Optional[List[ChannelType]]):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError("channel_types must be a list of ChannelType")
            if not all(isinstance(obj, ChannelType) for obj in value):
                raise TypeError("all list items must be ChannelType")

        self._underlying.channel_types = value


S_co = TypeVar("S_co", bound="ChannelSelect", covariant=True)


@overload
def channel_select(
    *,
    placeholder: Optional[str] = None,
    custom_id: str = ...,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    channel_types: Optional[List[ChannelType]] = None,
    row: Optional[int] = None,
) -> Callable[[ItemCallbackType[ChannelSelect[V_co]]], DecoratedItem[ChannelSelect[V_co]]]:
    ...


@overload
def channel_select(
    cls: Type[Object[S_co, P]], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[S_co]], DecoratedItem[S_co]]:
    ...


def channel_select(
    cls: Type[Object[S_co, P]] = ChannelSelect[Any], **kwargs: Any
) -> Callable[[ItemCallbackType[S_co]], DecoratedItem[S_co]]:
    """A decorator that attaches a channel select menu to a component.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.ChannelSelect` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`ChannelSelect.values`.

    .. versionadded:: 2.7

    Parameters
    ----------
    cls: Type[:class:`ChannelSelect`]
        The select subclass to create an instance of. If provided, the following parameters
        described below do not apply. Instead, this decorator will accept the same keywords
        as the passed cls does.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    custom_id: :class:`str`
        The ID of the select menu that gets received during an interaction.
        It is recommended not to set this parameter to prevent conflicts.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select is disabled. Defaults to ``False``.
    channel_types: Optional[List[:class:`.ChannelType`]]
        The list of channel types that can be selected in this select menu.
        Defaults to all types (i.e. ``None``).
    """
    return _create_decorator(cls, ChannelSelect, **kwargs)
