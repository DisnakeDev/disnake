# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict, Union

from .snowflake import Snowflake
from .threads import ForumTag, ThreadArchiveDurationLiteral, ThreadMember, ThreadMetadata
from .user import PartialUser

OverwriteType = Literal[0, 1]


class PermissionOverwrite(TypedDict):
    id: Snowflake
    type: OverwriteType
    allow: str
    deny: str


ChannelType = Literal[0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15]


class _BaseChannel(TypedDict):
    id: Snowflake


class _BaseGuildChannelOptional(TypedDict, total=False):
    flags: int
    # In theory, this will never be None and will always be present. In practice...
    name: Optional[str]


class _BaseGuildChannel(_BaseChannel, _BaseGuildChannelOptional):
    guild_id: Snowflake
    position: int
    permission_overwrites: List[PermissionOverwrite]
    nsfw: bool
    parent_id: Optional[Snowflake]


class PartialChannel(_BaseChannel):
    type: ChannelType


class GroupInviteRecipient(TypedDict):
    username: str


class InviteChannel(PartialChannel, total=False):
    name: Optional[str]
    recipients: List[GroupInviteRecipient]
    icon: Optional[str]


class _TextChannelOptional(TypedDict, total=False):
    topic: Optional[str]
    last_message_id: Optional[Snowflake]
    last_pin_timestamp: Optional[str]
    rate_limit_per_user: int
    default_auto_archive_duration: ThreadArchiveDurationLiteral


class TextChannel(_BaseGuildChannel, _TextChannelOptional):
    type: Literal[0]


class NewsChannel(_BaseGuildChannel, _TextChannelOptional):
    type: Literal[5]


VideoQualityMode = Literal[1, 2]


class _VoiceChannelOptional(TypedDict, total=False):
    rtc_region: Optional[str]
    video_quality_mode: VideoQualityMode
    last_message_id: Optional[Snowflake]
    rate_limit_per_user: int


class VoiceChannel(_BaseGuildChannel, _VoiceChannelOptional):
    type: Literal[2]
    bitrate: int
    user_limit: int


class CategoryChannel(_BaseGuildChannel):
    type: Literal[4]


class _StageChannelOptional(TypedDict, total=False):
    rtc_region: Optional[str]
    topic: Optional[str]


class StageChannel(_BaseGuildChannel, _StageChannelOptional):
    type: Literal[13]
    bitrate: int
    user_limit: int


class _ThreadChannelOptional(TypedDict, total=False):
    member: ThreadMember
    owner_id: Snowflake
    rate_limit_per_user: int
    last_message_id: Optional[Snowflake]
    last_pin_timestamp: str
    total_message_sent: Optional[int]
    message_count: Optional[int]


class ThreadChannel(_BaseChannel, _ThreadChannelOptional):
    type: Literal[10, 11, 12]
    name: str
    guild_id: Snowflake
    parent_id: Snowflake
    owner_id: Snowflake
    nsfw: bool
    last_message_id: Optional[Snowflake]
    rate_limit_per_user: int
    member_count: int
    thread_metadata: ThreadMetadata


class DefaultReaction(TypedDict):
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


class _ForumChannelOptional(TypedDict, total=False):
    topic: Optional[str]
    last_message_id: Optional[Snowflake]
    default_auto_archive_duration: ThreadArchiveDurationLiteral
    available_tags: List[ForumTag]
    default_reaction_emoji: Optional[DefaultReaction]
    default_thread_rate_limit_per_user: int


class ForumChannel(_BaseGuildChannel, _ForumChannelOptional):
    type: Literal[15]


GuildChannel = Union[
    TextChannel,
    NewsChannel,
    VoiceChannel,
    CategoryChannel,
    StageChannel,
    ThreadChannel,
    ForumChannel,
]


class DMChannel(_BaseChannel):
    type: Literal[1]
    last_message_id: Optional[Snowflake]
    recipients: List[PartialUser]


class GroupDMChannel(_BaseChannel):
    name: Optional[str]
    type: Literal[3]
    icon: Optional[str]
    owner_id: Snowflake


Channel = Union[GuildChannel, DMChannel, GroupDMChannel]

PrivacyLevel = Literal[1, 2]


class StageInstance(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    privacy_level: PrivacyLevel
    discoverable_disabled: bool
    guild_scheduled_event_id: Optional[Snowflake]


class GuildDirectory(_BaseChannel):
    type: Literal[14]
    name: str
