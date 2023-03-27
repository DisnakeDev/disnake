# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, TypedDict, Union

from typing_extensions import NotRequired

from .channel import ChannelType
from .emoji import PartialEmoji

ComponentType = Literal[1, 2, 3, 4, 5, 6, 7, 8]
ButtonStyle = Literal[1, 2, 3, 4, 5]
TextInputStyle = Literal[1, 2]


ComponentPayload = Union["ActionRowPayload", "ButtonComponentPayload", "AnySelectMenu", "TextInputPayload"]


class ActionRowPayload(TypedDict):
    type: Literal[1]
    components: List[ComponentPayload]


class ButtonComponentPayload(TypedDict):
    type: Literal[2]
    style: ButtonStyle
    label: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    custom_id: NotRequired[str]
    url: NotRequired[str]
    disabled: NotRequired[bool]


class SelectOptionPayload(TypedDict):
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


class BaseSelectMenuPayload(_SelectMenu):
    type: Literal[3, 5, 6, 7, 8]


class StringSelectMenuPayload(_SelectMenu):
    type: Literal[3]
    options: List[SelectOptionPayload]


class UserSelectMenu(_SelectMenu):
    type: Literal[5]


class RoleSelectMenuPayload(_SelectMenu):
    type: Literal[6]


class MentionableSelectMenuPayload(_SelectMenu):
    type: Literal[7]


class ChannelSelectMenuPayload(_SelectMenu):
    type: Literal[8]
    channel_types: NotRequired[List[ChannelType]]


AnySelectMenu = Union[
    StringSelectMenuPayload,
    UserSelectMenu,
    RoleSelectMenuPayload,
    MentionableSelectMenuPayload,
    ChannelSelectMenuPayload,
]


class Modal(TypedDict):
    title: str
    custom_id: str
    components: List[ActionRowPayload]


class TextInputPayload(TypedDict):
    type: Literal[4]
    custom_id: str
    style: TextInputStyle
    label: str
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]
