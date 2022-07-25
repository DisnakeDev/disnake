"""
The MIT License (MIT)

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

from typing import Literal, Optional, TypedDict

from .member import Member
from .snowflake import Snowflake
from .user import User

GuildScheduledEventPrivacyLevel = Literal[2]
GuildScheduledEventStatus = Literal[1, 2, 3, 4]
GuildScheduledEventEntityType = Literal[1, 2, 3]


class _GuildScheduledEventUserOptional(TypedDict, total=False):
    member: Member


class GuildScheduledEventUser(_GuildScheduledEventUserOptional):
    guild_scheduled_event_id: Snowflake
    user: User


class GuildScheduledEventEntityMetadata(TypedDict, total=False):
    location: str


class _GuildScheduledEventOptional(TypedDict, total=False):
    description: Optional[str]
    creator: User
    user_count: int
    image: Optional[str]


class GuildScheduledEvent(_GuildScheduledEventOptional):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
    creator_id: Optional[Snowflake]
    name: str
    scheduled_start_time: str
    scheduled_end_time: Optional[str]
    privacy_level: GuildScheduledEventPrivacyLevel
    status: GuildScheduledEventStatus
    entity_type: GuildScheduledEventEntityType
    entity_id: Optional[Snowflake]
    entity_metadata: Optional[GuildScheduledEventEntityMetadata]
