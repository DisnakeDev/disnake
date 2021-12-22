"""
The MIT License (MIT)

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

from typing import List, Optional, TYPE_CHECKING, Union

from .item import Item

from ..components import (
    Component,
    ActionRow as ActionRowComponent,
    Button as ButtonComponent,
    SelectOption,
    SelectMenu,
)
from ..enums import ButtonStyle, ComponentType
from ..utils import MISSING

__all__ = ("ActionRow",)

if TYPE_CHECKING:
    from ..emoji import Emoji
    from ..partial_emoji import PartialEmoji
    from ..types.components import ActionRow as ActionRowPayload


class ActionRow:
    """Represents a UI action row.

    .. versionadded:: 2.4

    Parameters
    ------------
    *items: :class:`Item`
        The items of this action row.
    """

    def __init__(self, *items: Item):
        self._total_width = 0
        components = []
        # Validate the components
        for item in items:
            if not isinstance(item, Item):
                raise ValueError("ActionRow must contain only Item instances")

            self._total_width += item.width

            if self._total_width > 5:
                raise ValueError(
                    "Too many items in 1 row. There should be not more than 5 buttons or 1 menu."
                )

            components.append(item._underlying)  # type: ignore

        self._underlying = ActionRowComponent._raw_construct(
            type=ComponentType.action_row,
            children=components,
        )

    @property
    def children(self) -> List[Component]:
        """List[:class:`Component`]: The components of this row."""
        return self._underlying.children

    @children.setter
    def children(self, value: List[Component]):
        self._underlying.children = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def append_item(self, item: Item) -> None:
        """Appends an item to the action row.

        Parameters
        -----------
        item: :class:`disnake.ui.Item`
            The item to append to the action row.

        Raises
        -------
        ValueError
            The width of the action row exceeds 5.
        """
        if self._total_width + item.width > 5:
            raise ValueError("Too many items in this row, can not appen a new one.")

        self._total_width += item.width
        self._underlying.children.append(item._underlying)  # type: ignore

    def add_button(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
    ):
        """Adds a button to the action row.

        To append a pre-existing :class:`disnake.ui.Button` use the
        :meth:`append_item` method instead.

        Parameters
        -----------
        style: :class:`disnake.ButtonStyle`
            The style of the button.
        custom_id: Optional[:class:`str`]
            The ID of the button that gets received during an interaction.
            If this button is for a URL, it does not have a custom ID.
        url: Optional[:class:`str`]
            The URL this button sends you to.
        disabled: :class:`bool`
            Whether the button is disabled or not.
        label: Optional[:class:`str`]
            The label of the button, if any.
        emoji: Optional[Union[:class:`.PartialEmoji`, :class:`.Emoji`, :class:`str`]]
            The emoji of the button, if available.

        Raises
        -------
        ValueError
            The width of the action row exceeds 5.
        """
        if self._total_width >= 5:
            raise ValueError("Too many items in this row, can not add a button.")

        self._total_width += 1
        self._underlying.children.append(
            ButtonComponent._raw_construct(
                type=ComponentType.button,
                custom_id=custom_id,
                url=url,
                disabled=disabled,
                label=label,
                style=style,
                emoji=emoji,
            )
        )

    def add_select(
        self,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        options: List[SelectOption] = MISSING,
        disabled: bool = False,
    ):
        """Adds a select menu to the action row.

        To append a pre-existing :class:`disnake.ui.Select` use the
        :meth:`append_item` method instead.

        Parameters
        -----------
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
        options: List[:class:`disnake.SelectOption`]
            A list of options that can be selected in this menu.
        disabled: :class:`bool`
            Whether the select is disabled or not.

        Raises
        -------
        ValueError
            The width of the action row exceeds 5.
        """
        if self._total_width >= 5:
            raise ValueError("Too many items in this row, can not add a select menu.")

        self._total_width += 5
        self._underlying.children.append(
            SelectMenu._raw_construct(
                custom_id=custom_id,
                type=ComponentType.select,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                options=options,
                disabled=disabled,
            )
        )

    def to_component_dict(self) -> ActionRowPayload:
        return self._underlying.to_dict()


def components_to_dict(
    components: Union[ActionRow, Item, List[Union[ActionRow, Item, List[Item]]]]
) -> List[ActionRowPayload]:
    if isinstance(components, ActionRow):
        return [components.to_component_dict()]

    if isinstance(components, Item):
        return [ActionRow(components).to_component_dict()]

    if not isinstance(components, list):
        raise ValueError("components must be an Item, a list of ActionRows or a list of Items")

    action_rows = []

    for component in components:
        if isinstance(component, ActionRow):
            action_rows.append(component.to_component_dict())

        elif isinstance(component, Item):
            action_rows.append(ActionRow(component).to_component_dict())

        elif isinstance(component, list):
            action_rows.append(ActionRow(*component).to_component_dict())

        else:
            raise ValueError("components must be an Item, a list of ActionRows or a list of Items")

    return action_rows
