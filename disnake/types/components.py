# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, TypedDict, Union

from typing_extensions import NotRequired

from .channel import ChannelType
from .emoji import PartialEmoji
from .snowflake import Snowflake

ComponentType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17]
ButtonStyle = Literal[1, 2, 3, 4, 5, 6]
TextInputStyle = Literal[1, 2]
SeparatorSpacing = Literal[1, 2]

SelectDefaultValueType = Literal["user", "role", "channel"]

Component = Union[
    "ActionRow",
    "ButtonComponent",
    "AnySelectMenu",
    "TextInput",
    "SectionComponent",
    "TextDisplayComponent",
    "ThumbnailComponent",  # TODO: reconsider the semantics of this `Component` union, not all of these types can appear in all places
    "MediaGalleryComponent",
    "SeparatorComponent",
    "FileComponent",
    "ContainerComponent",
]


# base types


class _BaseComponent(TypedDict):
    # type: ComponentType  # FIXME: current version of pyright complains about overriding types, latest might be fine
    # TODO: always present in responses?
    id: NotRequired[int]  # NOTE: not implemented (yet?)


class ActionRow(_BaseComponent):
    type: Literal[1]
    components: List[Component]


# button


class ButtonComponent(_BaseComponent):
    type: Literal[2]
    style: ButtonStyle
    label: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    custom_id: NotRequired[str]
    url: NotRequired[str]
    disabled: NotRequired[bool]
    sku_id: NotRequired[Snowflake]


# selects


class SelectOption(TypedDict):
    label: str
    value: str
    description: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    default: NotRequired[bool]


class SelectDefaultValue(TypedDict):
    id: Snowflake
    type: SelectDefaultValueType


class _SelectMenu(_BaseComponent):
    custom_id: str
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    disabled: NotRequired[bool]
    # This is technically not applicable to string selects, but for simplicity we'll just have it here
    default_values: NotRequired[List[SelectDefaultValue]]


class BaseSelectMenu(_SelectMenu):
    type: Literal[3, 5, 6, 7, 8]


class StringSelectMenu(_SelectMenu):
    type: Literal[3]
    options: List[SelectOption]


class UserSelectMenu(_SelectMenu):
    type: Literal[5]


class RoleSelectMenu(_SelectMenu):
    type: Literal[6]


class MentionableSelectMenu(_SelectMenu):
    type: Literal[7]


class ChannelSelectMenu(_SelectMenu):
    type: Literal[8]
    channel_types: NotRequired[List[ChannelType]]


AnySelectMenu = Union[
    StringSelectMenu,
    UserSelectMenu,
    RoleSelectMenu,
    MentionableSelectMenu,
    ChannelSelectMenu,
]


# modal


class Modal(TypedDict):
    title: str
    custom_id: str
    components: List[ActionRow]


class TextInput(_BaseComponent):
    type: Literal[4]
    custom_id: str
    style: TextInputStyle
    label: str
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]


# components v2
# NOTE: these are type definitions for *sending*, while *receiving* likely has fewer optional fields


# TODO: this expands to an `EmbedImage`-like structure in responses, with more than just the `url` field
class UnfurledMediaItem(TypedDict):
    url: str


# XXX: drop `Component` suffix? `ButtonComponent` also uses it, selects don't.
class SectionComponent(_BaseComponent):
    type: Literal[9]
    components: List[TextDisplayComponent]
    # this currently only supports ThumbnailComponent, others will be added in the future
    # (the API seemingly also allows buttons, but they don't render yet)
    accessory: Component


class TextDisplayComponent(_BaseComponent):
    type: Literal[10]
    content: str


# note, can't be used at top level, appears to be exclusively for `SectionComponent.accessory`?
class ThumbnailComponent(_BaseComponent):
    type: Literal[11]
    # TODO: this will be renamed to `media`
    image: UnfurledMediaItem
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryItem(TypedDict):
    media: UnfurledMediaItem
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryComponent(_BaseComponent):
    type: Literal[12]
    items: List[MediaGalleryItem]


class FileComponent(_BaseComponent):
    type: Literal[13]
    file: UnfurledMediaItem  # only supports `attachment://` urls
    spoiler: NotRequired[bool]


class SeparatorComponent(_BaseComponent):
    type: Literal[14]
    divider: NotRequired[bool]
    spacing: NotRequired[SeparatorSpacing]


class ContainerComponent(_BaseComponent):
    type: Literal[17]
    accent_color: NotRequired[int]
    spoiler: NotRequired[bool]
    components: List[
        Union[
            ActionRow,
            SectionComponent,
            TextDisplayComponent,
            MediaGalleryComponent,
            FileComponent,
            SeparatorComponent,
        ]
    ]
