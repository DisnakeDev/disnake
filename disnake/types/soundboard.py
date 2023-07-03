# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .user import User


class PartialSoundboardSound(TypedDict):
    sound_id: Snowflake
    volume: float
    override_path: Optional[str]


class SoundboardSound(PartialSoundboardSound):
    name: str
    id: NotRequired[Snowflake]  # this seems to always equal `sound_id`
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    user_id: Snowflake


class GuildSoundboardSound(SoundboardSound):
    guild_id: NotRequired[Snowflake]
    available: NotRequired[bool]
    user: NotRequired[User]
