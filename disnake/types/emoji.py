# SPDX-License-Identifier: MIT

from typing import TypedDict

from .snowflake import Snowflake, SnowflakeList
from .user import User


class PartialEmoji(TypedDict):
    id: Snowflake | None
    name: str | None


class Emoji(PartialEmoji, total=False):
    roles: SnowflakeList
    user: User
    require_colons: bool
    managed: bool
    animated: bool
    available: bool


class EditEmoji(TypedDict):
    name: str
    roles: SnowflakeList | None


class ListAppEmoji(TypedDict):
    items: list[Emoji]
