# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict, Union

from typing_extensions import NotRequired, Required, TypeAlias

from .channel import ChannelType
from .emoji import PartialEmoji
from .snowflake import Snowflake

ComponentType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18]
ButtonStyle = Literal[1, 2, 3, 4, 5, 6]
TextInputStyle = Literal[1, 2]
SeparatorSpacing = Literal[1, 2]

SelectDefaultValueType = Literal["user", "role", "channel"]


# component type aliases/groupings

# all implemented components
Component = Union[
    "ActionRow",
    "ButtonComponent",
    "AnySelectMenu",
    "TextInput",
    "SectionComponent",
    "TextDisplayComponent",
    "ThumbnailComponent",
    "MediaGalleryComponent",
    "FileComponent",
    "SeparatorComponent",
    "ContainerComponent",
    "LabelComponent",
]

ActionRowChildComponent = Union[
    "ButtonComponent",
    "AnySelectMenu",
    "TextInput",  # deprecated
]

LabelChildComponent = Union[
    "TextInput",
    "AnySelectMenu",
]

# valid message component types (v1/v2)
MessageTopLevelComponentV1: TypeAlias = "ActionRow"
# currently, all v2 components except Thumbnail
MessageTopLevelComponentV2 = Union[
    "SectionComponent",
    "TextDisplayComponent",
    "MediaGalleryComponent",
    "FileComponent",
    "SeparatorComponent",
    "ContainerComponent",
]
MessageTopLevelComponent = Union[MessageTopLevelComponentV1, MessageTopLevelComponentV2]

# valid modal component types
ModalTopLevelComponent = Union[
    "ActionRow",  # deprecated
    "TextDisplayComponent",
    "LabelComponent",
]


# base types


class _BaseComponent(TypedDict):
    # type: ComponentType  # FIXME: current version of pyright only supports PEP 705 experimentally, this can be re-enabled in 1.1.353+
    id: int  # note: technically optional when sending, we just default to 0 for simplicity, which is equivalent (https://discord.com/developers/docs/components/reference#anatomy-of-a-component)


class ActionRow(_BaseComponent):
    type: Literal[1]
    components: List[ActionRowChildComponent]


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
    required: NotRequired[bool]


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
    components: List[ModalTopLevelComponent]


class TextInput(_BaseComponent):
    type: Literal[4]
    custom_id: str
    style: TextInputStyle
    label: NotRequired[Optional[str]]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]


class LabelComponent(_BaseComponent):
    type: Literal[18]
    label: str
    description: NotRequired[str]
    component: LabelChildComponent


# components v2


class UnfurledMediaItem(TypedDict, total=False):
    url: Required[str]  # this is the only field required for sending
    proxy_url: str
    height: Optional[int]
    width: Optional[int]
    content_type: str
    attachment_id: Snowflake


# NOTE: these are type definitions for *sending*, while *receiving* likely has fewer optional fields


class SectionComponent(_BaseComponent):
    type: Literal[9]
    # note: this may be expanded to more component types in the future
    components: List[TextDisplayComponent]
    # note: same as above
    accessory: Union[ThumbnailComponent, ButtonComponent]


class TextDisplayComponent(_BaseComponent):
    type: Literal[10]
    content: str


# note, can't be used at top level, this is exclusively for use in `SectionComponent.accessory`
class ThumbnailComponent(_BaseComponent):
    type: Literal[11]
    media: UnfurledMediaItem
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
    name: NotRequired[str]  # only provided by api
    size: NotRequired[int]  # only provided by api


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
