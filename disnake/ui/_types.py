# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TypeAlias, Union

from typing_extensions import ParamSpec, TypeVar

if TYPE_CHECKING:
    from typing import TypeAlias

    from . import (
        ActionRow,
        Button,
        Container,
        File,
        Label,
        MediaGallery,
        Section,
        Separator,
        TextDisplay,
        TextInput,
    )
    from .select import ChannelSelect, MentionableSelect, RoleSelect, StringSelect, UserSelect
    from .view import View

V_co = TypeVar("V_co", bound="View | None", covariant=True, default=None)
# strict View-bound TypeVar used in decorators
V_deco = TypeVar("V_deco", bound="View", covariant=True)
P = ParamSpec("P")

AnySelect: TypeAlias = Union[
    "ChannelSelect[V_co]",
    "MentionableSelect[V_co]",
    "RoleSelect[V_co]",
    "StringSelect[V_co]",
    "UserSelect[V_co]",
]

# valid `ActionRow.components` item types in a message/modal
ActionRowMessageComponent: TypeAlias = Union["Button[Any]", "AnySelect[Any]"]
ActionRowModalComponent: TypeAlias = "TextInput"  # deprecated

# valid message component types (v1/v2)
MessageTopLevelComponentV1: TypeAlias = "ActionRow[ActionRowMessageComponent]"
MessageTopLevelComponentV2: TypeAlias = Union[
    "Section",
    "TextDisplay",
    "MediaGallery",
    "File",
    "Separator",
    "Container",
]
MessageTopLevelComponent: TypeAlias = Union[MessageTopLevelComponentV1, MessageTopLevelComponentV2]  # noqa: UP007

# valid modal component types (separate type with ActionRow until fully deprecated)
ModalTopLevelComponent_: TypeAlias = Union[
    "TextDisplay",
    "Label",
]
ModalTopLevelComponent: TypeAlias = Union[
    ModalTopLevelComponent_,
    "ActionRow[ActionRowModalComponent]",  # deprecated
]

ActionRowChildT = TypeVar(
    "ActionRowChildT",
    ActionRowMessageComponent,
    ActionRowModalComponent,
    infer_variance=True,
)

NonActionRowChildT = TypeVar(
    "NonActionRowChildT",
    bound=MessageTopLevelComponentV2 | ModalTopLevelComponent_,
)

# generic utility type for any single ui component (within some generic bounds)
AnyUIComponentInput: TypeAlias = Union[
    ActionRowChildT,  # action row child component
    "ActionRow[ActionRowChildT]",  # action row with given child types
    NonActionRowChildT,  # some subset of (v2) components that work outside of action rows
]

# The generic to end all generics.
# This represents valid input types where components are expected,
# providing some shortcuts/quality-of-life input shapes.
ComponentInput: TypeAlias = (
    AnyUIComponentInput[ActionRowChildT, NonActionRowChildT]
    | Sequence[AnyUIComponentInput[ActionRowChildT, NonActionRowChildT] | Sequence[ActionRowChildT]]
)

MessageComponents = ComponentInput[ActionRowMessageComponent, MessageTopLevelComponentV2]

ModalComponents = ComponentInput[
    ActionRowModalComponent,  # deprecated
    ModalTopLevelComponent_,
]
