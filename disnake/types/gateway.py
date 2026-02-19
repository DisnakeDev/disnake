# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeAlias, TypedDict

from typing_extensions import NotRequired

from .activity import PartialPresenceUpdate
from .audit_log import AuditLogEntry
from .automod import AutoModRule
from .channel import Channel, GuildChannel, StageInstance
from .entitlement import Entitlement
from .guild import Guild, UnavailableGuild
from .guild_scheduled_event import GuildScheduledEvent
from .integration import BaseIntegration
from .interactions import BaseInteraction, GuildApplicationCommandPermissions
from .member import MemberWithUser
from .message import Message
from .soundboard import GuildSoundboardSound
from .subscription import Subscription
from .threads import Thread, ThreadMember
from .user import User
from .voice import GuildVoiceState, VoiceChannelEffect

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .activity import PresenceData, SendableActivity
    from .appinfo import PartialAppInfo, PartialGatewayAppInfo
    from .automod import AutoModAction, AutoModTriggerType
    from .emoji import Emoji, PartialEmoji
    from .invite import InviteTargetType, InviteType
    from .role import Role
    from .snowflake import Snowflake, SnowflakeList
    from .sticker import GuildSticker
    from .threads import ThreadMemberWithPresence, ThreadType
    from .user import AvatarDecorationData
    from .voice import SupportedModes


class SessionStartLimit(TypedDict):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class Gateway(TypedDict):
    url: str


class GatewayBot(Gateway):
    shards: int
    session_start_limit: SessionStartLimit


#####
# Websocket payloads (receive)
#####


class GatewayPayload(TypedDict):
    op: Literal[0, 1, 7, 9, 10, 11]
    d: Any  # event data
    s: int | None  # sequence number
    t: str | None  # event name


#####
# Websocket payloads (send)
#####

# opcode 1


class HeartbeatCommand(TypedDict):
    op: Literal[1, 3]  # normal ws and voice ws have different heartbeat opcodes
    # normal ws uses a plain int seq, voice ws uses {t: <nonce>, seq_ack: <seq>}
    d: int | None | VoiceHeartbeatData


# opcode 2


class IdentifyProperties(TypedDict):
    os: str
    browser: str
    device: str


class IdentifyData(TypedDict):
    token: str
    properties: IdentifyProperties
    compress: NotRequired[bool]
    large_threshold: NotRequired[int]
    shard: NotRequired[tuple[int, int]]
    presence: NotRequired[PresenceUpdateData]
    intents: int


class IdentifyCommand(TypedDict):
    op: Literal[2]
    d: IdentifyData


# opcode 3


class PresenceUpdateData(TypedDict):
    since: int | None
    activities: Sequence[SendableActivity]
    status: str
    afk: bool


class PresenceUpdateCommand(TypedDict):
    op: Literal[3]
    d: PresenceUpdateData


# opcode 4


class VoiceStateData(TypedDict):
    guild_id: Snowflake
    channel_id: Snowflake | None
    self_mute: bool
    self_deaf: bool


class VoiceStateCommand(TypedDict):
    op: Literal[4]
    d: VoiceStateData


# opcode 6


class ResumeData(TypedDict):
    token: str
    session_id: str
    seq: int


class ResumeCommand(TypedDict):
    op: Literal[6]
    d: ResumeData


# opcode 8


class RequestMembersData(TypedDict):
    guild_id: Snowflake
    query: NotRequired[str]
    limit: int
    presences: NotRequired[bool]
    user_ids: NotRequired[Snowflake | SnowflakeList]
    nonce: NotRequired[str]


class RequestMembersCommand(TypedDict):
    op: Literal[8]
    d: RequestMembersData


#####
# Voice payloads (receive)
#####


class VoicePayload(TypedDict):
    op: Literal[2, 4, 6, 8, 9]
    d: Any
    seq: NotRequired[int]  # only present in some messages


# voice opcode 2


class VoiceReadyPayload(TypedDict):
    ssrc: int
    ip: str
    port: int
    modes: list[str]


# voice opcode 4


class VoiceSessionDescriptionPayload(TypedDict):
    mode: SupportedModes
    secret_key: list[int]


# voice opcode 6


class VoiceHeartbeatAckPayload(TypedDict):
    t: int


# voice opcode 8


class VoiceHelloPayload(TypedDict):
    heartbeat_interval: int


# voice opcode 9


VoiceResumedPayload = None


#####
# Voice payloads (send)
#####

# voice opcode 0


class VoiceIdentifyData(TypedDict):
    server_id: str
    user_id: str
    session_id: str
    token: str


class VoiceIdentifyCommand(TypedDict):
    op: Literal[0]
    d: VoiceIdentifyData


# voice opcode 1


class _VoiceSelectProtocolInnerData(TypedDict):
    address: str
    port: int
    mode: SupportedModes


class VoiceSelectProtocolData(TypedDict):
    protocol: Literal["udp"]
    data: _VoiceSelectProtocolInnerData


class VoiceSelectProtocolCommand(TypedDict):
    op: Literal[1]
    d: VoiceSelectProtocolData


# voice opcode 3


class VoiceHeartbeatData(TypedDict):
    t: int  # nonce
    seq_ack: int


class VoiceHeartbeatCommand(TypedDict):
    op: Literal[3]
    d: VoiceHeartbeatData


# voice opcode 5


class VoiceSpeakingData(TypedDict):
    speaking: int  # bitfield of 3 bits
    delay: int
    ssrc: int


class VoiceSpeakingCommand(TypedDict):
    op: Literal[5]
    d: VoiceSpeakingData


# voice opcode 7


class VoiceResumeData(TypedDict):
    server_id: str
    session_id: str
    token: str
    seq_ack: int


class VoiceResumeCommand(TypedDict):
    op: Literal[7]
    d: VoiceResumeData


#####
# Gateway events
#####


# https://docs.discord.com/developers/events/gateway-events#ready
class ReadyEvent(TypedDict):
    v: int
    user: User
    guilds: list[UnavailableGuild]
    session_id: str
    resume_gateway_url: str
    shard: NotRequired[tuple[int, int]]
    application: PartialGatewayAppInfo


# https://docs.discord.com/developers/events/gateway-events#resumed
class ResumedEvent(TypedDict): ...


# https://docs.discord.com/developers/events/gateway-events#application-command-permissions-update
ApplicationCommandPermissionsUpdateEvent: TypeAlias = GuildApplicationCommandPermissions


# https://docs.discord.com/developers/events/gateway-events#message-create
MessageCreateEvent: TypeAlias = Message


# https://docs.discord.com/developers/events/gateway-events#message-update
# This does not necessarily contain all message fields, but `id` and `channel_id` always exist
MessageUpdateEvent: TypeAlias = Message


# https://docs.discord.com/developers/events/gateway-events#message-delete
class MessageDeleteEvent(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


# https://docs.discord.com/developers/events/gateway-events#message-delete-bulk
class MessageDeleteBulkEvent(TypedDict):
    ids: list[Snowflake]
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


class _BaseReactionEvent(TypedDict):
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]
    emoji: PartialEmoji


# https://docs.discord.com/developers/events/gateway-events#message-reaction-add
class MessageReactionAddEvent(_BaseReactionEvent):
    member: NotRequired[MemberWithUser]
    message_author_id: NotRequired[Snowflake]


# https://docs.discord.com/developers/events/gateway-events#message-reaction-remove
class MessageReactionRemoveEvent(_BaseReactionEvent): ...


# https://docs.discord.com/developers/events/gateway-events#message-reaction-remove-all
class MessageReactionRemoveAllEvent(TypedDict):
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]


# https://docs.discord.com/developers/events/gateway-events#message-reaction-remove-emoji
class MessageReactionRemoveEmojiEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    message_id: Snowflake
    emoji: PartialEmoji


# https://docs.discord.com/developers/events/gateway-events#message-poll-vote-add
class PollVoteAddEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    message_id: Snowflake
    user_id: Snowflake
    answer_id: int


# https://docs.discord.com/developers/events/gateway-events#message-poll-vote-remove
class PollVoteRemoveEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    message_id: Snowflake
    user_id: Snowflake
    answer_id: int


# https://docs.discord.com/developers/events/gateway-events#interaction-create
InteractionCreateEvent: TypeAlias = BaseInteraction


# https://docs.discord.com/developers/events/gateway-events#presence-update
PresenceUpdateEvent: TypeAlias = PartialPresenceUpdate


# https://docs.discord.com/developers/events/gateway-events#user-update
UserUpdateEvent: TypeAlias = User


# https://docs.discord.com/developers/events/gateway-events#invite-create
class InviteCreateEvent(TypedDict):
    channel_id: Snowflake
    code: str
    created_at: str
    guild_id: NotRequired[Snowflake]
    inviter: NotRequired[User]
    max_age: int
    max_uses: int
    target_type: NotRequired[InviteTargetType]
    target_user: NotRequired[User]
    target_application: NotRequired[PartialAppInfo]
    temporary: bool
    type: InviteType
    uses: int  # always 0


# https://docs.discord.com/developers/events/gateway-events#invite-delete
class InviteDeleteEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    code: str


# https://docs.discord.com/developers/events/gateway-events#channel-create
ChannelCreateEvent: TypeAlias = GuildChannel


# https://docs.discord.com/developers/events/gateway-events#channel-update
ChannelUpdateEvent: TypeAlias = Channel


# https://docs.discord.com/developers/events/gateway-events#channel-delete
ChannelDeleteEvent: TypeAlias = Channel


# https://docs.discord.com/developers/events/gateway-events#channel-pins-update
class ChannelPinsUpdateEvent(TypedDict):
    guild_id: NotRequired[Snowflake]
    channel_id: Snowflake
    last_pin_timestamp: NotRequired[str | None]


# https://docs.discord.com/developers/events/gateway-events#thread-create
class ThreadCreateEvent(Thread):
    newly_created: NotRequired[bool]


# https://docs.discord.com/developers/events/gateway-events#thread-update
ThreadUpdateEvent: TypeAlias = Thread


# https://docs.discord.com/developers/events/gateway-events#thread-delete
class ThreadDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    parent_id: Snowflake
    type: ThreadType


# https://docs.discord.com/developers/events/gateway-events#thread-list-sync
class ThreadListSyncEvent(TypedDict):
    guild_id: Snowflake
    channel_ids: NotRequired[list[Snowflake]]
    threads: list[Thread]
    members: list[ThreadMember]


# https://docs.discord.com/developers/events/gateway-events#thread-member-update
class ThreadMemberUpdateEvent(ThreadMember):
    guild_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#thread-members-update
class ThreadMembersUpdateEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    member_count: int
    added_members: NotRequired[list[ThreadMemberWithPresence]]
    removed_member_ids: NotRequired[list[Snowflake]]


# https://docs.discord.com/developers/events/gateway-events#guild-member-add
class GuildMemberAddEvent(MemberWithUser):
    guild_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#guild-member-remove
class GuildMemberRemoveEvent(TypedDict):
    guild_id: Snowflake
    user: User


# https://docs.discord.com/developers/events/gateway-events#guild-member-update
class GuildMemberUpdateEvent(TypedDict):
    guild_id: Snowflake
    roles: list[Snowflake]
    user: User
    nick: NotRequired[str | None]
    avatar: str | None
    banner: str | None
    joined_at: str | None
    premium_since: NotRequired[str | None]
    deaf: NotRequired[bool]
    mute: NotRequired[bool]
    pending: NotRequired[bool]
    communication_disabled_until: NotRequired[str | None]
    flags: int
    avatar_decoration_data: NotRequired[AvatarDecorationData | None]


# https://docs.discord.com/developers/events/gateway-events#guild-emojis-update
class GuildEmojisUpdateEvent(TypedDict):
    guild_id: Snowflake
    emojis: list[Emoji]


# https://docs.discord.com/developers/events/gateway-events#guild-stickers-update
class GuildStickersUpdateEvent(TypedDict):
    guild_id: Snowflake
    stickers: list[GuildSticker]


# https://docs.discord.com/developers/events/gateway-events#guild-create
GuildCreateEvent: TypeAlias = Guild | UnavailableGuild


# https://docs.discord.com/developers/events/gateway-events#guild-update
GuildUpdateEvent: TypeAlias = Guild


# https://docs.discord.com/developers/events/gateway-events#guild-delete
GuildDeleteEvent: TypeAlias = UnavailableGuild


# https://docs.discord.com/developers/events/gateway-events#guild-audit-log-entry-create
class AuditLogEntryCreate(AuditLogEntry):
    guild_id: Snowflake


class _GuildBanEvent(TypedDict):
    guild_id: Snowflake
    user: User


# https://docs.discord.com/developers/events/gateway-events#guild-ban-add
GuildBanAddEvent: TypeAlias = _GuildBanEvent


# https://docs.discord.com/developers/events/gateway-events#guild-ban-remove
GuildBanRemoveEvent: TypeAlias = _GuildBanEvent


# https://docs.discord.com/developers/events/gateway-events#guild-role-create
class GuildRoleCreateEvent(TypedDict):
    guild_id: Snowflake
    role: Role


# https://docs.discord.com/developers/events/gateway-events#guild-role-delete
class GuildRoleDeleteEvent(TypedDict):
    guild_id: Snowflake
    role_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#guild-role-update
class GuildRoleUpdateEvent(TypedDict):
    guild_id: Snowflake
    role: Role


# https://docs.discord.com/developers/events/gateway-events#guild-scheduled-event-create
GuildScheduledEventCreateEvent: TypeAlias = GuildScheduledEvent


# https://docs.discord.com/developers/events/gateway-events#guild-scheduled-event-update
GuildScheduledEventUpdateEvent: TypeAlias = GuildScheduledEvent


# https://docs.discord.com/developers/events/gateway-events#guild-scheduled-event-delete
GuildScheduledEventDeleteEvent: TypeAlias = GuildScheduledEvent


class _GuildScheduledEventUserEvent(TypedDict):
    guild_scheduled_event_id: Snowflake
    user_id: Snowflake
    guild_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#guild-scheduled-event-user-add
GuildScheduledEventUserAddEvent: TypeAlias = _GuildScheduledEventUserEvent


# https://docs.discord.com/developers/events/gateway-events#guild-scheduled-event-user-remove
GuildScheduledEventUserRemoveEvent: TypeAlias = _GuildScheduledEventUserEvent


# https://docs.discord.com/developers/events/gateway-events#guild-members-chunk
class GuildMembersChunkEvent(TypedDict):
    guild_id: Snowflake
    members: list[MemberWithUser]
    chunk_index: int
    chunk_count: int
    not_found: NotRequired[list[Snowflake]]
    presences: NotRequired[list[PresenceData]]
    nonce: NotRequired[str]


# https://docs.discord.com/developers/events/gateway-events#guild-integrations-update
class GuildIntegrationsUpdateEvent(TypedDict):
    guild_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#integration-create
class IntegrationCreateEvent(BaseIntegration):
    guild_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#integration-update
class IntegrationUpdateEvent(BaseIntegration):
    guild_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#integration-delete
class IntegrationDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    application_id: NotRequired[Snowflake]


# https://docs.discord.com/developers/events/gateway-events#webhooks-update
class WebhooksUpdateEvent(TypedDict):
    guild_id: Snowflake
    channel_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#stage-instance-create
StageInstanceCreateEvent = StageInstance


# https://docs.discord.com/developers/events/gateway-events#stage-instance-update
StageInstanceUpdateEvent: TypeAlias = StageInstance


# https://docs.discord.com/developers/events/gateway-events#stage-instance-delete
StageInstanceDeleteEvent: TypeAlias = StageInstance


# https://docs.discord.com/developers/events/gateway-events#voice-state-update
# We assume that we'll only receive voice states for guilds
VoiceStateUpdateEvent: TypeAlias = GuildVoiceState


# https://docs.discord.com/developers/events/gateway-events#voice-server-update
class VoiceServerUpdateEvent(TypedDict):
    token: str
    guild_id: Snowflake
    endpoint: str | None


# https://docs.discord.com/developers/events/gateway-events#voice-channel-effect-send
class VoiceChannelEffectSendEvent(VoiceChannelEffect):
    channel_id: Snowflake
    guild_id: Snowflake
    user_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#typing-start
class TypingStartEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    user_id: Snowflake
    timestamp: int
    member: NotRequired[MemberWithUser]


# https://docs.discord.com/developers/events/gateway-events#auto-moderation-rule-create
AutoModerationRuleCreateEvent: TypeAlias = AutoModRule


# https://docs.discord.com/developers/events/gateway-events#auto-moderation-rule-update
AutoModerationRuleUpdateEvent: TypeAlias = AutoModRule


# https://docs.discord.com/developers/events/gateway-events#auto-moderation-rule-delete
AutoModerationRuleDeleteEvent: TypeAlias = AutoModRule


# https://docs.discord.com/developers/events/gateway-events#auto-moderation-action-execution
class AutoModerationActionExecutionEvent(TypedDict):
    guild_id: Snowflake
    action: AutoModAction
    rule_id: Snowflake
    rule_trigger_type: AutoModTriggerType
    user_id: Snowflake
    channel_id: NotRequired[Snowflake | None]
    message_id: NotRequired[Snowflake | None]
    alert_system_message_id: NotRequired[Snowflake | None]
    content: NotRequired[str]
    matched_content: NotRequired[str | None]
    matched_keyword: NotRequired[str | None]


# https://docs.discord.com/developers/events/gateway-events#entitlement-create
EntitlementCreate: TypeAlias = Entitlement


# https://docs.discord.com/developers/events/gateway-events#entitlement-update
EntitlementUpdate: TypeAlias = Entitlement


# https://docs.discord.com/developers/events/gateway-events#entitlement-delete
EntitlementDelete: TypeAlias = Entitlement


# https://docs.discord.com/developers/events/gateway-events#subscription-create
SubscriptionCreate: TypeAlias = Subscription


# https://docs.discord.com/developers/events/gateway-events#subscription-update
SubscriptionUpdate: TypeAlias = Subscription


# https://docs.discord.com/developers/events/gateway-events#subscription-delete
SubscriptionDelete: TypeAlias = Subscription


# https://docs.discord.com/developers/events/gateway-events#guild-soundboard-sound-create
GuildSoundboardSoundCreate: TypeAlias = GuildSoundboardSound


# https://docs.discord.com/developers/events/gateway-events#guild-soundboard-sound-update
GuildSoundboardSoundUpdate: TypeAlias = GuildSoundboardSound


# https://docs.discord.com/developers/events/gateway-events#guild-soundboard-sound-delete
class GuildSoundboardSoundDelete(TypedDict):
    guild_id: Snowflake
    sound_id: Snowflake


# https://docs.discord.com/developers/events/gateway-events#guild-soundboard-sounds-update
class GuildSoundboardSoundsUpdate(TypedDict):
    guild_id: Snowflake
    soundboard_sounds: list[GuildSoundboardSound]
