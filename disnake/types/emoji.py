# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from .snowflake import Snowflake, SnowflakeList
    from .user import User


class PartialEmoji(TypedDict):
    id: Optional[Snowflake]
    name: Optional[str]


class Emoji(PartialEmoji, total=False):
    roles: SnowflakeList
    user: User
    require_colons: bool
    managed: bool
    animated: bool
    available: bool


class EditEmoji(TypedDict):
    name: str
    roles: Optional[SnowflakeList]


class ListAppEmoji(TypedDict):
    items: list[Emoji]
