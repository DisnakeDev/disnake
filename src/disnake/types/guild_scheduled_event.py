# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .member import Member
    from .snowflake import Snowflake
    from .user import User

GuildScheduledEventPrivacyLevel = Literal[2]
GuildScheduledEventStatus = Literal[1, 2, 3, 4]
GuildScheduledEventEntityType = Literal[1, 2, 3]


class GuildScheduledEventUser(TypedDict):
    guild_scheduled_event_id: Snowflake
    user: User
    member: NotRequired[Member]


class GuildScheduledEventEntityMetadata(TypedDict, total=False):
    location: str


class GuildScheduledEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake | None
    creator_id: NotRequired[Snowflake | None]
    name: str
    description: NotRequired[str | None]
    scheduled_start_time: str
    scheduled_end_time: str | None
    privacy_level: GuildScheduledEventPrivacyLevel
    status: GuildScheduledEventStatus
    entity_type: GuildScheduledEventEntityType
    entity_id: Snowflake | None
    entity_metadata: GuildScheduledEventEntityMetadata | None
    creator: NotRequired[User]
    user_count: NotRequired[int]
    image: NotRequired[str | None]
