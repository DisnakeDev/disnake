# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional, Union

from .asset import Asset, AssetMixin
from .mixins import Hashable
from .utils import _get_as_snowflake, snowflake_time

if TYPE_CHECKING:
    from .emoji import Emoji
    from .guild import Guild
    from .partial_emoji import PartialEmoji
    from .state import ConnectionState
    from .types.soundboard import SoundboardSound as SoundboardSoundPayload
    from .user import User


__all__ = ("SoundboardSound",)


class SoundboardSound(Hashable, AssetMixin):
    """TODO"""

    __slots__ = (
        "name",
        "id",
        "volume",
        "emoji",
        "override_path",
        "guild_id",
        "available",
        "user",
    )

    def __init__(self, *, data: SoundboardSoundPayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["sound_id"])
        self.override_path: Optional[str] = data.get("override_path")
        self.guild_id: Optional[int] = _get_as_snowflake(data, "guild_id")
        self.user: Optional[User] = (
            state.store_user(user_data) if (user_data := data.get("user")) is not None else None
        )

        self._update(data)

    def _update(self, data: SoundboardSoundPayload) -> None:
        self.name: str = data["name"]
        self.volume: float = data["volume"]
        self.emoji: Optional[Union[Emoji, PartialEmoji]] = self._state._get_emoji_from_fields(
            name=data.get("emoji_name"),
            id=_get_as_snowflake(data, "emoji_id"),
        )
        self.available: bool = data.get("available", True)

    def __repr__(self) -> str:
        return (
            f"<SoundboardSound id={self.id!r} name={self.name!r} guild_id={self.guild_id!r}"
            f" user={self.user!r}>"
        )

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the role's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild that this sound is from.
        Could be ``None`` if the bot is not in the guild.
        """
        return self._state._get_guild(self.guild_id)

    @property
    def url(self) -> str:
        """:class:`str`: The url for the sound."""
        if self.override_path:
            return f"{Asset.BASE}/soundboard-default-sounds/{self.override_path}"
        return f"{Asset.BASE}/soundboard-sounds/{self.id}"
