"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .activity import PresenceData
from .member import Member
from .message import Message
from .snowflake import Snowflake

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


class ThreadMetadata(TypedDict):
    archived: bool
    auto_archive_duration: ThreadArchiveDurationLiteral
    archive_timestamp: str
    locked: bool
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[Optional[str]]


class Thread(TypedDict):
    id: Snowflake
    type: ThreadType
    guild_id: Snowflake
    name: str
    last_message_id: NotRequired[Optional[Snowflake]]
    rate_limit_per_user: int
    owner_id: NotRequired[Snowflake]
    parent_id: Snowflake
    last_pin_timestamp: NotRequired[Optional[str]]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    thread_metadata: ThreadMetadata
    member: NotRequired[ThreadMember]
    flags: NotRequired[int]
    total_message_sent: NotRequired[int]


class ForumThread(Thread):
    message: Message


class ThreadPaginationPayload(TypedDict):
    threads: List[Thread]
    members: List[ThreadMember]
    has_more: bool
