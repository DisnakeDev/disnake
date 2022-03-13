# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, TypedDict, Union

from typing_extensions import NotRequired

from .emoji import PartialEmoji

ComponentType = Literal[1, 2, 3, 4, 5, 6, 7, 8]
ButtonStyle = Literal[1, 2, 3, 4, 5]
TextInputStyle = Literal[1, 2]


Component = Union["ActionRow", "ButtonComponent", "AnySelectMenu", "TextInput"]


class ActionRow(TypedDict):
    type: Literal[1]
    components: List[Component]


class ButtonComponent(TypedDict):
    type: Literal[2]
    style: ButtonStyle
    label: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    custom_id: NotRequired[str]
    url: NotRequired[str]
    disabled: NotRequired[bool]


class SelectOption(TypedDict):
    label: str
    value: str
    description: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    default: NotRequired[bool]


class _SelectMenu(TypedDict):
    custom_id: str
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    disabled: NotRequired[bool]


class BaseSelectMenu(_SelectMenu):
    type: Literal[3]


class SelectMenu(_SelectMenu):
    type: Literal[3]
    options: List[SelectOption]


AnySelectMenu = SelectMenu


class Modal(TypedDict):
    title: str
    custom_id: str
    components: List[ActionRow]


class TextInput(TypedDict):
    type: Literal[4]
    custom_id: str
    style: TextInputStyle
    label: str
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]
