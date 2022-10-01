# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, Optional, TypedDict, Union

from .channel import ChannelType
from .components import Component, Modal
from .embed import Embed
from .member import Member, MemberWithUser
from .role import Role
from .snowflake import Snowflake
from .user import User

if TYPE_CHECKING:
    from .message import AllowedMentions, Attachment, Message


ApplicationCommandLocalizations = Dict[str, str]


ApplicationCommandType = Literal[1, 2, 3]


class _ApplicationCommandOptional(TypedDict, total=False):
    type: ApplicationCommandType
    guild_id: Snowflake
    options: List[ApplicationCommandOption]
    default_permission: bool  # deprecated
    default_member_permissions: Optional[str]
    dm_permission: Optional[bool]
    name_localizations: Optional[ApplicationCommandLocalizations]
    description_localizations: Optional[ApplicationCommandLocalizations]


class ApplicationCommand(_ApplicationCommandOptional):
    id: Snowflake
    application_id: Snowflake
    name: str
    description: str
    version: Snowflake


class _ApplicationCommandOptionOptional(TypedDict, total=False):
    required: bool
    choices: List[ApplicationCommandOptionChoice]
    options: List[ApplicationCommandOption]
    channel_types: List[ChannelType]
    min_value: float
    max_value: float
    min_length: int
    max_length: int
    autocomplete: bool
    name_localizations: Optional[ApplicationCommandLocalizations]
    description_localizations: Optional[ApplicationCommandLocalizations]


ApplicationCommandOptionType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ApplicationCommandOption(_ApplicationCommandOptionOptional):
    type: ApplicationCommandOptionType
    name: str
    description: str


ApplicationCommandOptionChoiceValue = Union[str, int, float]


class _ApplicationCommandOptionChoiceOptional(TypedDict, total=False):
    name_localizations: Optional[ApplicationCommandLocalizations]


class ApplicationCommandOptionChoice(_ApplicationCommandOptionChoiceOptional):
    name: str
    value: ApplicationCommandOptionChoiceValue


ApplicationCommandPermissionType = Literal[1, 2, 3]


class ApplicationCommandPermissions(TypedDict):
    id: Snowflake
    type: ApplicationCommandPermissionType
    permission: bool


class GuildApplicationCommandPermissions(TypedDict):
    id: Snowflake
    application_id: Snowflake
    guild_id: Snowflake
    permissions: List[ApplicationCommandPermissions]


InteractionType = Literal[1, 2, 3, 4, 5]


class _ApplicationCommandInteractionDataOption(TypedDict):
    name: str


class _ApplicationCommandInteractionDataOptionSubcommand(_ApplicationCommandInteractionDataOption):
    type: Literal[1, 2]
    options: List[ApplicationCommandInteractionDataOption]


class _ApplicationCommandInteractionDataOptionString(_ApplicationCommandInteractionDataOption):
    type: Literal[3]
    value: str


class _ApplicationCommandInteractionDataOptionInteger(_ApplicationCommandInteractionDataOption):
    type: Literal[4]
    value: int


class _ApplicationCommandInteractionDataOptionBoolean(_ApplicationCommandInteractionDataOption):
    type: Literal[5]
    value: bool


class _ApplicationCommandInteractionDataOptionSnowflake(_ApplicationCommandInteractionDataOption):
    type: Literal[6, 7, 8, 9, 11]
    value: Snowflake


class _ApplicationCommandInteractionDataOptionNumber(_ApplicationCommandInteractionDataOption):
    type: Literal[10]
    value: float


ApplicationCommandInteractionDataOption = Union[
    _ApplicationCommandInteractionDataOptionString,
    _ApplicationCommandInteractionDataOptionInteger,
    _ApplicationCommandInteractionDataOptionSubcommand,
    _ApplicationCommandInteractionDataOptionBoolean,
    _ApplicationCommandInteractionDataOptionSnowflake,
    _ApplicationCommandInteractionDataOptionNumber,
]


class ApplicationCommandResolvedPartialChannel(TypedDict):
    id: Snowflake
    type: ChannelType
    permissions: str
    name: str


class ApplicationCommandInteractionDataResolved(TypedDict, total=False):
    users: Dict[Snowflake, User]
    members: Dict[Snowflake, Member]
    roles: Dict[Snowflake, Role]
    channels: Dict[Snowflake, ApplicationCommandResolvedPartialChannel]
    messages: Dict[Snowflake, Message]
    attachments: Dict[Snowflake, Attachment]


class _ApplicationCommandInteractionDataOptional(TypedDict, total=False):
    options: List[ApplicationCommandInteractionDataOption]
    resolved: ApplicationCommandInteractionDataResolved
    target_id: Snowflake


class ApplicationCommandInteractionData(_ApplicationCommandInteractionDataOptional):
    id: Snowflake
    name: str
    type: ApplicationCommandType


## Interaction components


class _BaseComponentInteractionData(TypedDict):
    custom_id: str


### Message interaction components


class MessageComponentInteractionButtonData(_BaseComponentInteractionData):
    component_type: Literal[2]


class MessageComponentInteractionSelectData(_BaseComponentInteractionData):
    component_type: Literal[3]
    values: List[str]


MessageComponentInteractionData = Union[
    MessageComponentInteractionButtonData,
    MessageComponentInteractionSelectData,
]


### Modal interaction components


class ModalInteractionSelectData(_BaseComponentInteractionData):
    type: Literal[3]
    values: List[str]


class ModalInteractionTextInputData(_BaseComponentInteractionData):
    type: Literal[4]
    value: str


ModalInteractionComponentData = Union[
    ModalInteractionSelectData,
    ModalInteractionTextInputData,
]


class ModalInteractionActionRow(TypedDict):
    type: Literal[1]
    components: List[ModalInteractionComponentData]


class ModalInteractionData(TypedDict):
    custom_id: str
    components: List[ModalInteractionActionRow]


## Interactions


# base type for *all* interactions
class _BaseInteraction(TypedDict):
    id: Snowflake
    application_id: Snowflake
    token: str
    version: Literal[1]


# common properties in non-ping interactions
class _BaseUserInteractionOptional(TypedDict, total=False):
    app_permissions: str
    guild_id: Snowflake
    guild_locale: str
    # one of these two will always exist, according to docs
    member: MemberWithUser
    user: User


class _BaseUserInteraction(_BaseInteraction, _BaseUserInteractionOptional):
    # the docs specify `channel_id` as optional,
    # but it is assumed to always exist on non-ping interactions
    channel_id: Snowflake
    locale: str


class PingInteraction(_BaseInteraction):
    type: Literal[1]


class ApplicationCommandInteraction(_BaseUserInteraction):
    type: Literal[2, 4]
    data: ApplicationCommandInteractionData


class MessageInteraction(_BaseUserInteraction):
    type: Literal[3]
    data: MessageComponentInteractionData
    message: Message


class _ModalInteractionOptional(TypedDict, total=False):
    message: Message


class ModalInteraction(_BaseUserInteraction, _ModalInteractionOptional):
    type: Literal[5]
    data: ModalInteractionData


Interaction = Union[
    ApplicationCommandInteraction,
    MessageInteraction,
    ModalInteraction,
]

BaseInteraction = Union[Interaction, PingInteraction]


class InteractionApplicationCommandCallbackData(TypedDict, total=False):
    tts: bool
    content: str
    embeds: List[Embed]
    allowed_mentions: AllowedMentions
    flags: int
    components: List[Component]


class InteractionAutocompleteCallbackData(TypedDict):
    choices: List[ApplicationCommandOptionChoice]


InteractionResponseType = Literal[1, 4, 5, 6, 7]

InteractionCallbackData = Union[
    InteractionApplicationCommandCallbackData,
    InteractionAutocompleteCallbackData,
    Modal,
]


class _InteractionResponseOptional(TypedDict, total=False):
    data: InteractionCallbackData


class InteractionResponse(_InteractionResponseOptional):
    type: InteractionResponseType


class InteractionMessageReference(TypedDict):
    id: Snowflake
    type: InteractionType
    name: str
    user: User


class _EditApplicationCommandOptional(TypedDict, total=False):
    description: str
    options: Optional[List[ApplicationCommandOption]]
    default_member_permissions: Optional[str]
    dm_permission: bool
    type: ApplicationCommandType
    default_permission: bool  # deprecated
    name_localizations: Optional[ApplicationCommandLocalizations]
    description_localizations: Optional[ApplicationCommandLocalizations]


class EditApplicationCommand(_EditApplicationCommandOptional):
    name: str
