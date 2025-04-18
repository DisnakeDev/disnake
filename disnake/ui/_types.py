# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn, Optional, Sequence, TypeVar, Union

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
MessageTopLevelComponent = Union[MessageTopLevelComponentV1, MessageTopLevelComponentV2]

ActionRowChildT = TypeVar("ActionRowChildT", bound="WrappedComponent")
NonActionRowChildT = TypeVar("NonActionRowChildT", bound=MessageTopLevelComponentV2)

# generic utility type for any single ui component (within some generic bounds)
AnyUIComponentInput = Union[
    ActionRowChildT,  # action row child component
    "ActionRow[ActionRowChildT]",  # action row with given child types
    NonActionRowChildT,  # some subset of (v2) components that work outside of action rows
]

# The generic to end all generics.
# This represents valid input types where components are expected,
# providing some shortcuts/quality-of-life input shapes.
ComponentInput = Union[
    AnyUIComponentInput[ActionRowChildT, NonActionRowChildT],  # any single component
    Sequence[  # or, a sequence of either -
        Union[
            AnyUIComponentInput[ActionRowChildT, NonActionRowChildT],  # - any single component
            Sequence[ActionRowChildT],  # - a sequence of action row child types
        ]
    ],
]

MessageComponentInput = ComponentInput[ActionRowMessageComponent, MessageTopLevelComponentV2]
ModalComponentInput = ComponentInput[ActionRowModalComponent, NoReturn]
