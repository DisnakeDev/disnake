# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from . import utils
from .partial_emoji import PartialEmoji, _EmojiTag

if TYPE_CHECKING:
    from .emoji import Emoji
    from .guild import Guild
    from .invite import PartialInviteGuild
    from .state import ConnectionState
    from .types.welcome_screen import (
        WelcomeScreen as WelcomeScreenPayload,
        WelcomeScreenChannel as WelcomeScreenChannelPayload,
    )

__all__ = (
    "WelcomeScreen",
    "WelcomeScreenChannel",
)

MISSING = utils.MISSING


class WelcomeScreenChannel:
    """Represents a Discord welcome screen channel.

    .. versionadded:: 2.5

    Attributes
    ----------
    id: :class:`int`
        The ID of the guild channel this welcome screen channel represents.
    description: :class:`str`
        The description of this channel in the official UI.
    emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`]]
        The emoji associated with this channel's welcome message, if any.
    """

    __slots__ = (
        "id",
        "description",
        "emoji",
    )

    def __init__(
        self,
        *,
        id: int,
        description: str,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
    ) -> None:
        self.id: int = id
        self.description: str = description
        self.emoji: Optional[Union[Emoji, PartialEmoji]] = None
        if emoji is None:
            self.emoji = None
        elif isinstance(emoji, str):
            self.emoji = PartialEmoji.from_str(emoji)
        elif isinstance(emoji, _EmojiTag):
            self.emoji = emoji
        else:
            raise TypeError("emoji must be None, a str, PartialEmoji, or Emoji instance.")

    def __repr__(self) -> str:
        return f"<WelcomeScreenChannel id={self.id!r} emoji={self.emoji!r} description={self.description!r}>"

    @classmethod
    def _from_data(
        cls,
        *,
        data: WelcomeScreenChannelPayload,
        state: ConnectionState,
    ) -> WelcomeScreenChannel:
        emoji = state._get_emoji_from_fields(
            name=data.get("emoji_name"),
            id=utils._get_as_snowflake(data, "emoji_id"),
        )

        return cls(id=int(data["channel_id"]), description=data["description"], emoji=emoji)

    def to_dict(self) -> WelcomeScreenChannelPayload:
        result: WelcomeScreenChannelPayload = {}  # type: ignore
        result["channel_id"] = self.id
        result["description"] = self.description

        if self.emoji is not None:
            if self.emoji.id:
                result["emoji_id"] = self.emoji.id
            result["emoji_name"] = self.emoji.name

        return result


class WelcomeScreen:
    """Represents a Discord welcome screen for a :class:`Guild`.

    .. versionadded:: 2.5

    Attributes
    ----------
    description: Optional[:class:`str`]
        The guild description in the welcome screen.
    channels: List[:class:`WelcomeScreenChannel`]
        The welcome screen's channels.
    """

    __slots__ = (
        "description",
        "channels",
        "_guild",
        "_state",
    )

    def __init__(
        self,
        *,
        data: WelcomeScreenPayload,
        state: ConnectionState,
        guild: Union[Guild, PartialInviteGuild],
    ) -> None:
        self._state = state
        self._guild = guild
        self.description: Optional[str] = data.get("description")
        self.channels: List[WelcomeScreenChannel] = [
            WelcomeScreenChannel._from_data(data=channel, state=state)
            for channel in data["welcome_channels"]
        ]

    def __repr__(self) -> str:
        return f"<WelcomeScreen description={self.description!r} channels={self.channels!r} enabled={self.enabled!r}>"

    @property
    def enabled(self) -> bool:
        """:class:`bool`: Whether the welcome screen is displayed to users.
        This is equivalent to checking if ``WELCOME_SCREEN_ENABLED`` is present in :attr:`Guild.features`.
        """
        return "WELCOME_SCREEN_ENABLED" in self._guild.features

    async def edit(
        self,
        *,
        enabled: bool = MISSING,
        description: Optional[str] = MISSING,
        channels: Optional[List[WelcomeScreenChannel]] = MISSING,
        reason: Optional[str] = None,
    ) -> WelcomeScreen:
        """|coro|

        Edits the welcome screen.

        You must have the :attr:`~Permissions.manage_guild` permission to
        use this.

        This requires 'COMMUNITY' in :attr:`.Guild.features`.

        Parameters
        ----------
        enabled: :class:`bool`
            Whether the welcome screen is enabled.
        description: Optional[:class:`str`]
            The new guild description in the welcome screen.
        channels: Optional[List[:class:`WelcomeScreenChannel`]]
            The new welcome channels.
        reason: Optional[:class:`str`]
            The reason for editing the welcome screen. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to change the welcome screen
            or the guild is not allowed to create welcome screens.
        HTTPException
            Editing the welcome screen failed.
        TypeError
            ``channels`` is not a list of :class:`~disnake.WelcomeScreenChannel` instances

        Returns
        -------
        :class:`WelcomeScreen`
            The newly edited welcome screen.
        """
        from .guild import Guild

        if not isinstance(self._guild, Guild):
            raise TypeError("May not edit a WelcomeScreen from a PartialInviteGuild.")

        return await self._guild.edit_welcome_screen(
            enabled=enabled,
            channels=channels,
            description=description,
            reason=reason,
        )
