# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .asset import Asset, AssetMixin
from .mixins import Hashable
from .partial_emoji import PartialEmoji
from .utils import MISSING, _get_as_snowflake, snowflake_time

if TYPE_CHECKING:
    from .emoji import Emoji
    from .guild import Guild
    from .state import ConnectionState
    from .types.soundboard import (
        PartialSoundboardSound as PartialSoundboardSoundPayload,
        SoundboardSound as SoundboardSoundPayload,
    )
    from .user import User


__all__ = (
    "PartialSoundboardSound",
    "SoundboardSound",
)


class PartialSoundboardSound(Hashable, AssetMixin):
    """Represents a partial soundboard sound.

    Used for sounds in :class:`VoiceChannelEffect`\\s,
    and as the base for full :class:`SoundboardSound` objects.

    .. versionadded:: 2.10

    .. container:: operations

        .. describe:: x == y

            Checks if two soundboard sounds are equal.

        .. describe:: x != y

            Checks if two soundboard sounds are not equal.

        .. describe:: hash(x)

            Returns the soundboard sounds' hash.

    Attributes
    ----------
    id: :class:`int`
        The sound's ID.
    volume: :class:`float`
        The sound's volume (from ``0.0`` to ``1.0``).
    override_path: Optional[:class:`str`]
        The sound's filename, if applicable.
    """

    __slots__ = (
        "id",
        "volume",
        "override_path",
    )

    def __init__(
        self,
        *,
        data: PartialSoundboardSoundPayload,
        state: Optional[ConnectionState] = None,
    ) -> None:
        self._state = state
        self.id: int = int(data["sound_id"])
        self.override_path: Optional[str] = data.get("override_path")

        self._update(data)

    def _update(self, data: PartialSoundboardSoundPayload) -> None:
        self.volume: float = data["volume"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} override_path={self.override_path!r}>"

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        """Optional[:class:`datetime.datetime`]: Returns the sound's creation time in UTC.
        Can be ``None`` if this is a default sound.
        """
        if self.override_path:
            return None  # default sound
        return snowflake_time(self.id)

    @property
    def url(self) -> str:
        """:class:`str`: The url for the sound file."""
        if self.override_path:
            return f"{Asset.BASE}/soundboard-default-sounds/{self.override_path}"
        return f"{Asset.BASE}/soundboard-sounds/{self.id}"

    def is_default(self) -> bool:
        """Whether the sound is a default sound provided by Discord.

        :return type: :class:`bool`
        """
        return self.override_path is not None


class SoundboardSound(PartialSoundboardSound):
    """Represents a soundboard sound.

    .. versionadded:: 2.10

    .. container:: operations

        .. describe:: x == y

            Checks if two soundboard sounds are equal.

        .. describe:: x != y

            Checks if two soundboard sounds are not equal.

        .. describe:: hash(x)

            Returns the soundboard sounds' hash.

    Attributes
    ----------
    id: :class:`int`
        The sound's ID.
    volume: :class:`float`
        The sound's volume (from ``0.0`` to ``1.0``).
    override_path: Optional[:class:`str`]
        The sound's filename, if applicable.
    name: :class:`str`
        The sound's name.
    emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`]]
        The sound's emoji, if any.
        Due to a Discord limitation, this will have an empty
        :attr:`~PartialEmoji.name` if it is a custom :class:`PartialEmoji`.
    guild_id: Optional[:class:`int`]
        The ID of the guild this sound belongs to, if any.
    available: :class:`bool`
        Whether this sound is available for use.
    user: Optional[:class:`User`]
        The user that created this sound.
    """

    __slots__ = (
        "name",
        "emoji",
        "guild_id",
        "available",
        "user",
    )

    _state: ConnectionState

    def __init__(
        self,
        *,
        data: SoundboardSoundPayload,
        state: ConnectionState,
        # `guild_id` isn't sent over REST, so we manually keep track of it
        guild_id: Optional[int],
    ) -> None:
        super().__init__(data=data, state=state)

        self.guild_id: Optional[int] = guild_id or _get_as_snowflake(data, "guild_id")
        self.user: Optional[User] = (
            state.store_user(user_data) if (user_data := data.get("user")) is not None else None
        )

    def _update(self, data: SoundboardSoundPayload) -> None:
        super()._update(data)
        self.name: str = data["name"]
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
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild that this sound is from, if any."""
        return self._state._get_guild(self.guild_id)

    async def edit(
        self,
        *,
        name: str = MISSING,
        volume: float = MISSING,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = MISSING,
        reason: Optional[str] = None,
    ) -> SoundboardSound:
        """|coro|

        Edits a :class:`SoundboardSound` for the guild.

        You must have :attr:`~Permissions.manage_guild_expressions` permission to
        do this.

        All fields are optional.

        Parameters
        ----------
        name: :class:`str`
            The sounds's new name. Must be at least 2 characters.
        volume: :class:`float`
            The sound's new volume (from ``0.0`` to ``1.0``).
        emoji: Optional[Union[:class:`str`, :class:`Emoji`, :class:`PartialEmoji`]]
            The sound's new emoji. Can be ``None``.
        reason: Optional[:class:`str`]
            The reason for editing this sound. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You are not allowed to edit soundboard sounds.
        HTTPException
            An error occurred editing the soundboard sound.

        Returns
        -------
        :class:`SoundboardSound`
            The newly modified soundboard sound.
        """
        payload: Dict[str, Any] = {}

        # FIXME: workaround for API issue, which clears volume + emoji if not provided
        if volume is MISSING:
            volume = self.volume
        if emoji is MISSING:
            emoji = self.emoji

        if name is not MISSING:
            payload["name"] = name
        if volume is not MISSING:
            payload["volume"] = volume
        if emoji is not MISSING:
            emoji_name, emoji_id = PartialEmoji._emoji_to_name_id(emoji)
            payload["emoji_name"] = emoji_name
            payload["emoji_id"] = emoji_id

        if not self.guild_id:
            raise RuntimeError  # default sound  # TODO: improve this, split into two classes or raise proper error here
        data = await self._state.http.edit_guild_soundboard_sound(
            self.guild_id, self.id, reason=reason, **payload
        )
        return SoundboardSound(data=data, state=self._state, guild_id=self.guild_id)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        """|coro|

        Deletes the :class:`SoundboardSound` from the guild.

        You must have :attr:`~Permissions.manage_guild_expressions` permission to
        do this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this sound. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You are not allowed to delete soundboard sounds.
        HTTPException
            An error occurred deleting the soundboard sound.
        """
        if not self.guild_id:
            raise RuntimeError  # default sound  # TODO: see above
        await self._state.http.delete_guild_soundboard_sound(self.guild_id, self.id, reason=reason)
