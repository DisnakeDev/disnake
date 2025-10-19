# SPDX-License-Identifier: MIT

from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

from .message import MessagePin
from .snowflake import Snowflake
from .threads import ForumTag, ThreadArchiveDurationLiteral, ThreadMember, ThreadMetadata
from .user import PartialUser

OverwriteType = Literal[0, 1]


class PermissionOverwrite(TypedDict):
    id: Snowflake
    type: OverwriteType
    allow: str
    deny: str


ChannelType = Literal[0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16]


class _BaseChannel(TypedDict):
    id: Snowflake


class _BaseGuildChannel(_BaseChannel):
    guild_id: Snowflake
    position: int
    permission_overwrites: list[PermissionOverwrite]
    # In theory, this will never be None and will always be present. In practice...
    name: NotRequired[str | None]
    nsfw: bool
    parent_id: Snowflake | None
    flags: NotRequired[int]


class PartialChannel(_BaseChannel):
    type: ChannelType


class GroupInviteRecipient(TypedDict):
    username: str


class InviteChannel(PartialChannel, total=False):
    name: str | None
    recipients: list[GroupInviteRecipient]
    icon: str | None


class _BaseTextChannel(_BaseGuildChannel, total=False):
    topic: str | None
    last_message_id: Snowflake | None
    last_pin_timestamp: str | None
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
    rtc_region: NotRequired[str | None]


class VoiceChannel(_BaseVocalGuildChannel):
    type: Literal[2]
    last_message_id: NotRequired[Snowflake | None]
    rate_limit_per_user: NotRequired[int]
    video_quality_mode: NotRequired[VideoQualityMode]


class CategoryChannel(_BaseGuildChannel):
    type: Literal[4]


class StageChannel(_BaseVocalGuildChannel):
    type: Literal[13]
    topic: NotRequired[str | None]


class ThreadChannel(_BaseChannel):
    type: Literal[10, 11, 12]
    guild_id: Snowflake
    name: str
    nsfw: bool
    last_message_id: NotRequired[Snowflake | None]
    rate_limit_per_user: NotRequired[int]
    owner_id: NotRequired[Snowflake]
    parent_id: Snowflake
    last_pin_timestamp: NotRequired[str | None]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    thread_metadata: ThreadMetadata
    member: NotRequired[ThreadMember]
    total_message_sent: NotRequired[int]


class DefaultReaction(TypedDict):
    emoji_id: Snowflake | None
    emoji_name: str | None


ThreadSortOrder = Literal[0, 1]
ThreadLayout = Literal[0, 1, 2]


class _BaseThreadOnlyGuildChannel(_BaseGuildChannel):
    topic: NotRequired[str | None]
    last_message_id: NotRequired[Snowflake | None]
    default_auto_archive_duration: NotRequired[ThreadArchiveDurationLiteral]
    available_tags: NotRequired[list[ForumTag]]
    default_reaction_emoji: NotRequired[DefaultReaction | None]
    default_thread_rate_limit_per_user: NotRequired[int]
    default_sort_order: NotRequired[ThreadSortOrder | None]


class ForumChannel(_BaseThreadOnlyGuildChannel):
    type: Literal[15]
    default_forum_layout: NotRequired[ThreadLayout]


class MediaChannel(_BaseThreadOnlyGuildChannel):
    type: Literal[16]


GuildChannel = Union[
    TextChannel,
    NewsChannel,
    VoiceChannel,
    CategoryChannel,
    StageChannel,
    ThreadChannel,
    ForumChannel,
    MediaChannel,
]


class DMChannel(_BaseChannel):
    type: Literal[1]
    last_message_id: Snowflake | None
    recipients: list[PartialUser]


class GroupDMChannel(_BaseChannel):
    name: str | None
    type: Literal[3]
    icon: str | None
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
    guild_scheduled_event_id: Snowflake | None


class GuildDirectory(_BaseChannel):
    type: Literal[14]
    name: str


class CreateGuildChannel(TypedDict):
    name: str
    type: NotRequired[ChannelType | None]
    topic: NotRequired[str | None]
    bitrate: NotRequired[int | None]
    user_limit: NotRequired[int | None]
    rate_limit_per_user: NotRequired[int | None]
    position: NotRequired[int | None]
    permission_overwrites: NotRequired[list[PermissionOverwrite]]
    parent_id: NotRequired[Snowflake | None]
    nsfw: NotRequired[bool | None]
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[VideoQualityMode | None]
    default_auto_archive_duration: NotRequired[ThreadArchiveDurationLiteral | None]


class ChannelPins(TypedDict):
    items: list[MessagePin]
    has_more: bool
