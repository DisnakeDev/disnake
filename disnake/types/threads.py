# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .activity import PresenceData
from .member import Member
from .message import Message
from .snowflake import Snowflake, SnowflakeList

ThreadType = Literal[10, 11, 12]
ThreadArchiveDurationLiteral = Literal[60, 1440, 4320, 10080]


class ThreadMember(TypedDict):
    id: Snowflake
    user_id: Snowflake
    join_timestamp: str
    flags: int


class ThreadMemberWithPresence(ThreadMember):
    # currently unused, also not really documented properly
    member: Member
    presence: Optional[PresenceData]


class _ThreadMetadataOptional(TypedDict, total=False):
    locked: bool
    invitable: bool
    create_timestamp: str


class ThreadMetadata(_ThreadMetadataOptional):
    archived: bool
    auto_archive_duration: ThreadArchiveDurationLiteral
    archive_timestamp: str


class _ThreadOptional(TypedDict, total=False):
    member: ThreadMember
    owner_id: Snowflake
    last_message_id: Optional[Snowflake]
    last_pin_timestamp: Optional[str]
    flags: int
    applied_tags: SnowflakeList


class Thread(_ThreadOptional):
    id: Snowflake
    guild_id: Snowflake
    parent_id: Snowflake
    name: str
    type: ThreadType
    member_count: int
    message_count: int
    total_message_sent: int
    rate_limit_per_user: int
    thread_metadata: ThreadMetadata


class ForumThread(Thread):
    message: Message


class ThreadPaginationPayload(TypedDict):
    threads: List[Thread]
    members: List[ThreadMember]
    has_more: bool


class PartialForumTag(TypedDict):
    id: NotRequired[Snowflake]
    name: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    moderated: bool


class ForumTag(PartialForumTag):
    id: Snowflake
