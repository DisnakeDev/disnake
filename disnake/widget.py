# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .activity import BaseActivity, Spotify, create_activity
from .asset import Asset
from .enums import Status, WidgetStyle, try_enum
from .invite import Invite
from .user import BaseUser
from .utils import MISSING, _get_as_snowflake, resolve_invite, snowflake_time

if TYPE_CHECKING:
    import datetime

    from .abc import GuildChannel, Snowflake
    from .guild import Guild
    from .state import ConnectionState
    from .types.widget import (
        Widget as WidgetPayload,
        WidgetMember as WidgetMemberPayload,
        WidgetSettings as WidgetSettingsPayload,
    )

__all__ = (
    "WidgetChannel",
    "WidgetMember",
    "WidgetSettings",
    "Widget",
)


class WidgetChannel:
    """Represents a "partial" widget channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two partial channels are the same.

        .. describe:: x != y

            Checks if two partial channels are not the same.

        .. describe:: hash(x)

            Return the partial channel's hash.

        .. describe:: str(x)

            Returns the partial channel's name.

    Attributes
    ----------
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position
    """

    __slots__ = ("id", "name", "position")

    def __init__(self, id: int, name: str, position: int) -> None:
        self.id: int = id
        self.name: str = name
        self.position: int = position

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<WidgetChannel id={self.id} name={self.name!r} position={self.position!r}>"

    @property
    def mention(self) -> str:
        """:class:`str`: The string that allows you to mention the channel."""
        return f"<#{self.id}>"

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the channel's creation time in UTC."""
        return snowflake_time(self.id)


class WidgetMember(BaseUser):
    """Represents a "partial" member of the widget's guild.

    .. container:: operations

        .. describe:: x == y

            Checks if two widget members are the same.

        .. describe:: x != y

            Checks if two widget members are not the same.

        .. describe:: hash(x)

            Return the widget member's hash.

        .. describe:: str(x)

            Returns the widget member's `name#discriminator`.

    Attributes
    ----------
    id: :class:`int`
        The member's anonymized ID.
    name: :class:`str`
        The member's nickname (if set in the guild) or username.
    discriminator: :class:`str`
        The member's anonymized discriminator.
    status: :class:`Status`
        The member's status.
    activity: Optional[Union[:class:`BaseActivity`, :class:`Spotify`]]
        The member's activity. This generally only has the ``name`` set.
    deafened: Optional[:class:`bool`]
        Whether the member is currently deafened.
    muted: Optional[:class:`bool`]
        Whether the member is currently muted.
    suppress: Optional[:class:`bool`]
        Whether the member is currently being suppressed.
    connected_channel: Optional[:class:`WidgetChannel`]
        Which channel the member is connected to.
    """

    __slots__ = (
        "status",
        "activity",
        "deafened",
        "suppress",
        "muted",
        "connected_channel",
        "_avatar_url",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        data: WidgetMemberPayload,
        connected_channel: Optional[WidgetChannel] = None,
    ) -> None:
        super().__init__(state=state, data=data)
        self.status: Status = try_enum(Status, data.get("status"))
        self.deafened: Optional[bool] = data.get("deaf", False) or data.get("self_deaf", False)
        self.muted: Optional[bool] = data.get("mute", False) or data.get("self_mute", False)
        self.suppress: Optional[bool] = data.get("suppress", False)
        self._avatar_url: Optional[str] = data.get("avatar_url")

        self.activity: Optional[Union[BaseActivity, Spotify]] = None
        if activity := (data.get("activity") or data.get("game")):
            self.activity = create_activity(activity, state=state)

        self.connected_channel: Optional[WidgetChannel] = connected_channel

    def __repr__(self) -> str:
        return f"<WidgetMember name={self.name!r} discriminator={self.discriminator!r}"

    # overwrite base type's @property since widget members always seem to have `avatar: null`,
    # and instead a separate `avatar_url` field with a full url
    @property
    def avatar(self) -> Optional[Asset]:
        """
        Optional[:class:`Asset`]: The user's avatar.
        The size can be chosen using :func:`Asset.with_size`, however the format is always
        static and cannot be changed through :func:`Asset.with_format` or similar methods.
        """
        if (url := self._avatar_url) is not None:
            return Asset(self._state, url=url, key=url, animated=False)
        return None

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the member's name."""
        return self.name


class WidgetSettings:
    """Represents a :class:`Guild`'s widget settings.

    .. versionadded:: 2.5

    Attributes
    ----------
    guild: :class:`Guild`
        The widget's guild.
    enabled: :class:`bool`
        Whether the widget is enabled.
    channel_id: Optional[:class:`int`]
        The widget channel ID. If set, an invite link for this channel will be generated,
        which allows users to join the guild from the widget.
    """

    __slots__ = ("_state", "guild", "enabled", "channel_id")

    def __init__(
        self, *, state: ConnectionState, guild: Guild, data: WidgetSettingsPayload
    ) -> None:
        self._state: ConnectionState = state
        self.guild: Guild = guild
        self.enabled: bool = data["enabled"]
        self.channel_id: Optional[int] = _get_as_snowflake(data, "channel_id")

    def __repr__(self) -> str:
        return f"<WidgetSettings enabled={self.enabled!r} channel_id={self.channel_id!r} guild={self.guild!r}>"

    @property
    def channel(self) -> Optional[GuildChannel]:
        """Optional[:class:`abc.GuildChannel`]: The widget channel, if set."""
        return self.guild.get_channel(self.channel_id) if self.channel_id is not None else None

    async def edit(
        self,
        *,
        enabled: bool = MISSING,
        channel: Optional[Snowflake] = MISSING,
        reason: Optional[str] = None,
    ) -> WidgetSettings:
        """|coro|

        Edits the widget.

        You must have :attr:`~Permissions.manage_guild` permission to
        do this.

        Parameters
        ----------
        enabled: :class:`bool`
            Whether to enable the widget.
        channel: Optional[:class:`~disnake.abc.Snowflake`]
            The new widget channel. Pass ``None`` to remove the widget channel.
            If set, an invite link for this channel will be generated,
            which allows users to join the guild from the widget.
        reason: Optional[:class:`str`]
            The reason for editing the widget. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permission to edit the widget.
        HTTPException
            Editing the widget failed.

        Returns
        -------
        :class:`WidgetSettings`
            The new widget settings.
        """

        return await self.guild.edit_widget(enabled=enabled, channel=channel, reason=reason)


class Widget:
    """Represents a :class:`Guild` widget.

    .. container:: operations

        .. describe:: x == y

            Checks if two widgets are the same.

        .. describe:: x != y

            Checks if two widgets are not the same.

        .. describe:: str(x)

            Returns the widget's JSON URL.

    Attributes
    ----------
    id: :class:`int`
        The guild's ID.
    name: :class:`str`
        The guild's name.
    channels: List[:class:`WidgetChannel`]
        The publicly accessible voice and stage channels in the guild.
    members: List[:class:`WidgetMember`]
        The online members in the server. Offline members
        do not appear in the widget.

        .. note::

            Due to a Discord limitation, if this data is available
            the users will be "anonymized" with linear IDs and discriminator
            information being incorrect. Likewise, the number of members
            retrieved is capped.

    presence_count: :class:`int`
        The number of online members in the server.

        .. versionadded:: 2.6
    """

    __slots__ = ("_state", "channels", "_invite", "id", "members", "name", "presence_count")

    def __init__(self, *, state: ConnectionState, data: WidgetPayload) -> None:
        self._state = state
        self._invite = data.get("instant_invite")
        self.name: str = data["name"]
        self.id: int = int(data["id"])
        self.presence_count: int = data["presence_count"]

        self.channels: List[WidgetChannel] = []
        for channel in data.get("channels", []):
            _id = int(channel["id"])
            self.channels.append(
                WidgetChannel(id=_id, name=channel["name"], position=channel["position"])
            )

        self.members: List[WidgetMember] = []
        channels = {channel.id: channel for channel in self.channels}
        for member in data.get("members", []):
            connected_channel = _get_as_snowflake(member, "channel_id")
            if connected_channel in channels:
                connected_channel = channels[connected_channel]
            elif connected_channel:
                connected_channel = WidgetChannel(id=connected_channel, name="", position=0)

            self.members.append(WidgetMember(state=self._state, data=member, connected_channel=connected_channel))  # type: ignore

    def __str__(self) -> str:
        return self.json_url

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Widget):
            return self.id == other.id
        return False

    def __repr__(self) -> str:
        return (
            f"<Widget id={self.id} name={self.name!r}"
            f" invite_url={self.invite_url!r} presence_count={self.presence_count!r}>"
        )

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the member's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def json_url(self) -> str:
        """:class:`str`: The JSON URL of the widget."""
        return f"https://discord.com/api/guilds/{self.id}/widget.json"

    @property
    def invite_url(self) -> Optional[str]:
        """Optional[:class:`str`]: The invite URL for the guild, if available."""
        return self._invite

    async def fetch_invite(self, *, with_counts: bool = True) -> Optional[Invite]:
        """|coro|

        Retrieves an :class:`Invite` from the widget's invite URL.
        This is the same as :meth:`Client.fetch_invite`; the invite
        code is abstracted away.

        .. versionchanged:: 2.6
            This may now return ``None`` if the widget does not have
            an attached invite URL.

        Parameters
        ----------
        with_counts: :class:`bool`
            Whether to include count information in the invite. This fills the
            :attr:`Invite.approximate_member_count` and :attr:`Invite.approximate_presence_count`
            fields.

        Returns
        -------
        Optional[:class:`Invite`]
            The invite from the widget's invite URL, if available.
        """
        if not self._invite:
            return None

        invite_id = resolve_invite(self._invite)
        data = await self._state.http.get_invite(invite_id, with_counts=with_counts)
        return Invite.from_incomplete(state=self._state, data=data)

    async def edit(
        self,
        *,
        enabled: bool = MISSING,
        channel: Optional[Snowflake] = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """|coro|

        Edits the widget.

        You must have :attr:`~Permissions.manage_guild` permission to
        do this

        .. versionadded:: 2.4

        Parameters
        ----------
        enabled: :class:`bool`
            Whether to enable the widget.
        channel: Optional[:class:`~disnake.abc.Snowflake`]
            The new widget channel. Pass ``None`` to remove the widget channel.
        reason: Optional[:class:`str`]
            The reason for editing the widget. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permission to edit the widget.
        HTTPException
            Editing the widget failed.
        """
        payload: Dict[str, Any] = {}
        if enabled is not MISSING:
            payload["enabled"] = enabled
        if channel is not MISSING:
            payload["channel_id"] = None if channel is None else channel.id

        await self._state.http.edit_widget(self.id, payload, reason=reason)

    def image_url(self, style: WidgetStyle = WidgetStyle.shield) -> str:
        """Returns an URL to the widget's .png image.

        .. versionadded:: 2.5

        Parameters
        ----------
        style: :class:`WidgetStyle`
            The widget style.

        Returns
        -------
        :class:`str`
            The widget image URL.

        """
        return self._state.http.widget_image_url(self.id, style=str(style))
