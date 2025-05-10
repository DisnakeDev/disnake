# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .member import Member
from .snowflake import Snowflake
from .user import User

GuildScheduledEventPrivacyLevel = Literal[2]
GuildScheduledEventStatus = Literal[1, 2, 3, 4]
GuildScheduledEventEntityType = Literal[1, 2, 3]
GuildScheduledEventFrequency = Literal[0, 1, 2, 3]


class GuildScheduledEventUser(TypedDict):
    guild_scheduled_event_id: Snowflake
    user: User
    member: NotRequired[Member]


class GuildScheduledEventEntityMetadata(TypedDict, total=False):
    location: str


class GuildScheduledEventNWeekday(TypedDict):
    n: int
    day: int  # Matches Weekday enum int value (0-6)


class GuildScheduledEventRecurrenceRule(TypedDict, total=False):
    start: str  # ISO8601 string
    frequency: GuildScheduledEventFrequency  # YEARLY, MONTHLY, WEEKLY, DAILY
    interval: int

    by_weekday: List[int]  # List of Weekday int values (0-6)
    by_n_weekday: List[GuildScheduledEventNWeekday]
    by_month: List[int]  # 1-12
    by_month_day: List[int]  # 1-31


class GuildScheduledEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
    creator_id: NotRequired[Optional[Snowflake]]
    name: str
    description: NotRequired[Optional[str]]
    scheduled_start_time: str
    scheduled_end_time: Optional[str]
    privacy_level: GuildScheduledEventPrivacyLevel
    status: GuildScheduledEventStatus
    entity_type: GuildScheduledEventEntityType
    entity_id: Optional[Snowflake]
    entity_metadata: Optional[GuildScheduledEventEntityMetadata]
    creator: NotRequired[User]
    user_count: NotRequired[int]
    image: NotRequired[Optional[str]]
    recurrence_rule: Optional[GuildScheduledEventRecurrenceRule]
