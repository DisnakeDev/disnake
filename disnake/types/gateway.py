# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, List, Literal, Optional, Sequence, Tuple, TypedDict, Union

from typing_extensions import NotRequired

from .activity import PartialPresenceUpdate, PresenceData, SendableActivity
from .appinfo import PartialAppInfo, PartialGatewayAppInfo
from .automod import AutoModAction, AutoModRule, AutoModTriggerType
from .channel import Channel, GuildChannel, StageInstance
from .emoji import Emoji, PartialEmoji
from .guild import Guild, UnavailableGuild
from .guild_scheduled_event import GuildScheduledEvent
from .integration import BaseIntegration
from .interactions import BaseInteraction, GuildApplicationCommandPermissions
from .invite import InviteTargetType
from .member import MemberWithUser
from .message import Message
from .role import Role
from .snowflake import Snowflake, SnowflakeList
from .sticker import GuildSticker
from .threads import Thread, ThreadMember, ThreadMemberWithPresence, ThreadType
from .user import User
from .voice import GuildVoiceState, SupportedModes


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
    s: Optional[int]  # sequence number
    t: Optional[str]  # event name


#####
# Websocket payloads (send)
#####

# opcode 1


class HeartbeatCommand(TypedDict):
    op: Literal[1, 3]  # normal ws and voice ws have different heartbeat opcodes
    d: Optional[int]


# opcode 2


class IdentifyProperties(TypedDict):
    os: str
    browser: str
    device: str


class _IdentifyDataOptional(TypedDict, total=False):
    compress: bool
    large_threshold: int
    shard: Tuple[int, int]
    presence: PresenceUpdateData


class IdentifyData(_IdentifyDataOptional):
    token: str
    properties: IdentifyProperties
    intents: int


class IdentifyCommand(TypedDict):
    op: Literal[2]
    d: IdentifyData


# opcode 3


class PresenceUpdateData(TypedDict):
    since: Optional[int]
    activities: Sequence[SendableActivity]
    status: str
    afk: bool


class PresenceUpdateCommand(TypedDict):
    op: Literal[3]
    d: PresenceUpdateData


# opcode 4


class VoiceStateData(TypedDict):
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
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


class _RequestMembersDataOptional(TypedDict, total=False):
    query: str
    presences: bool
    user_ids: Union[Snowflake, SnowflakeList]
    nonce: str


class RequestMembersData(_RequestMembersDataOptional):
    guild_id: Snowflake
    limit: int


class RequestMembersCommand(TypedDict):
    op: Literal[8]
    d: RequestMembersData


#####
# Voice payloads (receive)
#####


class VoicePayload(TypedDict):
    op: Literal[2, 4, 6, 8, 9]
    d: Any


class VoiceReadyPayload(TypedDict):
    ssrc: int
    ip: str
    port: int
    modes: List[str]


class VoiceSessionDescriptionPayload(TypedDict):
    mode: SupportedModes
    secret_key: List[int]


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


class VoiceResumeCommand(TypedDict):
    op: Literal[7]
    d: VoiceResumeData


#####
# Gateway events
#####

# https://discord.com/developers/docs/topics/gateway#ready
class ReadyEvent(TypedDict):
    v: int
    user: User
    guilds: List[UnavailableGuild]
    session_id: str
    resume_gateway_url: str
    shard: NotRequired[Tuple[int, int]]
    application: PartialGatewayAppInfo


# https://discord.com/developers/docs/topics/gateway#resumed
class ResumedEvent(TypedDict):
    ...


# https://discord.com/developers/docs/topics/gateway#application-command-permissions-update
ApplicationCommandPermissionsUpdateEvent = GuildApplicationCommandPermissions


# https://discord.com/developers/docs/topics/gateway#message-create
MessageCreateEvent = Message


# https://discord.com/developers/docs/topics/gateway#message-update
# This does not necessarily contain all message fields, but `id` and `channel_id` always exist
MessageUpdateEvent = Message


# https://discord.com/developers/docs/topics/gateway#message-delete
class MessageDeleteEvent(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


# https://discord.com/developers/docs/topics/gateway#message-delete-bulk
class MessageDeleteBulkEvent(TypedDict):
    ids: List[Snowflake]
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


class _BaseReactionEvent(TypedDict):
    user_id: Snowflake
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]
    emoji: PartialEmoji


# https://discord.com/developers/docs/topics/gateway#message-reaction-add
class MessageReactionAddEvent(_BaseReactionEvent):
    member: NotRequired[MemberWithUser]


# https://discord.com/developers/docs/topics/gateway#message-reaction-remove
class MessageReactionRemoveEvent(_BaseReactionEvent):
    ...


# https://discord.com/developers/docs/topics/gateway#message-reaction-remove-all
class MessageReactionRemoveAllEvent(TypedDict):
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: NotRequired[Snowflake]


# https://discord.com/developers/docs/topics/gateway#message-reaction-remove-emoji
class MessageReactionRemoveEmojiEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    message_id: Snowflake
    emoji: PartialEmoji


# https://discord.com/developers/docs/topics/gateway#interaction-create
InteractionCreateEvent = BaseInteraction


# https://discord.com/developers/docs/topics/gateway#presence-update
PresenceUpdateEvent = PartialPresenceUpdate


# https://discord.com/developers/docs/topics/gateway#user-update
UserUpdateEvent = User


# https://discord.com/developers/docs/topics/gateway#invite-create
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
    uses: int  # always 0


# https://discord.com/developers/docs/topics/gateway#invite-delete
class InviteDeleteEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    code: str


# https://discord.com/developers/docs/topics/gateway#channel-create
ChannelCreateEvent = GuildChannel


# https://discord.com/developers/docs/topics/gateway#channel-update
ChannelUpdateEvent = Channel


# https://discord.com/developers/docs/topics/gateway#channel-delete
ChannelDeleteEvent = Channel


# https://discord.com/developers/docs/topics/gateway#channel-pins-update
class ChannelPinsUpdateEvent(TypedDict):
    guild_id: NotRequired[Snowflake]
    channel_id: Snowflake
    last_pin_timestamp: NotRequired[Optional[str]]


# https://discord.com/developers/docs/topics/gateway#thread-create
class ThreadCreateEvent(Thread):
    newly_created: NotRequired[bool]


# https://discord.com/developers/docs/topics/gateway#thread-update
ThreadUpdateEvent = Thread


# https://discord.com/developers/docs/topics/gateway#thread-delete
class ThreadDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    parent_id: Snowflake
    type: ThreadType


# https://discord.com/developers/docs/topics/gateway#thread-list-sync
class ThreadListSyncEvent(TypedDict):
    guild_id: Snowflake
    channel_ids: NotRequired[List[Snowflake]]
    threads: List[Thread]
    members: List[ThreadMember]


# https://discord.com/developers/docs/topics/gateway#thread-member-update
class ThreadMemberUpdateEvent(ThreadMember):
    guild_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#thread-members-update
class ThreadMembersUpdateEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    member_count: int
    added_members: NotRequired[List[ThreadMemberWithPresence]]
    removed_member_ids: NotRequired[List[Snowflake]]


# https://discord.com/developers/docs/topics/gateway#guild-member-add
class GuildMemberAddEvent(MemberWithUser):
    guild_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#guild-member-remove
class GuildMemberRemoveEvent(TypedDict):
    guild_id: Snowflake
    user: User


# https://discord.com/developers/docs/topics/gateway#guild-member-update
class GuildMemberUpdateEvent(TypedDict):
    guild_id: Snowflake
    roles: List[Snowflake]
    user: User
    nick: NotRequired[Optional[str]]
    avatar: Optional[str]
    joined_at: Optional[str]
    premium_since: NotRequired[Optional[str]]
    deaf: NotRequired[bool]
    mute: NotRequired[bool]
    pending: NotRequired[bool]
    communication_disabled_until: NotRequired[Optional[str]]


# https://discord.com/developers/docs/topics/gateway#guild-emojis-update
class GuildEmojisUpdateEvent(TypedDict):
    guild_id: Snowflake
    emojis: List[Emoji]


# https://discord.com/developers/docs/topics/gateway#guild-stickers-update
class GuildStickersUpdateEvent(TypedDict):
    guild_id: Snowflake
    stickers: List[GuildSticker]


# https://discord.com/developers/docs/topics/gateway#guild-create
GuildCreateEvent = Union[Guild, UnavailableGuild]


# https://discord.com/developers/docs/topics/gateway#guild-update
GuildUpdateEvent = Guild


# https://discord.com/developers/docs/topics/gateway#guild-delete
GuildDeleteEvent = UnavailableGuild


class _GuildBanEvent(TypedDict):
    guild_id: Snowflake
    user: User


# https://discord.com/developers/docs/topics/gateway#guild-ban-add
GuildBanAddEvent = _GuildBanEvent


# https://discord.com/developers/docs/topics/gateway#guild-ban-remove
GuildBanRemoveEvent = _GuildBanEvent


# https://discord.com/developers/docs/topics/gateway#guild-role-create
class GuildRoleCreateEvent(TypedDict):
    guild_id: Snowflake
    role: Role


# https://discord.com/developers/docs/topics/gateway#guild-role-delete
class GuildRoleDeleteEvent(TypedDict):
    guild_id: Snowflake
    role_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#guild-role-update
class GuildRoleUpdateEvent(TypedDict):
    guild_id: Snowflake
    role: Role


# https://discord.com/developers/docs/topics/gateway#guild-scheduled-event-create
GuildScheduledEventCreateEvent = GuildScheduledEvent


# https://discord.com/developers/docs/topics/gateway#guild-scheduled-event-update
GuildScheduledEventUpdateEvent = GuildScheduledEvent


# https://discord.com/developers/docs/topics/gateway#guild-scheduled-event-delete
GuildScheduledEventDeleteEvent = GuildScheduledEvent


class _GuildScheduledEventUserEvent(TypedDict):
    guild_scheduled_event_id: Snowflake
    user_id: Snowflake
    guild_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#guild-scheduled-event-user-add
GuildScheduledEventUserAddEvent = _GuildScheduledEventUserEvent


# https://discord.com/developers/docs/topics/gateway#guild-scheduled-event-user-remove
GuildScheduledEventUserRemoveEvent = _GuildScheduledEventUserEvent


# https://discord.com/developers/docs/topics/gateway#guild-members-chunk
class GuildMembersChunkEvent(TypedDict):
    guild_id: Snowflake
    members: List[MemberWithUser]
    chunk_index: int
    chunk_count: int
    not_found: NotRequired[List[Snowflake]]
    presences: NotRequired[List[PresenceData]]
    nonce: NotRequired[str]


# https://discord.com/developers/docs/topics/gateway#guild-integrations-update
class GuildIntegrationsUpdateEvent(TypedDict):
    guild_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#integration-create
class IntegrationCreateEvent(BaseIntegration):
    guild_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#integration-update
class IntegrationUpdateEvent(BaseIntegration):
    guild_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#integration-delete
class IntegrationDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    application_id: NotRequired[Snowflake]


# https://discord.com/developers/docs/topics/gateway#webhooks-update
class WebhooksUpdateEvent(TypedDict):
    guild_id: Snowflake
    channel_id: Snowflake


# https://discord.com/developers/docs/topics/gateway#stage-instance-create
StageInstanceCreateEvent = StageInstance


# https://discord.com/developers/docs/topics/gateway#stage-instance-update
StageInstanceUpdateEvent = StageInstance


# https://discord.com/developers/docs/topics/gateway#stage-instance-delete
StageInstanceDeleteEvent = StageInstance


# https://discord.com/developers/docs/topics/gateway#voice-state-update
# We assume that we'll only receive voice states for guilds
VoiceStateUpdateEvent = GuildVoiceState


# https://discord.com/developers/docs/topics/gateway#voice-server-update
class VoiceServerUpdateEvent(TypedDict):
    token: str
    guild_id: Snowflake
    endpoint: Optional[str]


# https://discord.com/developers/docs/topics/gateway#typing-start
class TypingStartEvent(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    user_id: Snowflake
    timestamp: int
    member: NotRequired[MemberWithUser]


# https://discord.com/developers/docs/topics/gateway#auto-moderation-rule-create
AutoModerationRuleCreateEvent = AutoModRule


# https://discord.com/developers/docs/topics/gateway#auto-moderation-rule-update
AutoModerationRuleUpdateEvent = AutoModRule


# https://discord.com/developers/docs/topics/gateway#auto-moderation-rule-delete
AutoModerationRuleDeleteEvent = AutoModRule


# https://discord.com/developers/docs/topics/gateway#auto-moderation-action-execution
class AutoModerationActionExecutionEvent(TypedDict):
    guild_id: Snowflake
    action: AutoModAction
    rule_id: Snowflake
    rule_trigger_type: AutoModTriggerType
    user_id: Snowflake
    channel_id: NotRequired[Optional[Snowflake]]
    message_id: NotRequired[Optional[Snowflake]]
    alert_system_message_id: NotRequired[Optional[Snowflake]]
    content: NotRequired[str]
    matched_content: NotRequired[Optional[str]]
    matched_keyword: NotRequired[Optional[str]]
