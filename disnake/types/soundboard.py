# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .user import User


class SoundboardSound(TypedDict):
    name: str
    sound_id: Snowflake
    id: NotRequired[Snowflake]  # this seems to always equal `sound_id`
    volume: float
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    override_path: Optional[str]
    guild_id: NotRequired[Snowflake]
    user_id: Snowflake
    available: NotRequired[bool]
    user: NotRequired[User]
