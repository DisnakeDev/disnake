# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from .asset import Asset
from .emoji import Emoji
from .sticker import GuildSticker

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.guild import GuildPreview as GuildPreviewPayload

__all__ = ("GuildPreview",)


class GuildPreview:
    """Represents a :class:`.Guild` preview object.

    .. versionadded:: 2.5

    Attributes
    ----------
    name: :class:`str`
        The guild's name.
    emojis: Tuple[:class:`Emoji`, ...]
        All emojis that the guild owns.
    stickers: Tuple[:class:`GuildSticker`, ...]
        All stickers that the guild owns.
    id: :class:`int`
        The ID of the guild this preview represents.
    description: Optional[:class:`str`]
        The guild's description.
    features: List[:class:`str`]
        A list of features that the guild has. The features that a guild can have are
        subject to arbitrary change by Discord.

        See :attr:`Guild.features` for a list of features.
    approximate_member_count: :class:`int`
        The approximate number of members in the guild.
    approximate_presence_count: :class:`int`
        The approximate number of members currently active in the guild.
        This includes idle, dnd, online, and invisible members. Offline members are excluded.
    """

    __slots__ = (
        "id",
        "name",
        "description",
        "features",
        "approximate_member_count",
        "approximate_presence_count",
        "stickers",
        "emojis",
        "_discovery_splash",
        "_icon",
        "_splash",
        "_state",
    )

    def __init__(self, *, data: GuildPreviewPayload, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.approximate_member_count: int = data["approximate_member_count"]
        self.approximate_presence_count: int = data["approximate_presence_count"]
        self.description: Optional[str] = data.get("description")
        self.features = data["features"]

        self._icon: Optional[str] = data.get("icon")
        self._splash: Optional[str] = data.get("splash")
        self._discovery_splash: Optional[str] = data.get("discovery_splash")

        emojis = data.get("emojis")
        if emojis:
            self.emojis: Tuple[Emoji, ...] = tuple(
                Emoji(guild=self, state=self._state, data=emoji) for emoji in emojis
            )
        else:
            self.emojis: Tuple[Emoji, ...] = ()

        stickers = data.get("stickers")
        if stickers:
            self.stickers: Tuple[GuildSticker, ...] = tuple(
                GuildSticker(state=self._state, data=sticker) for sticker in stickers
            )
        else:
            self.stickers: Tuple[GuildSticker, ...] = ()

    def __repr__(self) -> str:
        return f"<GuildPreview id={self.id!r} name={self.name!r}>"

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild preview's icon asset, if available."""
        if self._icon is None:
            return None
        return Asset._from_guild_icon(self._state, self.id, self._icon)

    @property
    def splash(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild preview's invite splash asset, if available."""
        if self._splash is None:
            return None
        return Asset._from_guild_image(self._state, self.id, self._splash, path="splashes")

    @property
    def discovery_splash(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild preview's discovery splash asset, if available."""
        if self._discovery_splash is None:
            return None
        return Asset._from_guild_image(
            self._state, self.id, self._discovery_splash, path="discovery-splashes"
        )
