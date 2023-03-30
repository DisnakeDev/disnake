# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict, Union

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .threads import ForumTag, ThreadArchiveDurationLiteral, ThreadMember, ThreadMetadata
from .user import PartialUser

OverwriteType = Literal[0, 1]


class PermissionOverwritePayload(TypedDict):
    id: Snowflake
    type: OverwriteType
    allow: str
    deny: str


LiteralChannelType = Literal[0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15]


class _BaseChannelPayload(TypedDict):
    id: Snowflake


class _BaseGuildChannelPayload(_BaseChannelPayload):
    guild_id: Snowflake
    position: int
    permission_overwrites: List[PermissionOverwritePayload]
    # In theory, this will never be None and will always be present. In practice...
    name: NotRequired[Optional[str]]
    nsfw: bool
    parent_id: Optional[Snowflake]
    flags: NotRequired[int]


class PartialChannelPayload(_BaseChannelPayload):
    type: LiteralChannelType


class GroupInviteRecipient(TypedDict):
    username: str


class InviteChannel(PartialChannelPayload, total=False):
    name: Optional[str]
    recipients: List[GroupInviteRecipient]
    icon: Optional[str]


class _BaseTextChannelPayload(_BaseGuildChannelPayload, total=False):
    topic: Optional[str]
    last_message_id: Optional[Snowflake]
    last_pin_timestamp: Optional[str]
    rate_limit_per_user: int
    default_auto_archive_duration: ThreadArchiveDurationLiteral
    default_thread_rate_limit_per_user: NotRequired[int]


class TextChannelPayload(_BaseTextChannelPayload):
    type: Literal[0]


class NewsChannelPayload(_BaseTextChannelPayload):
    type: Literal[5]


VideoQualityMode = Literal[1, 2]


class _BaseVocalGuildChannelPayload(_BaseGuildChannelPayload):
    bitrate: int
    user_limit: int
    rtc_region: NotRequired[Optional[str]]


class VoiceChannelPayload(_BaseVocalGuildChannelPayload):
    type: Literal[2]
    last_message_id: NotRequired[Optional[Snowflake]]
    rate_limit_per_user: NotRequired[int]
    video_quality_mode: NotRequired[VideoQualityMode]


class CategoryChannelPayload(_BaseGuildChannelPayload):
    type: Literal[4]


class StageChannelPayload(_BaseVocalGuildChannelPayload):
    type: Literal[13]
    topic: NotRequired[Optional[str]]


class ThreadChannelPayload(_BaseChannelPayload):
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


class DefaultReactionPayload(TypedDict):
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


ThreadSortOrder = Literal[0, 1]
ThreadLayout = Literal[0, 1, 2]


class ForumChannelPayload(_BaseGuildChannelPayload):
    type: Literal[15]
    topic: NotRequired[Optional[str]]
    last_message_id: NotRequired[Optional[Snowflake]]
    default_auto_archive_duration: NotRequired[ThreadArchiveDurationLiteral]
    available_tags: NotRequired[List[ForumTag]]
    default_reaction_emoji: NotRequired[Optional[DefaultReactionPayload]]
    default_thread_rate_limit_per_user: NotRequired[int]
    default_sort_order: NotRequired[Optional[ThreadSortOrder]]
    default_forum_layout: NotRequired[ThreadLayout]


GuildChannelPayload = Union[
    TextChannelPayload,
    NewsChannelPayload,
    VoiceChannelPayload,
    CategoryChannelPayload,
    StageChannelPayload,
    ThreadChannelPayload,
    ForumChannelPayload,
]


class DMChannelPayload(_BaseChannelPayload):
    type: Literal[1]
    last_message_id: Optional[Snowflake]
    recipients: List[PartialUser]


class GroupDMChannelPayload(_BaseChannelPayload):
    name: Optional[str]
    type: Literal[3]
    icon: Optional[str]
    owner_id: Snowflake


ChannelPayload = Union[GuildChannelPayload, DMChannelPayload, GroupDMChannelPayload]

PrivacyLevel = Literal[1, 2]


class StageInstancePayload(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    privacy_level: PrivacyLevel
    discoverable_disabled: bool
    guild_scheduled_event_id: Optional[Snowflake]


class GuildDirectoryPayload(_BaseChannelPayload):
    type: Literal[14]
    name: str


class CreateGuildChannel(TypedDict):
    name: str
    type: NotRequired[Optional[LiteralChannelType]]
    topic: NotRequired[Optional[str]]
    bitrate: NotRequired[Optional[int]]
    user_limit: NotRequired[Optional[int]]
    rate_limit_per_user: NotRequired[Optional[int]]
    position: NotRequired[Optional[int]]
    permission_overwrites: NotRequired[List[PermissionOverwritePayload]]
    parent_id: NotRequired[Optional[Snowflake]]
    nsfw: NotRequired[Optional[bool]]
    rtc_region: NotRequired[Optional[str]]
    video_quality_mode: NotRequired[Optional[VideoQualityMode]]
    default_auto_archive_duration: NotRequired[Optional[ThreadArchiveDurationLiteral]]
