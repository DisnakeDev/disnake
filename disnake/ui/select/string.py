# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from ...components import SelectOption, StringSelectMenu
from ...enums import ComponentType
from ...utils import MISSING
from .base import BaseSelect, P, V_co, _create_decorator

if TYPE_CHECKING:
    from typing_extensions import Self

    from ...emoji import Emoji
    from ...partial_emoji import PartialEmoji
    from ..item import DecoratedItem, ItemCallbackType, Object


__all__ = (
    "StringSelect",
    "Select",
    "string_select",
    "select",
)


SelectOptionInput = Union[List[SelectOption], List[str], Dict[str, str]]


def _parse_select_options(options: SelectOptionInput) -> List[SelectOption]:
    if isinstance(options, dict):
        return [SelectOption(label=key, value=val) for key, val in options.items()]

    return [opt if isinstance(opt, SelectOption) else SelectOption(label=opt) for opt in options]


class StringSelect(BaseSelect[StringSelectMenu, str, V_co]):
    """Represents a UI string select menu.

    This is usually represented as a drop down menu.

    In order to get the selected items that the user has chosen, use :attr:`.values`.

    .. versionadded:: 2.0

    .. versionchanged:: 2.7
        Renamed from ``Select`` to ``StringSelect``.

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
    options: Union[List[:class:`disnake.SelectOption`], List[:class:`str`], Dict[:class:`str`, :class:`str`]]
        A list of options that can be selected in this menu. Use explicit :class:`.SelectOption`\\s
        for fine-grained control over the options. Alternatively, a list of strings will be treated
        as a list of labels, and a dict will be treated as a mapping of labels to values.

        .. versionchanged:: 2.5
            Now also accepts a list of str or a dict of str to str, which are then appropriately parsed as
            :class:`.SelectOption` labels and values.

    disabled: :class:`bool`
        Whether the select is disabled.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).

    Attributes
    ----------
    values: List[:class:`str`]
        A list of values that have been selected by the user.
    """

    __repr_attributes__: Tuple[str, ...] = BaseSelect.__repr_attributes__ + ("options",)

    @overload
    def __init__(
        self: StringSelect[None],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        options: SelectOptionInput = ...,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self: StringSelect[V_co],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        options: SelectOptionInput = ...,
        disabled: bool = False,
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
        options: SelectOptionInput = MISSING,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        super().__init__(
            StringSelectMenu,
            ComponentType.string_select,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )
        self._underlying.options = [] if options is MISSING else _parse_select_options(options)

    @classmethod
    def from_component(cls, component: StringSelectMenu) -> Self:
        return cls(
            custom_id=component.custom_id,
            placeholder=component.placeholder,
            min_values=component.min_values,
            max_values=component.max_values,
            options=component.options,
            disabled=component.disabled,
            row=None,
        )

    @property
    def options(self) -> List[SelectOption]:
        """List[:class:`disnake.SelectOption`]: A list of options that can be selected in this select menu."""
        return self._underlying.options

    @options.setter
    def options(self, value: List[SelectOption]) -> None:
        if not isinstance(value, list):
            raise TypeError("options must be a list of SelectOption")
        if not all(isinstance(obj, SelectOption) for obj in value):
            raise TypeError("all list items must subclass SelectOption")

        self._underlying.options = value

    def add_option(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        default: bool = False,
    ) -> None:
        """Adds an option to the select menu.

        To append a pre-existing :class:`.SelectOption` use the
        :meth:`append_option` method instead.

        Parameters
        ----------
        label: :class:`str`
            The label of the option. This is displayed to users.
            Can only be up to 100 characters.
        value: :class:`str`
            The value of the option. This is not displayed to users.
            If not given, defaults to the label. Can only be up to 100 characters.
        description: Optional[:class:`str`]
            An additional description of the option, if any.
            Can only be up to 100 characters.
        emoji: Optional[Union[:class:`str`, :class:`.Emoji`, :class:`.PartialEmoji`]]
            The emoji of the option, if available. This can either be a string representing
            the custom or unicode emoji or an instance of :class:`.PartialEmoji` or :class:`.Emoji`.
        default: :class:`bool`
            Whether this option is selected by default.

        Raises
        ------
        ValueError
            The number of options exceeds 25.
        """
        option = SelectOption(
            label=label,
            value=value,
            description=description,
            emoji=emoji,
            default=default,
        )

        self.append_option(option)

    def append_option(self, option: SelectOption) -> None:
        """Appends an option to the select menu.

        Parameters
        ----------
        option: :class:`disnake.SelectOption`
            The option to append to the select menu.

        Raises
        ------
        ValueError
            The number of options exceeds 25.
        """
        if len(self._underlying.options) >= 25:
            raise ValueError("maximum number of options already provided")

        self._underlying.options.append(option)


Select = StringSelect  # backwards compatibility


S_co = TypeVar("S_co", bound="StringSelect", covariant=True)


@overload
def string_select(
    *,
    placeholder: Optional[str] = None,
    custom_id: str = ...,
    min_values: int = 1,
    max_values: int = 1,
    options: SelectOptionInput = ...,
    disabled: bool = False,
    row: Optional[int] = None,
) -> Callable[[ItemCallbackType[StringSelect[V_co]]], DecoratedItem[StringSelect[V_co]]]:
    ...


@overload
def string_select(
    cls: Type[Object[S_co, P]], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[S_co]], DecoratedItem[S_co]]:
    ...


def string_select(
    cls: Type[Object[S_co, P]] = StringSelect[Any],
    /,
    **kwargs: Any,
) -> Callable[[ItemCallbackType[S_co]], DecoratedItem[S_co]]:
    """A decorator that attaches a string select menu to a component.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.StringSelect` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`StringSelect.values`.

    .. versionchanged:: 2.7
        Renamed from ``select`` to ``string_select``.

    Parameters
    ----------
    cls: Type[:class:`StringSelect`]
        The select subclass to create an instance of. If provided, the following parameters
        described below do no apply. Instead, this decorator will accept the same keywords
        as the passed cls does.

        .. versionadded:: 2.6

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
    options: Union[List[:class:`disnake.SelectOption`], List[:class:`str`], Dict[:class:`str`, :class:`str`]]
        A list of options that can be selected in this menu. Use explicit :class:`.SelectOption`\\s
        for fine-grained control over the options. Alternatively, a list of strings will be treated
        as a list of labels, and a dict will be treated as a mapping of labels to values.

        .. versionchanged:: 2.5
            Now also accepts a list of str or a dict of str to str, which are then appropriately parsed as
            :class:`.SelectOption` labels and values.

    disabled: :class:`bool`
        Whether the select is disabled. Defaults to ``False``.
    """
    return _create_decorator(cls, StringSelect, **kwargs)


select = string_select  # backwards compatibility
