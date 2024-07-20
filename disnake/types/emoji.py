# SPDX-License-Identifier: MIT

from typing import List, Optional, TypedDict

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


class ApplicationEmojiList(TypedDict):
    items: List[Emoji]


class EditEmoji(TypedDict):
    name: str
    roles: Optional[SnowflakeList]
