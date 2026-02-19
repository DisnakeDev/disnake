# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias, TypedDict

from .appinfo import ApplicationIntegrationType
from .channel import ChannelType
from .components import MessageTopLevelComponent, Modal
from .embed import Embed
from .entitlement import Entitlement
from .i18n import LocalizationDict
from .member import Member, MemberWithUser
from .role import Role
from .snowflake import Snowflake
from .threads import ThreadMetadata
from .user import User

if TYPE_CHECKING:
    from typing import TypeAlias

    from typing_extensions import NotRequired

    from .message import AllowedMentions, Attachment, Message


ApplicationCommandType = Literal[1, 2, 3]

InteractionContextType = Literal[1, 2, 3]  # GUILD, BOT_DM, PRIVATE_CHANNEL


class ApplicationCommand(TypedDict):
    id: Snowflake
    type: NotRequired[ApplicationCommandType]
    application_id: Snowflake
    guild_id: NotRequired[Snowflake]
    name: str
    name_localizations: NotRequired[LocalizationDict | None]
    description: str
    description_localizations: NotRequired[LocalizationDict | None]
    options: NotRequired[list[ApplicationCommandOption]]
    default_member_permissions: NotRequired[str | None]
    dm_permission: NotRequired[bool | None]  # deprecated
    default_permission: NotRequired[bool]  # deprecated
    nsfw: NotRequired[bool]
    integration_types: NotRequired[list[ApplicationIntegrationType]]
    contexts: NotRequired[list[InteractionContextType] | None]
    version: Snowflake


ApplicationCommandOptionType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ApplicationCommandOption(TypedDict):
    type: ApplicationCommandOptionType
    name: str
    name_localizations: NotRequired[LocalizationDict | None]
    description: str
    description_localizations: NotRequired[LocalizationDict | None]
    required: NotRequired[bool]
    choices: NotRequired[list[ApplicationCommandOptionChoice]]
    options: NotRequired[list[ApplicationCommandOption]]
    channel_types: NotRequired[list[ChannelType]]
    min_value: NotRequired[float]
    max_value: NotRequired[float]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    autocomplete: NotRequired[bool]


ApplicationCommandOptionChoiceValue: TypeAlias = str | int | float


class ApplicationCommandOptionChoice(TypedDict):
    name: str
    name_localizations: NotRequired[LocalizationDict | None]
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
    permissions: list[ApplicationCommandPermissions]


InteractionType = Literal[1, 2, 3, 4, 5]


class InteractionChannel(TypedDict):
    id: Snowflake
    type: ChannelType
    permissions: str
    name: str

    # only in threads
    thread_metadata: NotRequired[ThreadMetadata]
    parent_id: NotRequired[Snowflake]


class InteractionDataResolved(TypedDict, total=False):
    users: dict[Snowflake, User]
    members: dict[Snowflake, Member]
    roles: dict[Snowflake, Role]
    channels: dict[Snowflake, InteractionChannel]


class ApplicationCommandInteractionDataResolved(InteractionDataResolved, total=False):
    messages: dict[Snowflake, Message]
    attachments: dict[Snowflake, Attachment]


class _ApplicationCommandInteractionDataOption(TypedDict):
    name: str


class _ApplicationCommandInteractionDataOptionSubcommand(_ApplicationCommandInteractionDataOption):
    type: Literal[1, 2]
    options: list[ApplicationCommandInteractionDataOption]


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


ApplicationCommandInteractionDataOption: TypeAlias = (
    _ApplicationCommandInteractionDataOptionString
    | _ApplicationCommandInteractionDataOptionInteger
    | _ApplicationCommandInteractionDataOptionSubcommand
    | _ApplicationCommandInteractionDataOptionBoolean
    | _ApplicationCommandInteractionDataOptionSnowflake
    | _ApplicationCommandInteractionDataOptionNumber
)


class ApplicationCommandInteractionData(TypedDict):
    id: Snowflake
    name: str
    type: ApplicationCommandType
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    options: NotRequired[list[ApplicationCommandInteractionDataOption]]
    # this is the guild the command is registered to, not the guild the command was invoked in (see interaction.guild_id)
    guild_id: NotRequired[Snowflake]
    target_id: NotRequired[Snowflake]


## Interaction components


class _BaseComponentInteractionData(TypedDict):
    id: int


class _BaseCustomIdComponentInteractionData(_BaseComponentInteractionData):
    custom_id: str


### Message interaction components


class _BaseSnowflakeMessageComponentInteractionData(_BaseCustomIdComponentInteractionData):
    values: list[Snowflake]
    resolved: NotRequired[InteractionDataResolved]


class MessageComponentInteractionButtonData(_BaseCustomIdComponentInteractionData):
    component_type: Literal[2]


class MessageComponentInteractionStringSelectData(_BaseCustomIdComponentInteractionData):
    component_type: Literal[3]
    values: list[str]


class MessageComponentInteractionUserSelectData(_BaseSnowflakeMessageComponentInteractionData):
    component_type: Literal[5]


class MessageComponentInteractionRoleSelectData(_BaseSnowflakeMessageComponentInteractionData):
    component_type: Literal[6]


class MessageComponentInteractionMentionableSelectData(
    _BaseSnowflakeMessageComponentInteractionData
):
    component_type: Literal[7]


class MessageComponentInteractionChannelSelectData(_BaseSnowflakeMessageComponentInteractionData):
    component_type: Literal[8]


MessageComponentInteractionData: TypeAlias = (
    MessageComponentInteractionButtonData
    | MessageComponentInteractionStringSelectData
    | MessageComponentInteractionUserSelectData
    | MessageComponentInteractionRoleSelectData
    | MessageComponentInteractionMentionableSelectData
    | MessageComponentInteractionChannelSelectData
)


### Modal interaction components


class _BaseSnowflakeModalComponentInteractionData(_BaseCustomIdComponentInteractionData):
    values: list[Snowflake]


class ModalInteractionStringSelectData(_BaseCustomIdComponentInteractionData):
    type: Literal[3]
    values: list[str]


class ModalInteractionTextInputData(_BaseCustomIdComponentInteractionData):
    type: Literal[4]
    value: str


class ModalInteractionUserSelectData(_BaseSnowflakeModalComponentInteractionData):
    type: Literal[5]


class ModalInteractionRoleSelectData(_BaseSnowflakeModalComponentInteractionData):
    type: Literal[6]


class ModalInteractionMentionableSelectData(_BaseSnowflakeModalComponentInteractionData):
    type: Literal[7]


class ModalInteractionChannelSelectData(_BaseSnowflakeModalComponentInteractionData):
    type: Literal[8]


class ModalInteractionFileUploadData(_BaseSnowflakeModalComponentInteractionData):
    type: Literal[19]


# top-level modal component data

ModalInteractionActionRowChildData: TypeAlias = ModalInteractionTextInputData


class ModalInteractionActionRowData(_BaseComponentInteractionData):
    type: Literal[1]
    components: list[ModalInteractionActionRowChildData]


class ModalInteractionTextDisplayData(_BaseComponentInteractionData):
    type: Literal[10]


ModalInteractionLabelChildData: TypeAlias = (
    ModalInteractionStringSelectData
    | ModalInteractionTextInputData
    | ModalInteractionUserSelectData
    | ModalInteractionRoleSelectData
    | ModalInteractionMentionableSelectData
    | ModalInteractionChannelSelectData
    | ModalInteractionFileUploadData
)


class ModalInteractionLabelData(_BaseComponentInteractionData):
    type: Literal[18]
    component: ModalInteractionLabelChildData


# innermost (non-layout) components, i.e. those containing user input
ModalInteractionInnerComponentData: TypeAlias = (
    ModalInteractionActionRowChildData | ModalInteractionLabelChildData
)

# top-level components
ModalInteractionComponentData: TypeAlias = (
    ModalInteractionActionRowData | ModalInteractionTextDisplayData | ModalInteractionLabelData
)


class ModalInteractionData(TypedDict):
    custom_id: str
    components: list[ModalInteractionComponentData]
    resolved: NotRequired[InteractionDataResolved]


## Interactions


# keys are stringified ApplicationInstallType's
AuthorizingIntegrationOwners = dict[str, Snowflake]


# base type for *all* interactions
class _BaseInteraction(TypedDict):
    id: Snowflake
    application_id: Snowflake
    token: str
    version: Literal[1]
    app_permissions: str
    attachment_size_limit: int


# common properties in non-ping interactions
class _BaseUserInteraction(_BaseInteraction):
    # the docs specify `channel_id` and 'channel` as optional,
    # but they're assumed to always exist on non-ping interactions
    channel_id: Snowflake
    channel: InteractionChannel
    locale: str
    guild_id: NotRequired[Snowflake]
    guild_locale: NotRequired[str]
    entitlements: NotRequired[list[Entitlement]]
    authorizing_integration_owners: NotRequired[AuthorizingIntegrationOwners]
    context: NotRequired[InteractionContextType]
    # one of these two will always exist, according to docs
    member: NotRequired[MemberWithUser]
    user: NotRequired[User]


class PingInteraction(_BaseInteraction):
    type: Literal[1]


class ApplicationCommandInteraction(_BaseUserInteraction):
    type: Literal[2, 4]
    data: ApplicationCommandInteractionData


class MessageInteraction(_BaseUserInteraction):
    type: Literal[3]
    data: MessageComponentInteractionData
    message: Message


class ModalInteraction(_BaseUserInteraction):
    type: Literal[5]
    data: ModalInteractionData
    message: NotRequired[Message]


Interaction: TypeAlias = ApplicationCommandInteraction | MessageInteraction | ModalInteraction

BaseInteraction: TypeAlias = Interaction | PingInteraction


class InteractionApplicationCommandCallbackData(TypedDict, total=False):
    tts: bool
    content: str
    embeds: list[Embed]
    allowed_mentions: AllowedMentions
    flags: int
    components: list[MessageTopLevelComponent]
    attachments: list[Attachment]


class InteractionAutocompleteCallbackData(TypedDict):
    choices: list[ApplicationCommandOptionChoice]


InteractionResponseType: TypeAlias = Literal[1, 4, 5, 6, 7, 10]

InteractionCallbackData: TypeAlias = (
    InteractionApplicationCommandCallbackData | InteractionAutocompleteCallbackData | Modal
)


class InteractionResponse(TypedDict):
    type: InteractionResponseType
    data: NotRequired[InteractionCallbackData]


class InteractionMessageReference(TypedDict):
    id: Snowflake
    type: InteractionType
    name: str
    user: User
    member: NotRequired[Member]


class _BaseInteractionMetadata(TypedDict):
    id: Snowflake
    type: InteractionType
    user: User
    authorizing_integration_owners: AuthorizingIntegrationOwners
    original_response_message_id: NotRequired[Snowflake]  # only on followups


class ApplicationCommandInteractionMetadata(_BaseInteractionMetadata):
    target_user: NotRequired[User]  # only on user command interactions
    target_message_id: NotRequired[Snowflake]  # only on message command interactions


class MessageComponentInteractionMetadata(_BaseInteractionMetadata):
    interacted_message_id: Snowflake


class ModalInteractionMetadata(_BaseInteractionMetadata):
    triggering_interaction_metadata: (
        ApplicationCommandInteractionMetadata | MessageComponentInteractionMetadata
    )


InteractionMetadata: TypeAlias = (
    ApplicationCommandInteractionMetadata
    | MessageComponentInteractionMetadata
    | ModalInteractionMetadata
)


class EditApplicationCommand(TypedDict):
    name: str
    name_localizations: NotRequired[LocalizationDict | None]
    description: NotRequired[str]
    description_localizations: NotRequired[LocalizationDict | None]
    options: NotRequired[list[ApplicationCommandOption] | None]
    default_member_permissions: NotRequired[str | None]
    dm_permission: NotRequired[bool]  # deprecated
    default_permission: NotRequired[bool]  # deprecated
    nsfw: NotRequired[bool]
    integration_types: NotRequired[list[ApplicationIntegrationType] | None]
    contexts: NotRequired[list[InteractionContextType] | None]
    # n.b. this cannot be changed
    type: NotRequired[ApplicationCommandType]
