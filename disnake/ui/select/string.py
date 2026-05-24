# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    TypeAlias,
    TypeVar,
    overload,
)

from ...abc import Snowflake
from ...components import SelectOption, StringSelectMenu
from ...enums import ComponentType, SelectDefaultValueType
from ...utils import MISSING
from .base import BaseSelect, P, V_co, _create_decorator

if TYPE_CHECKING:
    from typing_extensions import Self

    from ...emoji import Emoji
    from ...partial_emoji import PartialEmoji
    from ..item import DecoratedItem, ItemCallbackType


__all__ = (
    "StringSelect",
    "Select",
    "string_select",
    "select",
)


SelectOptionInput: TypeAlias = list[SelectOption] | list[str] | dict[str, str]


def _parse_select_options(options: SelectOptionInput) -> list[SelectOption]:
    if isinstance(options, dict):
        return [SelectOption(label=key, value=val) for key, val in options.items()]

    return [opt if isinstance(opt, SelectOption) else SelectOption(label=opt) for opt in options]


class StringSelect(BaseSelect[StringSelectMenu, str, V_co]):
    r"""Represents a UI string select menu.

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
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select is disabled.
    options: :class:`list`\[:class:`disnake.SelectOption`] | :class:`list`\[:class:`str`] | :class:`dict`\[:class:`str`, :class:`str`]
        A list of options that can be selected in this menu. Use explicit :class:`.SelectOption`\s
        for fine-grained control over the options. Alternatively, a list of strings will be treated
        as a list of labels, and a dict will be treated as a mapping of labels to values.

        .. versionchanged:: 2.5
            Now also accepts a list of str or a dict of str to str, which are then appropriately parsed as
            :class:`.SelectOption` labels and values.

    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a message or modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message or modal.

        .. versionadded:: 2.11
    row: :class:`int` | :data:`None`
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to :data:`None`, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).

    Attributes
    ----------
    values: :class:`list`\[:class:`str`]
        A list of values that have been selected by the user.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (*BaseSelect.__repr_attributes__, "options")

    # In practice this should never be used by anything, might as well have it anyway though.
    _default_value_type_map: ClassVar[
        Mapping[SelectDefaultValueType, tuple[type[Snowflake], ...]]
    ] = {}

    @overload
    def __init__(
        self: StringSelect[None],
        *,
        custom_id: str = ...,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        options: SelectOptionInput = ...,
        required: bool = True,
        id: int = 0,
        row: int | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self: StringSelect[V_co],
        *,
        custom_id: str = ...,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        options: SelectOptionInput = ...,
        required: bool = True,
        id: int = 0,
        row: int | None = None,
    ) -> None: ...

    def __init__(
        self,
        *,
        custom_id: str = MISSING,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        options: SelectOptionInput = MISSING,
        required: bool = True,
        id: int = 0,
        row: int | None = None,
    ) -> None:
        super().__init__(
            StringSelectMenu,
            ComponentType.string_select,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            default_values=None,
            required=required,
            id=id,
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
            disabled=component.disabled,
            options=component.options,
            required=component.required,
            id=component.id,
            row=None,
        )

    @property
    def options(self) -> list[SelectOption]:
        r""":class:`list`\[:class:`disnake.SelectOption`]: A list of options that can be selected in this select menu."""
        return self._underlying.options

    @options.setter
    def options(self, value: list[SelectOption]) -> None:
        if not isinstance(value, list):
            msg = "options must be a list of SelectOption"
            raise TypeError(msg)
        if not all(isinstance(obj, SelectOption) for obj in value):
            msg = "all list items must subclass SelectOption"
            raise TypeError(msg)

        self._underlying.options = value

    def add_option(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
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
        description: :class:`str` | :data:`None`
            An additional description of the option, if any.
            Can only be up to 100 characters.
        emoji: :class:`str` | :class:`.Emoji` | :class:`.PartialEmoji` | :data:`None`
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
            msg = "maximum number of options already provided"
            raise ValueError(msg)

        self._underlying.options.append(option)


Select = StringSelect  # backwards compatibility


S_co = TypeVar("S_co", bound="StringSelect", covariant=True)


@overload
def string_select(
    *,
    placeholder: str | None = None,
    custom_id: str = ...,
    min_values: int = 1,
    max_values: int = 1,
    options: SelectOptionInput = ...,
    disabled: bool = False,
    id: int = 0,
    row: int | None = None,
) -> Callable[[ItemCallbackType[V_co, StringSelect[V_co]]], DecoratedItem[StringSelect[V_co]]]: ...


@overload
def string_select(
    cls: Callable[P, S_co], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]: ...


def string_select(
    cls: Callable[..., S_co] = StringSelect[Any], **kwargs: Any
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]:
    r"""A decorator that attaches a string select menu to a component.

    The function being decorated should have three parameters: ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.StringSelect` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`StringSelect.values`.

    .. versionchanged:: 2.7
        Renamed from ``select`` to ``string_select``.

    Parameters
    ----------
    cls: :class:`~collections.abc.Callable`\[..., :class:`StringSelect`]
        A callable (such as a :class:`StringSelect` subclass) returning an instance of a :class:`StringSelect`.
        If provided, the other parameters described below do not apply.
        Instead, this decorator will accept the same keyword arguments as the passed callable does.

        .. versionadded:: 2.6
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    custom_id: :class:`str`
        The ID of the select menu that gets received during an interaction.
        It is recommended not to set this parameter to prevent conflicts.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    options: :class:`list`\[:class:`disnake.SelectOption`] | :class:`list`\[:class:`str`] | :class:`dict`\[:class:`str`, :class:`str`]
        A list of options that can be selected in this menu. Use explicit :class:`.SelectOption`\s
        for fine-grained control over the options. Alternatively, a list of strings will be treated
        as a list of labels, and a dict will be treated as a mapping of labels to values.

        .. versionchanged:: 2.5
            Now also accepts a list of str or a dict of str to str, which are then appropriately parsed as
            :class:`.SelectOption` labels and values.

    disabled: :class:`bool`
        Whether the select is disabled. Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a view.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the view.

        .. versionadded:: 2.11
    row: :class:`int` | :data:`None`
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to :data:`None`, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).

    Raises
    ------
    TypeError
        The decorated function was not a coroutine function,
        or the ``cls`` parameter was not a callable or a subclass of :class:`StringSelect`.
    """
    return _create_decorator(cls, **kwargs)


select = string_select  # backwards compatibility
