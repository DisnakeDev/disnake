# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from .asset import Asset
from .emoji import Emoji
from .sticker import GuildSticker

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.guild import GuildPreview as GuildPreviewPayload

__all__ = ("GuildPreview",)


class GuildPreview:
    r"""Represents a :class:`.Guild` preview object.

    .. versionadded:: 2.5

    Attributes
    ----------
    name: :class:`str`
        The guild's name.
    emojis: :class:`tuple`\[:class:`Emoji`, ...]
        All emojis that the guild owns.
    stickers: :class:`tuple`\[:class:`GuildSticker`, ...]
        All stickers that the guild owns.
    id: :class:`int`
        The ID of the guild this preview represents.
    description: :class:`str` | :data:`None`
        The guild's description.
    features: :class:`list`\[:class:`str`]
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
        self.description: str | None = data.get("description")
        self.features = data["features"]

        self._icon: str | None = data.get("icon")
        self._splash: str | None = data.get("splash")
        self._discovery_splash: str | None = data.get("discovery_splash")

        emojis = data.get("emojis")
        if emojis:
            self.emojis: tuple[Emoji, ...] = tuple(
                Emoji(guild=self, state=self._state, data=emoji) for emoji in emojis
            )
        else:
            self.emojis: tuple[Emoji, ...] = ()

        stickers = data.get("stickers")
        if stickers:
            self.stickers: tuple[GuildSticker, ...] = tuple(
                GuildSticker(state=self._state, data=sticker) for sticker in stickers
            )
        else:
            self.stickers: tuple[GuildSticker, ...] = ()

    def __repr__(self) -> str:
        return f"<GuildPreview id={self.id!r} name={self.name!r}>"

    @property
    def icon(self) -> Asset | None:
        """:class:`Asset` | :data:`None`: Returns the guild preview's icon asset, if available."""
        if self._icon is None:
            return None
        return Asset._from_guild_icon(self._state, self.id, self._icon)

    @property
    def splash(self) -> Asset | None:
        """:class:`Asset` | :data:`None`: Returns the guild preview's invite splash asset, if available."""
        if self._splash is None:
            return None
        return Asset._from_guild_image(self._state, self.id, self._splash, path="splashes")

    @property
    def discovery_splash(self) -> Asset | None:
        """:class:`Asset` | :data:`None`: Returns the guild preview's discovery splash asset, if available."""
        if self._discovery_splash is None:
            return None
        return Asset._from_guild_image(
            self._state, self.id, self._discovery_splash, path="discovery-splashes"
        )
