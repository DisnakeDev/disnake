# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional, Type, TypeVar, Union, overload

from ...components import UserSelectMenu
from ...enums import ComponentType
from ...utils import MISSING
from .base import BaseSelect, P, V_co, _create_decorator

if TYPE_CHECKING:
    from typing_extensions import Self

    from ...member import Member
    from ...user import User
    from ..item import DecoratedItem, ItemCallbackType, Object


__all__ = (
    "UserSelect",
    "user_select",
)


class UserSelect(BaseSelect[UserSelectMenu, "Union[User, Member]", V_co]):
    """Represents a UI user select menu.

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

    Attributes
    ----------
    values: List[:class:`~disnake.User`, :class:`.Member`]
        A list of users/members that have been selected by the user.
    """

    @overload
    def __init__(
        self: UserSelect[None],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self: UserSelect[V_co],
        *,
        custom_id: str = ...,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
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
        disabled: bool = False,
        row: Optional[int] = None,
    ) -> None:
        super().__init__(
            UserSelectMenu,
            ComponentType.user_select,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            row=row,
        )

    @classmethod
    def from_component(cls, component: UserSelectMenu) -> Self:
        return cls(
            custom_id=component.custom_id,
            placeholder=component.placeholder,
            min_values=component.min_values,
            max_values=component.max_values,
            disabled=component.disabled,
            row=None,
        )


S_co = TypeVar("S_co", bound="UserSelect", covariant=True)


@overload
def user_select(
    *,
    placeholder: Optional[str] = None,
    custom_id: str = ...,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    row: Optional[int] = None,
) -> Callable[[ItemCallbackType[UserSelect[V_co]]], DecoratedItem[UserSelect[V_co]]]:
    ...


@overload
def user_select(
    cls: Type[Object[S_co, P]], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[S_co]], DecoratedItem[S_co]]:
    ...


def user_select(
    cls: Type[Object[S_co, P]] = UserSelect[Any],
    /,
    **kwargs: Any,
) -> Callable[[ItemCallbackType[S_co]], DecoratedItem[S_co]]:
    """A decorator that attaches a user select menu to a component.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.UserSelect` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`UserSelect.values`.

    .. versionadded:: 2.7

    Parameters
    ----------
    cls: Type[:class:`UserSelect`]
        The select subclass to create an instance of. If provided, the following parameters
        described below do no apply. Instead, this decorator will accept the same keywords
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
    """
    return _create_decorator(cls, UserSelect, **kwargs)
