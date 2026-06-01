# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake


class RoleBase(TypedDict):
    id: Snowflake
    name: str
    position: int
    color: int
    colors: RoleColors
    icon: NotRequired[str | None]
    unicode_emoji: NotRequired[str | None]


class Role(RoleBase):
    hoist: bool
    permissions: str
    managed: bool
    mentionable: bool
    tags: NotRequired[RoleTags]
    flags: int


class PartialRole(RoleBase): ...


class RoleTags(TypedDict, total=False):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: None
    guild_connections: None
    subscription_listing_id: Snowflake
    available_for_purchase: None


class RoleColors(TypedDict):
    primary_color: int
    secondary_color: int | None
    tertiary_color: int | None


class CreateRole(TypedDict, total=False):
    name: str
    permissions: str
    colors: RoleColors
    hoist: bool
    icon: str | None
    unicode_emoji: str | None
    mentionable: bool
