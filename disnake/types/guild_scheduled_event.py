# SPDX-License-Identifier: MIT

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
