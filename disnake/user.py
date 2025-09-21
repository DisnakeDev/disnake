# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import disnake.abc

from .asset import Asset
from .colour import Colour
from .enums import Locale, NameplatePalette, try_enum
from .flags import PublicUserFlags
from .utils import MISSING, _assetbytes_to_base64_data, _get_as_snowflake, snowflake_time

if TYPE_CHECKING:
    from datetime import datetime

    from typing_extensions import Self

    from .asset import AssetBytes
    from .channel import DMChannel
    from .guild import Guild
    from .message import Message
    from .state import ConnectionState
    from .types.channel import DMChannel as DMChannelPayload
    from .types.user import (
        AvatarDecorationData as AvatarDecorationDataPayload,
        Collectibles as CollectiblesPayload,
        Nameplate as NameplatePayload,
        PartialUser as PartialUserPayload,
        User as UserPayload,
        UserPrimaryGuild as UserPrimaryGuildPayload,
    )


__all__ = (
    "User",
    "ClientUser",
    "Nameplate",
    "Collectibles",
    "PrimaryGuild",
)


class _UserTag:
    __slots__ = ()
    id: int


class BaseUser(_UserTag):
    __slots__ = (
        "name",
        "id",
        "discriminator",
        "global_name",
        "bot",
        "system",
        "_avatar",
        "_banner",
        "_avatar_decoration_data",
        "_accent_colour",
        "_public_flags",
        "_collectibles",
        "_primary_guild",
        "_state",
    )

    def __init__(
        self, *, state: ConnectionState, data: Union[UserPayload, PartialUserPayload]
    ) -> None:
        self._state: ConnectionState = state
        self._update(data)

    def __repr__(self) -> str:
        return (
            f"<BaseUser id={self.id} name={self.name!r} global_name={self.global_name!r}"
            f" discriminator={self.discriminator!r} bot={self.bot} system={self.system}>"
        )

    def __str__(self) -> str:
        discriminator = self.discriminator
        if discriminator == "0":
            return self.name
        # legacy behavior
        return f"{self.name}#{discriminator}"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, _UserTag) and other.id == self.id

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.id >> 22

    def _update(self, data: Union[UserPayload, PartialUserPayload]) -> None:
        self.name: str = data["username"]
        self.id: int = int(data["id"])
        self.discriminator: str = data["discriminator"]
        self.global_name: Optional[str] = data.get("global_name")
        self._avatar: Optional[str] = data["avatar"]
        self._banner: Optional[str] = data.get("banner")
        self._avatar_decoration_data: Optional[AvatarDecorationDataPayload] = data.get(
            "avatar_decoration_data"
        )
        self._accent_colour: Optional[int] = data.get("accent_color")
        self._public_flags: int = data.get("public_flags", 0)
        self._collectibles: Optional[CollectiblesPayload] = data.get("collectibles")
        self._primary_guild: Optional[UserPrimaryGuildPayload] = data.get("primary_guild")
        self.bot: bool = data.get("bot", False)
        self.system: bool = data.get("system", False)

    @classmethod
    def _copy(cls, user: BaseUser) -> Self:
        self = cls.__new__(cls)  # bypass __init__

        self._state = user._state
        self.name = user.name
        self.id = user.id
        self.discriminator = user.discriminator
        self.global_name = user.global_name
        self._avatar = user._avatar
        self._banner = user._banner
        self._avatar_decoration_data = user._avatar_decoration_data
        self._accent_colour = user._accent_colour
        self._public_flags = user._public_flags
        self._collectibles = user._collectibles
        self._primary_guild = user._primary_guild
        self.bot = user.bot
        self.system = user.system

        return self

    def _to_minimal_user_json(self) -> UserPayload:
        return {
            "username": self.name,
            "id": self.id,
            "avatar": self._avatar,
            "discriminator": self.discriminator,
            "global_name": self.global_name,
            "bot": self.bot,
            "public_flags": self._public_flags,
            "avatar_decoration_data": self._avatar_decoration_data,
            "collectibles": self._collectibles,
            "primary_guild": self._primary_guild,
        }

    @property
    def public_flags(self) -> PublicUserFlags:
        """:class:`PublicUserFlags`: The publicly available flags the user has."""
        return PublicUserFlags._from_value(self._public_flags)

    @property
    def avatar(self) -> Optional[Asset]:
        """:class:`Asset` | ``None``: Returns an :class:`Asset` for the avatar the user has.

        If the user does not have a traditional avatar, ``None`` is returned.
        If you want the avatar that a user has displayed, consider :attr:`display_avatar`.
        """
        if self._avatar is not None:
            return Asset._from_avatar(self._state, self.id, self._avatar)
        return None

    @property
    def default_avatar(self) -> Asset:
        """:class:`Asset`: Returns the default avatar for a given user.

        .. versionchanged:: 2.9
            Added handling for users migrated to the new username system without discriminators.
        """
        if self.discriminator == "0":
            index = (self.id >> 22) % 6
        else:
            # legacy behavior
            index = int(self.discriminator) % 5
        return Asset._from_default_avatar(self._state, index)

    @property
    def display_avatar(self) -> Asset:
        """:class:`Asset`: Returns the user's display avatar.

        For regular users this is just their default avatar or uploaded avatar.

        .. versionadded:: 2.0
        """
        return self.avatar or self.default_avatar

    @property
    def banner(self) -> Optional[Asset]:
        """:class:`Asset` | ``None``: Returns the user's banner asset, if available.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        if self._banner is None:
            return None
        return Asset._from_banner(self._state, self.id, self._banner)

    @property
    def avatar_decoration(self) -> Optional[Asset]:
        """:class:`Asset` | ``None``: Returns the user's avatar decoration asset, if available.

        .. versionadded:: 2.10

        .. note::

            Since Discord always sends an animated PNG for animated avatar decorations,
            the following methods will not work as expected:

            - :meth:`Asset.replace`
            - :meth:`Asset.with_size`
            - :meth:`Asset.with_format`
            - :meth:`Asset.with_static_format`
        """
        if self._avatar_decoration_data is None:
            return None
        return Asset._from_avatar_decoration(self._state, self._avatar_decoration_data["asset"])

    @property
    def collectibles(self) -> Collectibles:
        """:class:`Collectibles`: Returns the user's collectibles.

        .. versionadded:: 2.11
        """
        return Collectibles(
            state=self._state, data=(self._collectibles if self._collectibles else {})
        )

    @property
    def accent_colour(self) -> Optional[Colour]:
        """:class:`Colour` | ``None``: Returns the user's accent colour, if applicable.

        There is an alias for this named :attr:`accent_color`.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        if self._accent_colour is None:
            return None
        return Colour(int(self._accent_colour))

    @property
    def accent_color(self) -> Optional[Colour]:
        """:class:`Colour` | ``None``: Returns the user's accent color, if applicable.

        There is an alias for this named :attr:`accent_colour`.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        return self.accent_colour

    @property
    def colour(self) -> Colour:
        """:class:`Colour`: A property that returns a colour denoting the rendered colour
        for the user. This always returns :meth:`Colour.default`.

        There is an alias for this named :attr:`color`.
        """
        return Colour.default()

    @property
    def color(self) -> Colour:
        """:class:`Colour`: A property that returns a color denoting the rendered color
        for the user. This always returns :meth:`Colour.default`.

        There is an alias for this named :attr:`colour`.
        """
        return self.colour

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the given user."""
        return f"<@{self.id}>"

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: Returns the user's creation time in UTC.

        This is when the user's Discord account was created.
        """
        return snowflake_time(self.id)

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the user's display name.

        This is their :attr:`global name <.global_name>` if set,
        or their :attr:`username <.name>` otherwise.

        .. versionchanged:: 2.9
            Added :attr:`.global_name`.
        """
        return self.global_name or self.name

    @property
    def primary_guild(self) -> Optional[PrimaryGuild]:
        """:class:`PrimaryGuild` | ``None``: Returns the user's primary guild, if any.

        .. versionadded:: 2.11
        """
        if self._primary_guild is not None:
            return PrimaryGuild(
                state=self._state,
                data=self._primary_guild,
            )
        return None

    def mentioned_in(self, message: Message) -> bool:
        """Checks if the user is mentioned in the specified message.

        Parameters
        ----------
        message: :class:`Message`
            The message to check.

        Returns
        -------
        :class:`bool`
            Indicates if the user is mentioned in the message.
        """
        if message.mention_everyone:
            return True

        return any(user.id == self.id for user in message.mentions)


class ClientUser(BaseUser):
    """Represents your Discord user.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's username (with discriminator, if not migrated to new system yet).

    Attributes
    ----------
    name: :class:`str`
        The user's username.
    id: :class:`int`
        The user's unique ID.
    discriminator: :class:`str`
        The user's discriminator.

    global_name: :class:`str` | ``None``
        The user's global display name, if set.
        This takes precedence over :attr:`.name` when shown.

        .. versionadded:: 2.9

    bot: :class:`bool`
        Specifies if the user is a bot account.
    system: :class:`bool`
        Specifies if the user is a system user (i.e. represents Discord officially).

        .. versionadded:: 1.3

    verified: :class:`bool`
        Specifies if the user's email is verified.
    locale: :class:`Locale` | ``None``
        The IETF language tag used to identify the language the user is using.

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    mfa_enabled: :class:`bool`
        Specifies if the user has MFA turned on and working.
    """

    __slots__ = ("locale", "_flags", "verified", "mfa_enabled", "__weakref__")

    if TYPE_CHECKING:
        verified: bool
        locale: Optional[Locale]
        mfa_enabled: bool
        _flags: int

    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        super().__init__(state=state, data=data)

    def __repr__(self) -> str:
        return (
            f"<ClientUser id={self.id} name={self.name!r} global_name={self.global_name!r} discriminator={self.discriminator!r}"
            f" bot={self.bot} verified={self.verified} mfa_enabled={self.mfa_enabled}>"
        )

    def _update(self, data: UserPayload) -> None:
        super()._update(data)
        self.verified = data.get("verified", False)
        locale = data.get("locale")
        self.locale = try_enum(Locale, locale) if locale else None
        self._flags = data.get("flags", 0)
        self.mfa_enabled = data.get("mfa_enabled", False)

    async def edit(
        self,
        *,
        username: str = MISSING,
        avatar: Optional[AssetBytes] = MISSING,
        banner: Optional[AssetBytes] = MISSING,
    ) -> ClientUser:
        """|coro|

        Edits the current profile of the client.

        .. versionchanged:: 2.0
            The edit is no longer in-place, instead the newly edited client user is returned.

        .. versionchanged:: 2.6
            Raises :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        username: :class:`str`
            The new username you wish to change to.
        avatar: |resource_type| | ``None``
            A :term:`py:bytes-like object` or asset representing the image to upload.
            Could be ``None`` to denote no avatar.

            Only JPG, PNG, WEBP (static), and GIF (static/animated) images are supported.

            .. versionchanged:: 2.5
                Now accepts various resource types in addition to :class:`bytes`.

        banner: |resource_type| | ``None``
            A :term:`py:bytes-like object` or asset representing the image to upload.
            Could be ``None`` to denote no banner.

            Only JPG, PNG, WEBP (static), and GIF (static/animated) images are supported.

            .. versionadded:: 2.10

        Raises
        ------
        NotFound
            The ``avatar`` or ``banner`` asset couldn't be found.
        HTTPException
            Editing your profile failed.
        TypeError
            The ``avatar`` or ``banner`` asset is a lottie sticker (see :func:`Sticker.read`).
        ValueError
            Wrong image format passed for ``avatar`` or ``banner``.

        Returns
        -------
        :class:`ClientUser`
            The newly edited client user.
        """
        payload: Dict[str, Any] = {}
        if username is not MISSING:
            payload["username"] = username

        if avatar is not MISSING:
            payload["avatar"] = await _assetbytes_to_base64_data(avatar)

        if banner is not MISSING:
            payload["banner"] = await _assetbytes_to_base64_data(banner)

        data: UserPayload = await self._state.http.edit_profile(payload)
        return ClientUser(state=self._state, data=data)


class Nameplate:
    """
    Represents the decoration behind the name of a user that appears
    in the server, DM and DM group members list.

    .. versionadded:: 2.11

    Attributes
    ----------
    sku_id: :class:`int`
        The ID of the nameplate SKU.
    label: :class:`str`
        The label of this nameplate.
    palette: :class:`NameplatePalette`
        The background color of the nameplate.
    """

    __slots__ = (
        "sku_id",
        "label",
        "palette",
        "_state",
        "_asset",
    )

    def __init__(self, *, state: ConnectionState, data: NameplatePayload) -> None:
        self._state: ConnectionState = state
        self.sku_id: int = int(data["sku_id"])
        self._asset: str = data["asset"]
        self.label: str = data["label"]
        self.palette = try_enum(NameplatePalette, data["palette"])

    def __repr__(self) -> str:
        return f"<Nameplate sku_id={self.sku_id} label={self.label!r} palette={self.palette}>"

    @property
    def animated_asset(self) -> Asset:
        """:class:`Asset`: Returns the animated nameplate for the user.

        .. versionadded:: 2.11

        .. note::

             Since Discord always sends a WEBM for animated nameplates,
             the following methods will not work as expected:

             - :meth:`Asset.replace`
             - :meth:`Asset.with_size`
             - :meth:`Asset.with_format`
             - :meth:`Asset.with_static_format`
        """
        return Asset._from_nameplate(self._state, self._asset)

    @property
    def static_asset(self) -> Asset:
        """:class:`Asset`: Returns the static nameplate for the user.

        .. versionadded:: 2.11
        """
        return Asset._from_nameplate(self._state, self._asset, animated=False)


class Collectibles:
    """
    Represents the collectibles the user has, excluding Avatar Decorations and Profile Effects.

    .. versionadded:: 2.11

    Attributes
    ----------
    nameplate: :class:`Nameplate` | ``None``
        The nameplate of the user, if available.
    """

    __slots__ = ("nameplate",)

    def __init__(self, state: ConnectionState, data: CollectiblesPayload) -> None:
        self.nameplate: Optional[Nameplate] = (
            Nameplate(state=state, data=nameplate_data)
            if (nameplate_data := data.get("nameplate"))
            else None
        )

    def __repr__(self) -> str:
        return f"<Collectibles nameplate={self.nameplate}>"


class User(BaseUser, disnake.abc.Messageable):
    """Represents a Discord user.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's username (with discriminator, if not migrated to new system yet).

    Attributes
    ----------
    name: :class:`str`
        The user's username.
    id: :class:`int`
        The user's unique ID.
    discriminator: :class:`str`
        The user's discriminator.

        .. note::
            This is being phased out by Discord; the username system is moving away from ``username#discriminator``
            to users having a globally unique username.
            The value of a single zero (``"0"``) indicates that the user has been migrated to the new system.
            See the `help article <https://dis.gd/app-usernames>`__ for details.

    global_name: :class:`str` | ``None``
        The user's global display name, if set.
        This takes precedence over :attr:`.name` when shown.

        .. versionadded:: 2.9

    bot: :class:`bool`
        Specifies if the user is a bot account.
    system: :class:`bool`
        Specifies if the user is a system user (i.e. represents Discord officially).
    """

    __slots__ = ("__weakref__",)

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} name={self.name!r} global_name={self.global_name!r}"
            f" discriminator={self.discriminator!r} bot={self.bot}>"
        )

    async def _get_channel(self) -> DMChannel:
        ch = await self.create_dm()
        return ch

    @property
    def dm_channel(self) -> Optional[DMChannel]:
        """:class:`DMChannel` | ``None``: Returns the channel associated with this user if it exists.

        If this returns ``None``, you can create a DM channel by calling the
        :meth:`create_dm` coroutine function.
        """
        return self._state._get_private_channel_by_user(self.id)

    @property
    def mutual_guilds(self) -> List[Guild]:
        """:class:`list`\\[:class:`Guild`]: The guilds that the user shares with the client.

        .. note::

            This will only return mutual guilds within the client's internal cache.

        .. versionadded:: 1.7
        """
        return [guild for guild in self._state._guilds.values() if guild.get_member(self.id)]

    async def create_dm(self) -> DMChannel:
        """|coro|

        Creates a :class:`DMChannel` with this user.

        This should be rarely called, as this is done transparently for most
        people.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        found = self.dm_channel
        if found is not None:
            return found

        state = self._state
        data: DMChannelPayload = await state.http.start_private_message(self.id)
        return state.add_dm_channel(data)


class PrimaryGuild:
    """Represents a user's primary guild.

    .. versionadded:: 2.11

    Attributes
    ----------
    guild_id: :class:`int` | ``None``
        The ID of the user's primary guild.
    identity_enabled: :class:`bool` | ``None``
        Whether the user is displaying the primary guild's server tag. This can be ``None``
        if the system clears the identity, e.g. the server no longer supports tags. This will be ``False``
        if the user manually removes their tag.
    tag: :class:`str` | ``None``
        The text of the user's server tag, up to 4 characters.
    """

    __slots__ = (
        "guild_id",
        "identity_enabled",
        "tag",
        "_state",
        "_badge",
    )

    def __init__(self, *, state: ConnectionState, data: UserPrimaryGuildPayload) -> None:
        self._state = state
        self.guild_id: Optional[int] = _get_as_snowflake(data, "identity_guild_id")
        self.identity_enabled: Optional[bool] = data.get("identity_enabled")
        self.tag: Optional[str] = data.get("tag")
        self._badge: Optional[str] = data.get("badge")

    def __repr__(self) -> str:
        return f"<PrimaryGuild guild_id={self.guild_id} identity_enabled={self.identity_enabled} tag={self.tag}>"

    @property
    def badge(self) -> Optional[Asset]:
        """:class:`Asset` | ``None``: Returns the server tag badge, if any."""
        # if badge is not None identity_guild_id won't be None either
        if self._badge is not None and self.guild_id is not None:
            return Asset._from_guild_tag_badge(self._state, self.guild_id, self._badge)
        return None
