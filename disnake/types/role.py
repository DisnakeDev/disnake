# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, TypedDict

from .snowflake import Snowflake


class _RoleOptional(TypedDict, total=False):
    tags: RoleTags


class Role(_RoleOptional):
    id: Snowflake
    name: str
    color: int
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool


class RoleTags(TypedDict, total=False):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: None
