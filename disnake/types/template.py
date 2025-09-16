# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .guild import Guild
    from .snowflake import Snowflake
    from .user import User


class CreateTemplate(TypedDict):
    name: str
    description: str | None


class Template(TypedDict):
    code: str
    name: str
    description: str | None
    usage_count: int
    creator_id: Snowflake
    creator: User | None  # unsure when this can be null, but the spec says so
    created_at: str
    updated_at: str
    source_guild_id: Snowflake
    serialized_source_guild: Guild
    is_dirty: bool | None
