# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Tuple, Union

from .asset import Asset, AssetMixin
from .partial_emoji import PartialEmoji, _EmojiTag
from .user import User
from .utils import MISSING, SnowflakeList, snowflake_time

__all__ = ("BaseEmoji", "Emoji", "GuildEmoji", "ApplicationEmoji", "AnyEmoji")

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import Snowflake
    from .guild import Guild
    from .guild_preview import GuildPreview
    from .role import Role
    from .state import ConnectionState
    from .types.emoji import Emoji as EmojiPayload


class BaseEmoji(_EmojiTag, AssetMixin):
    """Represents an abstract custom emoji.

    This is usually represented as a custom emoji.

    This isn't meant to be used directly, instead use one of the concrete custom emoji types:

    - :class:`GuildEmoji`
    - :class:`ApplicationEmoji`

    .. collapse:: operations

        .. describe:: x == y

            Checks if two emoji are the same.

        .. describe:: x != y

            Checks if two emoji are not the same.

        .. describe:: hash(x)

            Return the emoji's hash.

        .. describe:: iter(x)

            Returns an iterator of ``(field, value)`` pairs. This allows this class
            to be used as an iterable in list/dict/etc constructions.

        .. describe:: str(x)

            Returns the emoji rendered for Discord.

    Attributes
    ----------
    name: :class:`str`
        The emoji's name.
    id: :class:`int`
        The emoji's ID.
    require_colons: :class:`bool`
        Whether colons are required to use this emoji in the client (:PJSalt: vs PJSalt).
    animated: :class:`bool`
        Whether the emoji is animated or not.
    managed: :class:`bool`
        Whether the emoji is managed by a Twitch integration.
    available: :class:`bool`
        Whether the emoji is available for use.
    user: Optional[:class:`User`]
        The user that created this emoji. This can only be retrieved using
        :meth:`Guild.fetch_emoji`/:meth:`Guild.fetch_emojis` while
        having the :attr:`~Permissions.manage_guild_expressions` permission.
    """

    __slots__: Tuple[str, ...] = (
        "require_colons",
        "animated",
        "managed",
        "id",
        "name",
        "_roles",
        "user",
        "available",
    )

    def __init__(self, *, state: ConnectionState, data: EmojiPayload) -> None:
        self._state: ConnectionState = state
        self._from_data(data)

    def _from_data(self, emoji: EmojiPayload) -> None:
        self.require_colons: bool = emoji.get("require_colons", False)
        self.managed: bool = emoji.get("managed", False)
        self.id: int = int(emoji["id"])  # type: ignore
        self.name: str = emoji["name"]  # type: ignore
        self.animated: bool = emoji.get("animated", False)
        self.available: bool = emoji.get("available", True)
        self._roles: SnowflakeList = SnowflakeList(map(int, emoji.get("roles", [])))
        user = emoji.get("user")
        self.user: Optional[User] = User(state=self._state, data=user) if user else None

    def _to_partial(self) -> PartialEmoji:
        return PartialEmoji(name=self.name, animated=self.animated, id=self.id)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        for attr in self.__slots__:
            if attr[0] != "_":
                value = getattr(self, attr, None)
                if value is not None:
                    yield (attr, value)

    def __str__(self) -> str:
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"

    def __repr__(self) -> str:
        return f"<BaseEmoji id={self.id} name={self.name!r} animated={self.animated}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, _EmojiTag) and self.id == other.id

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.id >> 22

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: Returns the emoji's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def url(self) -> str:
        """:class:`str`: Returns the URL of the emoji."""
        fmt = "gif" if self.animated else "png"
        return f"{Asset.BASE}/emojis/{self.id}.{fmt}"


class GuildEmoji(BaseEmoji):
    """Represents a custom emoji in a guild.

    Depending on the way this object was created, some of the attributes can
    have a value of ``None``.

    This is an alias for :class:`Emoji`.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two emoji are the same.

        .. describe:: x != y

            Checks if two emoji are not the same.

        .. describe:: hash(x)

            Return the emoji's hash.

        .. describe:: iter(x)

            Returns an iterator of ``(field, value)`` pairs. This allows this class
            to be used as an iterable in list/dict/etc constructions.

        .. describe:: str(x)

            Returns the emoji rendered for Discord.

    Attributes
    ----------
    name: :class:`str`
        The emoji's name.
    id: :class:`int`
        The emoji's ID.
    require_colons: :class:`bool`
        Whether colons are required to use this emoji in the client (:PJSalt: vs PJSalt).
    animated: :class:`bool`
        Whether the emoji is animated or not.
    managed: :class:`bool`
        Whether the emoji is managed by a Twitch integration.
    guild_id: :class:`int`
        The guild ID the emoji belongs to.
    available: :class:`bool`
        Whether the emoji is available for use.
    user: Optional[:class:`User`]
        The user that created this emoji. This can only be retrieved using
        :meth:`Guild.fetch_emoji`/:meth:`Guild.fetch_emojis` while
        having the :attr:`~Permissions.manage_guild_expressions` permission.
    """

    __slots__: Tuple[str, ...] = BaseEmoji.__slots__ + ("guild_id",)

    def __init__(
        self, *, guild: Union[Guild, GuildPreview], state: ConnectionState, data: EmojiPayload
    ) -> None:
        self.guild_id: int = guild.id
        super().__init__(state=state, data=data)

    def __repr__(self) -> str:
        return f"<GuildEmoji id={self.id} name={self.name!r} animated={self.animated} managed={self.managed}>"

    @property
    def roles(self) -> List[Role]:
        """List[:class:`Role`]: A :class:`list` of roles that are allowed to use this emoji.

        If roles is empty, the emoji is unrestricted.

        Emojis with :attr:`subscription roles <RoleTags.integration_id>` are considered premium emojis,
        and count towards a separate limit of 25 emojis.
        """
        guild = self.guild
        if guild is None:  # pyright: ignore[reportUnnecessaryComparison]
            return []

        return [role for role in guild.roles if self._roles.has(role.id)]

    @property
    def guild(self) -> Guild:
        """:class:`Guild`: The guild this emoji belongs to."""
        # this will most likely never return None but there's a possibility
        return self._state._get_guild(self.guild_id)  # type: ignore

    def is_usable(self) -> bool:
        """Whether the bot can use this emoji.

        .. versionadded:: 1.3

        :return type: :class:`bool`
        """
        if not self.available:
            return False
        if not self._roles:
            return True
        emoji_roles, my_roles = self._roles, self.guild.me._roles
        return any(my_roles.has(role_id) for role_id in emoji_roles)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        """|coro|

        Deletes the custom emoji.

        You must have :attr:`~Permissions.manage_guild_expressions` permission to
        do this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this emoji. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You are not allowed to delete this emoji.
        HTTPException
            An error occurred deleting the emoji.
        """
        await self._state.http.delete_custom_emoji(self.guild.id, self.id, reason=reason)

    async def edit(
        self, *, name: str = MISSING, roles: List[Snowflake] = MISSING, reason: Optional[str] = None
    ) -> GuildEmoji:
        """|coro|

        Edits the custom emoji.

        You must have :attr:`~Permissions.manage_guild_expressions` permission to
        do this.

        .. versionchanged:: 2.0
            The newly updated emoji is returned.

        Parameters
        ----------
        name: :class:`str`
            The new emoji name.
        roles: Optional[List[:class:`~disnake.abc.Snowflake`]]
            A list of roles that can use this emoji. An empty list can be passed to make it available to everyone.

            An emoji cannot have both subscription roles (see :attr:`RoleTags.integration_id`) and
            non-subscription roles, and emojis can't be converted between premium and non-premium
            after creation.
        reason: Optional[:class:`str`]
            The reason for editing this emoji. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You are not allowed to edit this emoji.
        HTTPException
            An error occurred editing the emoji.

        Returns
        -------
        :class:`GuildEmoji`
            The newly updated emoji.
        """
        payload = {}
        if name is not MISSING:
            payload["name"] = name
        if roles is not MISSING:
            payload["roles"] = [role.id for role in roles]

        data = await self._state.http.edit_custom_emoji(
            self.guild.id, self.id, payload=payload, reason=reason
        )
        return GuildEmoji(guild=self.guild, data=data, state=self._state)


Emoji = GuildEmoji


class ApplicationEmoji(BaseEmoji):
    """Represents a custom emoji from an application.

    Depending on the way this object was created, some attributes can
    have a value of ``None``.

    .. container:: operations

        .. describe:: x == y

            Checks if two emoji are the same.

        .. describe:: x != y

            Checks if two emoji are not the same.

        .. describe:: hash(x)

            Return the emoji's hash.

        .. describe:: iter(x)

            Returns an iterator of ``(field, value)`` pairs. This allows this class
            to be used as an iterable in list/dict/etc constructions.

        .. describe:: str(x)

            Returns the emoji rendered for discord.

    Attributes
    ----------
    name: :class:`str`
        The name of the emoji.
    id: :class:`int`
        The emoji's ID.
    require_colons: :class:`bool`
        If colons are required to use this emoji in the client (:PJSalt: vs PJSalt).
    animated: :class:`bool`
        Whether an emoji is animated or not.
    managed: :class:`bool`
        If this emoji is managed by a Twitch integration.
    application_id: Optional[:class:`int`]
        The application ID the emoji belongs to, if available.
    available: :class:`bool`
        Whether the emoji is available for use.
    user: Optional[:class:`User`]
        The user that created the emoji.
    """

    __slots__: Tuple[str, ...] = BaseEmoji.__slots__ + ("application_id",)

    def __init__(self, *, application_id: int, state: ConnectionState, data: EmojiPayload) -> None:
        self.application_id: int = application_id
        super().__init__(state=state, data=data)

    def __repr__(self) -> str:
        return f"<ApplicationEmoji id={self.id} name={self.name!r} animated={self.animated}>"

    def is_usable(self) -> bool:
        """Whether the bot can use this emoji."""
        return self.application_id == self._state.application_id

    async def delete(self) -> None:
        """|coro|
        Deletes the application emoji.
        You must own the emoji to do this.

        Raises
        ------
        Forbidden
            You are not allowed to delete the emoji.
        HTTPException
            An error occurred deleting the emoji.
        """
        await self._state.http.delete_application_emoji(self.application_id, self.id)
        if self._state.cache_app_emojis and self._state.get_emoji(self.id):
            self._state._remove_emoji(self)

    async def edit(
        self,
        *,
        name: str = MISSING,
    ) -> ApplicationEmoji:
        r"""|coro|
        Edits the application emoji.
        You must own the emoji to do this.

        Parameters
        ----------
        name: :class:`str`
            The new emoji name.

        Raises
        ------
        Forbidden
            You are not allowed to edit the emoji.
        HTTPException
            An error occurred editing the emoji.

        Returns
        -------
        :class:`ApplicationEmoji`
            The newly updated emoji.
        """
        payload = {}
        if name is not MISSING:
            payload["name"] = name

        data = await self._state.http.edit_application_emoji(
            self.application_id, self.id, payload=payload
        )
        return self._state.store_application_emoji(self.application_id, data)


AnyEmoji = Union[GuildEmoji, ApplicationEmoji]
