# SPDX-License-Identifier: MIT

from typing import Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake, SnowflakeList
from .user import User


class PartialEmoji(TypedDict):
    id: Optional[Snowflake]
    name: Optional[str]
    animated: NotRequired[bool]


class Emoji(PartialEmoji, total=False):
    roles: SnowflakeList
    user: User
    require_colons: bool
    managed: bool
    available: bool


class EditEmoji(TypedDict):
    name: str
    roles: Optional[SnowflakeList]
