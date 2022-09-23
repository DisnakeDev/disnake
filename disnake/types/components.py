# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, TypedDict, Union

from .emoji import PartialEmoji

ComponentType = Literal[1, 2, 3, 4]
ButtonStyle = Literal[1, 2, 3, 4, 5]
TextInputStyle = Literal[1, 2]


Component = Union["ActionRow", "ButtonComponent", "SelectMenu", "TextInput"]


class ActionRow(TypedDict):
    type: Literal[1]
    components: List[Component]


class _ButtonComponentOptional(TypedDict, total=False):
    custom_id: str
    url: str
    disabled: bool
    emoji: PartialEmoji
    label: str


class ButtonComponent(_ButtonComponentOptional):
    type: Literal[2]
    style: ButtonStyle


class _SelectMenuOptional(TypedDict, total=False):
    placeholder: str
    min_values: int
    max_values: int
    disabled: bool


class _SelectOptionsOptional(TypedDict, total=False):
    description: str
    emoji: PartialEmoji


class SelectOption(_SelectOptionsOptional):
    label: str
    value: str
    default: bool


class SelectMenu(_SelectMenuOptional):
    type: Literal[3]
    custom_id: str
    options: List[SelectOption]


class Modal(TypedDict):
    title: str
    custom_id: str
    components: List[ActionRow]


class _TextInputOptional(TypedDict, total=False):
    value: str
    placeholder: str
    min_length: int
    max_length: int
    required: bool


class TextInput(_TextInputOptional):
    type: Literal[4]
    custom_id: str
    style: TextInputStyle
    label: str
