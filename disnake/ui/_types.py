# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Sequence, TypeVar, Union

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from . import (
        ActionRow,
        Button,
        Container,
        File,
        MediaGallery,
        Section,
        Separator,
        TextDisplay,
        TextInput,
    )
    from .item import WrappedComponent
    from .select import ChannelSelect, MentionableSelect, RoleSelect, StringSelect, UserSelect
    from .view import View

# TODO: consider if there are any useful types to make public (e.g. disnake-compass used MessageUIComponent)

V_co = TypeVar("V_co", bound="Optional[View]", covariant=True)

AnySelect = Union[
    "ChannelSelect[V_co]",
    "MentionableSelect[V_co]",
    "RoleSelect[V_co]",
    "StringSelect[V_co]",
    "UserSelect[V_co]",
]

# valid `ActionRow.components` item types in a message/modal
ActionRowMessageComponent = Union["Button[Any]", "AnySelect[Any]"]
ActionRowModalComponent: TypeAlias = "TextInput"

# valid message component types (v1/v2)
MessageTopLevelComponentV1: TypeAlias = "ActionRow[ActionRowMessageComponent]"
MessageTopLevelComponentV2 = Union[
    "Section",
    "TextDisplay",
    "MediaGallery",
    "File",
    "Separator",
    "Container",
]

ActionRowChildT = TypeVar("ActionRowChildT", bound="WrappedComponent")
# valid input types where action rows are expected
# (provides some shortcuts, such as converting lists to action rows)
ActionRowInput = Union[
    ActionRowChildT,  # single child component
    "ActionRow[ActionRowChildT]",  # single action row
    Sequence[  # multiple items, rows, or lists of items
        Union[ActionRowChildT, "ActionRow[ActionRowChildT]", Sequence[ActionRowChildT]]
    ],
]

# shortcuts for valid actionrow-ish input types
MessageComponentInputV1 = ActionRowInput[ActionRowMessageComponent]
MessageComponentInputV2 = Union[
    MessageTopLevelComponentV2,
    Sequence[MessageTopLevelComponentV2],
]
MessageComponentInput = Union[MessageComponentInputV1, MessageComponentInputV2]
ModalComponentInput = ActionRowInput[ActionRowModalComponent]
