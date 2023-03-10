# SPDX-License-Identifier: MIT

from typing import Optional, TypedDict

from disnake.types.snowflake import Snowflake, SnowflakeList
from disnake.types.user import User


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
