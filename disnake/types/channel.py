# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict, Union

from typing_extensions import NotRequired

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


class _BaseGuildChannel(_BaseChannel):
    guild_id: Snowflake
    position: int
    permission_overwrites: List[PermissionOverwrite]
    # In theory, this will never be None and will always be present. In practice...
    name: NotRequired[Optional[str]]
    nsfw: bool
    parent_id: Optional[Snowflake]
    flags: NotRequired[int]


class PartialChannel(_BaseChannel):
    type: ChannelType


class GroupInviteRecipient(TypedDict):
    username: str


class InviteChannel(PartialChannel, total=False):
    name: Optional[str]
    recipients: List[GroupInviteRecipient]
    icon: Optional[str]


class _BaseTextChannel(_BaseGuildChannel, total=False):
    topic: Optional[str]
    last_message_id: Optional[Snowflake]
    last_pin_timestamp: Optional[str]
    rate_limit_per_user: int
    default_auto_archive_duration: ThreadArchiveDurationLiteral
    default_thread_rate_limit_per_user: NotRequired[int]


class TextChannel(_BaseTextChannel):
    type: Literal[0]


class NewsChannel(_BaseTextChannel):
    type: Literal[5]


VideoQualityMode = Literal[1, 2]


class _BaseVocalGuildChannel(_BaseGuildChannel):
    bitrate: int
    user_limit: int
    rtc_region: NotRequired[Optional[str]]


class VoiceChannel(_BaseVocalGuildChannel):
    type: Literal[2]
    last_message_id: NotRequired[Optional[Snowflake]]
    rate_limit_per_user: NotRequired[int]
    video_quality_mode: NotRequired[VideoQualityMode]


class CategoryChannel(_BaseGuildChannel):
    type: Literal[4]


class StageChannel(_BaseVocalGuildChannel):
    type: Literal[13]
    topic: NotRequired[Optional[str]]


class ThreadChannel(_BaseChannel):
    type: Literal[10, 11, 12]
    guild_id: Snowflake
    name: str
    nsfw: bool
    last_message_id: NotRequired[Optional[Snowflake]]
    rate_limit_per_user: NotRequired[int]
    owner_id: NotRequired[Snowflake]
    parent_id: Snowflake
    last_pin_timestamp: NotRequired[Optional[str]]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    thread_metadata: ThreadMetadata
    member: NotRequired[ThreadMember]
    total_message_sent: NotRequired[int]


class DefaultReaction(TypedDict):
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


ThreadSortOrder = Literal[0, 1]
ThreadLayout = Literal[0, 1, 2]


class ForumChannel(_BaseGuildChannel):
    type: Literal[15]
    topic: NotRequired[Optional[str]]
    last_message_id: NotRequired[Optional[Snowflake]]
    default_auto_archive_duration: NotRequired[ThreadArchiveDurationLiteral]
    available_tags: NotRequired[List[ForumTag]]
    default_reaction_emoji: NotRequired[Optional[DefaultReaction]]
    default_thread_rate_limit_per_user: NotRequired[int]
    default_sort_order: NotRequired[Optional[ThreadSortOrder]]
    default_forum_layout: NotRequired[ThreadLayout]


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


class CreateGuildChannel(TypedDict):
    name: str
    type: NotRequired[Optional[ChannelType]]
    topic: NotRequired[Optional[str]]
    bitrate: NotRequired[Optional[int]]
    user_limit: NotRequired[Optional[int]]
    rate_limit_per_user: NotRequired[Optional[int]]
    position: NotRequired[Optional[int]]
    permission_overwrites: NotRequired[List[PermissionOverwrite]]
    parent_id: NotRequired[Optional[Snowflake]]
    nsfw: NotRequired[Optional[bool]]
    rtc_region: NotRequired[Optional[str]]
    video_quality_mode: NotRequired[Optional[VideoQualityMode]]
    default_auto_archive_duration: NotRequired[Optional[ThreadArchiveDurationLiteral]]
