# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    TypeVar,
    overload,
)

from ...abc import Snowflake
from ...components import RoleSelectMenu
from ...enums import ComponentType, SelectDefaultValueType
from ...object import Object
from ...role import Role
from ...utils import MISSING
from .base import BaseSelect, P, SelectDefaultValueInputType, V_co, _create_decorator

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..item import DecoratedItem, ItemCallbackType


__all__ = (
    "RoleSelect",
    "role_select",
)


class RoleSelect(BaseSelect[RoleSelectMenu, "Role", V_co]):
    r"""Represents a UI role select menu.

    This is usually represented as a drop down menu.

    In order to get the selected items that the user has chosen, use :attr:`.values`.

    .. versionadded:: 2.7

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
    default_values: :class:`~collections.abc.Sequence`\[:class:`.Role` | :class:`.SelectDefaultValue` | :class:`.Object`] | :data:`None`
        The list of values (roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message or modal.
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
    values: :class:`list`\[:class:`.Role`]
        A list of roles that have been selected by the user.
    """

    _default_value_type_map: ClassVar[
        Mapping[SelectDefaultValueType, tuple[type[Snowflake], ...]]
    ] = {
        SelectDefaultValueType.role: (Role, Object),
    }

    @overload
    def __init__(
        self: RoleSelect[None],
        *,
        custom_id: str = ...,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Sequence[SelectDefaultValueInputType[Role]] | None = None,
        required: bool = True,
        id: int = 0,
        row: int | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self: RoleSelect[V_co],
        *,
        custom_id: str = ...,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Sequence[SelectDefaultValueInputType[Role]] | None = None,
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
        default_values: Sequence[SelectDefaultValueInputType[Role]] | None = None,
        required: bool = True,
        id: int = 0,
        row: int | None = None,
    ) -> None:
        super().__init__(
            RoleSelectMenu,
            ComponentType.role_select,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            default_values=default_values,
            required=required,
            id=id,
            row=row,
        )

    @classmethod
    def from_component(cls, component: RoleSelectMenu) -> Self:
        return cls(
            custom_id=component.custom_id,
            placeholder=component.placeholder,
            min_values=component.min_values,
            max_values=component.max_values,
            disabled=component.disabled,
            default_values=component.default_values,
            required=component.required,
            id=component.id,
            row=None,
        )


S_co = TypeVar("S_co", bound="RoleSelect", covariant=True)


@overload
def role_select(
    *,
    placeholder: str | None = None,
    custom_id: str = ...,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    default_values: Sequence[SelectDefaultValueInputType[Role]] | None = None,
    id: int = 0,
    row: int | None = None,
) -> Callable[[ItemCallbackType[V_co, RoleSelect[V_co]]], DecoratedItem[RoleSelect[V_co]]]: ...


@overload
def role_select(
    cls: Callable[P, S_co], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]: ...


def role_select(
    cls: Callable[..., S_co] = RoleSelect[Any], **kwargs: Any
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]:
    r"""A decorator that attaches a role select menu to a component.

    The function being decorated should have three parameters: ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.RoleSelect` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`RoleSelect.values`.

    .. versionadded:: 2.7

    Parameters
    ----------
    cls: :class:`~collections.abc.Callable`\[..., :class:`RoleSelect`]
        A callable (such as a :class:`RoleSelect` subclass) returning an instance of a :class:`RoleSelect`.
        If provided, the other parameters described below do not apply.
        Instead, this decorator will accept the same keyword arguments as the passed callable does.
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
    disabled: :class:`bool`
        Whether the select is disabled. Defaults to ``False``.
    default_values: :class:`~collections.abc.Sequence`\[:class:`.Role` | :class:`.SelectDefaultValue` | :class:`.Object`] | :data:`None`
        The list of values (roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
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
        or the ``cls`` parameter was not a callable or a subclass of :class:`RoleSelect`.
    """
    return _create_decorator(cls, **kwargs)
