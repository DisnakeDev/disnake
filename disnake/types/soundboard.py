# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, TypedDict

from typing_extensions import NotRequired

from disnake.types.snowflake import Snowflake
from disnake.types.user import User


class PartialSoundboardSound(TypedDict):
    sound_id: Snowflake
    volume: float


class SoundboardSound(PartialSoundboardSound):
    name: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    available: bool


class GuildSoundboardSound(SoundboardSound):
    guild_id: NotRequired[Snowflake]
    user: NotRequired[User]  # only available via REST, given appropriate permissions


class ListGuildSoundboardSounds(TypedDict):
    items: list[GuildSoundboardSound]
