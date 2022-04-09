"""
The MIT License (MIT)

Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from .partial_emoji import PartialEmoji, _EmojiTag
from .utils import MISSING, _get_as_snowflake

if TYPE_CHECKING:
    from .emoji import Emoji
    from .guild import Guild
    from .invite import PartialInviteGuild
    from .state import ConnectionState
    from .types.welcome_screen import (
        WelcomeScreen as WelcomeScreenPayload,
        WelcomeScreenChannel as WelcomeScreenChannelPayload,
    )
__all__ = ("WelcomeScreen", "WelcomeScreenChannel")


class WelcomeScreenChannel:
    """Represents a Discord welcome screen channel.

    .. versionadded:: 2.5

    Attributes
    ----------
    id: :class:`int`
        The ID of the guild channel this welcome screen channel represents.
    description: :class:`str`
        The description of this channel in the official UI.
    emoji: Optional[:class:`PartialEmoji`]
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
    ):
        self.id: int = id
        self.description: str = description
        self.emoji: Optional[PartialEmoji] = None
        if emoji is None:
            self.emoji = None
        elif isinstance(emoji, str):
            self.emoji = PartialEmoji.from_str(emoji)
        elif isinstance(emoji, PartialEmoji):
            self.emoji = emoji
        elif isinstance(emoji, _EmojiTag):
            self.emoji = emoji._to_partial()
        else:
            raise TypeError("emoji must be None, a str, PartialEmoji, or Emoji instance.")

    def __repr__(self):
        return f"<WelcomeScreenChannel id={self.id!r} emoji={self.emoji!r} description={self.description!r}>"

    @classmethod
    def _from_data(
        cls, *, data: WelcomeScreenChannelPayload, state: ConnectionState
    ) -> WelcomeScreenChannel:
        emoji_id = _get_as_snowflake(data, "emoji_id")
        emoji_name = data.get("emoji_name") or None
        emoji = None
        if emoji_name:
            emoji = PartialEmoji.with_state(state, name=emoji_name, id=emoji_id)

        return cls(id=int(data["channel_id"]), description=data["description"], emoji=emoji)

    def to_dict(self) -> WelcomeScreenChannelPayload:

        result = {
            "channel_id": self.id,
            "description": self.description,
        }
        if self.emoji is not None:
            if self.emoji.id:
                result["emoji_id"] = self.emoji.id
            result["emoji_name"] = self.emoji.name

        return result  # type: ignore


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
        "welcome_channels",
        "_guild",
        "_state",
    )

    def __init__(
        self,
        *,
        data: WelcomeScreenPayload,
        state: ConnectionState,
        guild: Union[Guild, PartialInviteGuild],
    ):
        self._state = state
        self._guild = guild
        self.description: Optional[str] = data.get("description")
        self.welcome_channels: List[WelcomeScreenChannel] = [
            WelcomeScreenChannel._from_data(data=channel, state=state)
            for channel in data["welcome_channels"]
        ]

    def __repr__(self) -> str:
        return f"<WelcomeScreen description={self.description!r} welcome_channels={self.welcome_channels!r} enabled={self.enabled!r}>"

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
        description: str = MISSING,
        welcome_channels: List[WelcomeScreenChannel] = MISSING,
        reason: Optional[str] = None,
    ) -> WelcomeScreen:
        """|coro|

        Edits the welcome screen.

        You must have the :attr:`~Permissions.manage_guild` permission to
        use this.

        All fields are optional and nullable.

        Parameters
        ----------
        enabled: :class:`bool`
            Whether the welcome screen is enabled.
        description: :class:`str`
            The new guild description in the welcome screen.
        welcome_channels: List[:class:`WelcomeScreenChannel`]
            The new welcome channels.
        reason: Optional[:class:`str`]
            The reason for editing the welcome screen. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to change the welcome screen.
        HTTPException
            Editing the welcome screen failed.

        Returns
        -------
        :class:`WelcomeScreen`
            The newly edited welcome screen.
        """
        payload = {}

        if enabled is not MISSING:
            payload["enabled"] = enabled

        if description is not MISSING:
            payload["description"] = description

        if welcome_channels is not MISSING:
            if welcome_channels is None:
                payload["welcome_channels"] = None
            elif isinstance(welcome_channels, list):
                welcome_channel_payload = []
                for channel in welcome_channels:
                    if not isinstance(channel, WelcomeScreenChannel):
                        raise TypeError(
                            "'welcome_channels' must be a list of 'WelcomeScreenChannel' objects"
                        )
                    welcome_channel_payload.append(channel.to_dict())
                payload["welcome_channels"] = welcome_channel_payload

        data = await self._state.http.edit_guild_welcome_screen(
            self._guild.id, reason=reason, **payload
        )
        return WelcomeScreen(state=self._state, data=data, guild=self._guild)
