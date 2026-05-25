# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, TypedDict

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
    presence: PresenceData | None


class ThreadMetadata(TypedDict):
    archived: bool
    auto_archive_duration: ThreadArchiveDurationLiteral
    archive_timestamp: str
    locked: bool
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[str | None]


class Thread(TypedDict):
    id: Snowflake
    type: ThreadType
    guild_id: Snowflake
    name: str
    last_message_id: NotRequired[Snowflake | None]
    rate_limit_per_user: int
    owner_id: NotRequired[Snowflake]
    parent_id: Snowflake
    last_pin_timestamp: NotRequired[str | None]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    thread_metadata: ThreadMetadata
    member: NotRequired[ThreadMember]
    flags: NotRequired[int]
    total_message_sent: NotRequired[int]
    applied_tags: NotRequired[SnowflakeList]


class ForumThread(Thread):
    message: Message


class ThreadPaginationPayload(TypedDict):
    threads: list[Thread]
    members: list[ThreadMember]
    has_more: bool


class PartialForumTag(TypedDict):
    id: NotRequired[Snowflake]
    name: str
    emoji_id: Snowflake | None
    emoji_name: str | None
    moderated: bool


class ForumTag(PartialForumTag):
    id: Snowflake
