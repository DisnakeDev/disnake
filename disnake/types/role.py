# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, TypedDict

from typing_extensions import NotRequired

from disnake.types.snowflake import Snowflake


class Role(TypedDict):
    id: Snowflake
    name: str
    color: int
    colors: RoleColors
    hoist: bool
    icon: NotRequired[Optional[str]]
    unicode_emoji: NotRequired[Optional[str]]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: NotRequired[RoleTags]
    flags: int


class RoleTags(TypedDict, total=False):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: None
    guild_connections: None
    subscription_listing_id: Snowflake
    available_for_purchase: None


class RoleColors(TypedDict):
    primary_color: int
    secondary_color: Optional[int]
    tertiary_color: Optional[int]


class CreateRole(TypedDict, total=False):
    name: str
    permissions: str
    colors: RoleColors
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    mentionable: bool
