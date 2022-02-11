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

from typing import TYPE_CHECKING, List, Optional

from .partial_emoji import PartialEmoji
from .utils import MISSING, _get_as_snowflake

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState
    from .types.welcome_screen import (
        WelcomeScreen as WelcomeScreenPayload,
        WelcomeScreenChannel as WelcomeScreenChannelPayload,
    )
__all__ = ("WelcomeScreen", "WelcomeScreenChannel")


class WelcomeScreenChannel:
    """Represents a Discord welcome screen channel.

    Attributes
    ----------
    id: :class:`int`
        The ID of the guild channel this welcome screen channel represents.
    description: :class:`str`
        The description of this channel in the official UI.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji associated with this channel's welcome message, if any.
    """

    def __init__(self, *, id: int, description: str, emoji: Optional[PartialEmoji] = None):
        self.id = id
        self.description = description
        self.emoji = emoji

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

    def to_dict(self):

        result = {
            "channel_id": self.id,
            "description": self.description,
        }
        if self.emoji is not None:
            result["emoji_id"] = self.emoji.id
            result["emoji_name"] = self.emoji.name

        return result


class WelcomeScreen:
    """Represents a Discord welcome screen for a :class:`Guild`.

    Attributes
    ----------
    description: :class:`str`
        The welcome screen description.
    channels: List[:class:`WelcomeScreenChannel`]
        The welcome screen's channels.
    enabled: class:`bool`:
        Whether the welcome screen is displayed to users.
        This is equivalent to checking if ``WELCOME_SCREEN_ENABLED`` is present in :attr:`Guild.features`.
    """

    def __init__(self, *, data: WelcomeScreenPayload, state: ConnectionState, guild: Guild):
        self._state = state
        self._guild = guild
        self.description = data["description"]
        self.channels = [
            WelcomeScreenChannel._from_data(data=channel, state=state)
            for channel in data["welcome_channels"]
        ]

    def __repr__(self) -> str:
        return f"<WelcomeScreen description={self.description!r} channels={self.channels!r} enabled={self.enabled!r}>"

    @property
    def enabled(self) -> bool:
        return "WELCOME_SCREEN_ENABLED" in self._guild.features

    async def edit(
        self,
        *,
        enabled: bool = MISSING,
        description: str = MISSING,
        welcome_channels: List[WelcomeScreenChannel] = MISSING,
        reason: str = None,
    ):
        """Edits the welcome screen.

        You must have the :attr:`~Permissions.manage_guild` permission to
        use this.

        All fields are optional.

        Parameters
        -----------
        enabled: :class:`bool`
            Whether the welcome screen is enabled.
        description: :class:`str`
            The new guild description.
        welcome_channels: List[:class:`WelcomeScreenChannel`]
            The new welcome channels.
        reason: Optional[:class:`str`]
            The reason for editing the welcome screen. Shows up on the audit log.

        Raises
        -------
        Forbidden
            You do not have permissions to change the welcome screen.
        HTTPException
            Editing the welcome screen failed.

        Returns
        --------
        :class:`WelcomeScreen`
            The newly edited welcome screen.
        """
        payload = {}

        if enabled is not MISSING:
            payload["enabled"] = enabled

        if description is not MISSING:
            payload["description"] = description

        if welcome_channels is not MISSING:
            payload["welcome_channels"] = [channel.to_dict() for channel in welcome_channels]

        data = await self._state.http.edit_guild_welcome_screen(
            self._guild.id, reason=reason, **payload
        )
        return WelcomeScreen(data=data, state=self._state, guild=self._guild)
