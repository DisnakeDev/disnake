# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, TypedDict

from .guild import Guild
from .snowflake import Snowflake
from .user import User


class CreateTemplate(TypedDict):
    name: str
    description: Optional[str]


class Template(TypedDict):
    code: str
    name: str
    description: Optional[str]
    usage_count: int
    creator_id: Snowflake
    creator: User
    created_at: str
    updated_at: str
    source_guild_id: Snowflake
    serialized_source_guild: Guild
    is_dirty: Optional[bool]
