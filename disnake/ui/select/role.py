# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
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
    """Represents a UI role select menu.

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
    default_values: Optional[Sequence[Union[:class:`.Role`, :class:`.SelectDefaultValue`, :class:`.Object`]]]
        The list of values (roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).

    Attributes
    ----------
    values: List[:class:`.Role`]
        A list of roles that have been selected by the user.
    """

    _default_value_type_map: ClassVar[
        Mapping[SelectDefaultValueType, Tuple[Type[Snowflake], ...]]
    ] = {
        SelectDefaultValueType.role: (Role, Object),
    }

    @overload
    def __init__(
        self: RoleSelect[None],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Optional[Sequence[SelectDefaultValueInputType[Role]]] = None,
        row: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self: RoleSelect[V_co],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Optional[Sequence[SelectDefaultValueInputType[Role]]] = None,
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
        default_values: Optional[Sequence[SelectDefaultValueInputType[Role]]] = None,
        row: Optional[int] = None,
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
            row=None,
        )


S_co = TypeVar("S_co", bound="RoleSelect", covariant=True)


@overload
def role_select(
    *,
    placeholder: Optional[str] = None,
    custom_id: str = ...,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    default_values: Optional[Sequence[SelectDefaultValueInputType[Role]]] = None,
    row: Optional[int] = None,
) -> Callable[[ItemCallbackType[V_co, RoleSelect[V_co]]], DecoratedItem[RoleSelect[V_co]]]:
    ...


@overload
def role_select(
    cls: Callable[P, S_co], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]:
    ...


def role_select(
    cls: Callable[..., S_co] = RoleSelect[Any], **kwargs: Any
) -> Callable[[ItemCallbackType[V_co, S_co]], DecoratedItem[S_co]]:
    """A decorator that attaches a role select menu to a component.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.RoleSelect` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`RoleSelect.values`.

    .. versionadded:: 2.7

    Parameters
    ----------
    cls: Callable[..., :class:`RoleSelect`]
        A callable (may be a :class:`RoleSelect` subclass) to create a new instance of this component.
        If provided, the other parameters described below do not apply.
        Instead, this decorator will accept the same keywords as the passed callable/class does.
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
    default_values: Optional[Sequence[Union[:class:`.Role`, :class:`.SelectDefaultValue`, :class:`.Object`]]]
        The list of values (roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    """
    return _create_decorator(cls, **kwargs)
