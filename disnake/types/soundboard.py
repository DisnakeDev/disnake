# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .user import User


class PartialSoundboardSound(TypedDict):
    sound_id: Snowflake
    volume: float


class SoundboardSound(PartialSoundboardSound):
    name: str
    emoji_id: Snowflake | None
    emoji_name: str | None
    available: bool


class GuildSoundboardSound(SoundboardSound):
    guild_id: NotRequired[Snowflake]
    user: NotRequired[User]  # only available via REST, given appropriate permissions


class ListGuildSoundboardSounds(TypedDict):
    items: list[GuildSoundboardSound]
