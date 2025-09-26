# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Tuple, Union

from .asset import Asset, AssetMixin
from .errors import InvalidData
from .partial_emoji import PartialEmoji, _EmojiTag
from .user import User
from .utils import MISSING, SnowflakeList, snowflake_time

__all__ = ("Emoji",)

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import Snowflake
    from .guild import Guild
    from .guild_preview import GuildPreview
    from .role import Role
    from .state import ConnectionState
    from .types.emoji import Emoji as EmojiPayload


class Emoji(_EmojiTag, AssetMixin):
    """Represents a custom emoji.

    Depending on the way this object was created, some of the attributes can
    have a value of ``None``.

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

    .. versionchanged:: |vnext|

        This class can now represent app emojis. Use :meth:`Emoji.is_app_emoji` to check for this.
        To check if this is a guild emoji, use :meth:`Emoji.is_guild_emoji`.

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
    guild_id: Optional[:class:`int`]
        The guild ID the emoji belongs to. ``None`` if this is an app emoji.
    available: :class:`bool`
        Whether the emoji is available for use.
    user: Optional[:class:`User`]
        The user that created this emoji. If this is a guild emoji, this can only be retrieved
        using :meth:`Guild.fetch_emoji`/:meth:`Guild.fetch_emojis` while
        having the :attr:`~Permissions.manage_guild_expressions` permission.

        If this is an app emoji, this is the team member that uploaded the emoji,
        or the bot user if created using :meth:`Client.create_application_emoji`.
    """

    __slots__: Tuple[str, ...] = (
        "require_colons",
        "animated",
        "managed",
        "id",
        "name",
        "_roles",
        "guild_id",
        "user",
        "available",
    )

    def __init__(
        self,
        *,
        guild: Optional[Union[Guild, GuildPreview]],
        state: ConnectionState,
        data: EmojiPayload,
    ) -> None:
        self.guild_id: Optional[int] = guild.id if guild else None
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
        return (
            f"<Emoji id={self.id} name={self.name!r} animated={self.animated} managed={self.managed} "
            + (f"{self.guild_id=}" if self.guild_id else "")
            + (f"{self.application_id=}" if self.application_id else "")
            + ">"
        )

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

    @property
    def roles(self) -> List[Role]:
        """List[:class:`Role`]: A :class:`list` of roles that are allowed to use this emoji.

        If roles is empty, the emoji is unrestricted.

        Emojis with :attr:`subscription roles <RoleTags.integration_id>` are considered premium emojis,
        and count towards a separate limit of 25 emojis.
        """
        guild = self.guild
        if guild is None:
            return []

        return [role for role in guild.roles if self._roles.has(role.id)]

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild this emoji belongs to. ``None`` if this is an app emoji.

        .. versionchanged:: |vnext|

            This can now return ``None`` if the emoji is an
            application owned emoji.
        """
        return self._state._get_guild(self.guild_id)

    @property
    def application_id(self) -> Optional[int]:
        """Optional[:class:`int`]: The ID of the application which owns this emoji,
        if this is an app emoji.

        .. versionadded:: |vnext|
        """
        if self.guild_id:
            return None
        return self._state.application_id

    def is_guild_emoji(self) -> bool:
        """Whether this emoji is a guild emoji.

        .. versionadded:: |vnext|

        :return type: :class:`bool`
        """
        return self.guild_id is not None

    def is_app_emoji(self) -> bool:
        """Whether this emoji is an application emoji.

        .. versionadded:: |vnext|

        :return type: :class:`bool`
        """
        return self.guild_id is None

    def is_usable(self) -> bool:
        """Whether the bot can use this emoji.

        .. versionadded:: 1.3

        :return type: :class:`bool`
        """
        if not self.available:
            return False
        # if we don't have a guild, this is an app emoji
        if not self.guild or not self._roles:
            return True
        emoji_roles, my_roles = self._roles, self.guild.me._roles
        return any(my_roles.has(role_id) for role_id in emoji_roles)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        """|coro|

        Deletes the emoji.

        If this is not an app emoji, you must have
        :attr:`~Permissions.manage_guild_expressions` permission to do this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this emoji. Shows up on the audit log.

            Only applies to emojis that belong to a :class:`.Guild`.

        Raises
        ------
        Forbidden
            You are not allowed to delete this emoji.
        HTTPException
            An error occurred deleting the emoji.
        InvalidData
            The emoji data is invalid and cannot be processed.
        """
        if self.guild_id is None:
            # this is an app emoji
            if self.application_id is None:
                # should never happen
                msg = (
                    f"guild_id and application_id are both None when attempting to delete emoji with ID {self.id}."
                    " This may be a library bug! Open an issue on GitHub."
                )
                raise InvalidData(msg)

            return await self._state.http.delete_app_emoji(self.application_id, self.id)
        await self._state.http.delete_custom_emoji(self.guild_id, self.id, reason=reason)

    async def edit(
        self, *, name: str = MISSING, roles: List[Snowflake] = MISSING, reason: Optional[str] = None
    ) -> Emoji:
        """|coro|

        Edits the emoji.

        If this emoji is a guild emoji, you must have
        :attr:`~Permissions.manage_guild_expressions` permission to do this.

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

            Only applies to emojis that belong to a :class:`.Guild`.
        reason: Optional[:class:`str`]
            The reason for editing this emoji. Shows up on the audit log.

            Only applies to emojis that belong to a :class:`.Guild`.

        Raises
        ------
        Forbidden
            You are not allowed to edit this emoji.
        HTTPException
            An error occurred editing the emoji.
        InvalidData
            The emoji data is invalid and cannot be processed.

        Returns
        -------
        :class:`Emoji`
            The newly updated emoji.
        """
        if self.guild_id is None:
            # this is an app emoji
            if self.application_id is None:
                # should never happen
                msg = (
                    f"guild_id and application_id are both None when attempting to edit emoji with ID {self.id}."
                    " This may be a library bug! Open an issue on GitHub."
                )
                raise InvalidData(msg)

            data = await self._state.http.edit_app_emoji(self.application_id, self.id, name=name)
        else:
            payload = {}
            if name is not MISSING:
                payload["name"] = name
            if roles is not MISSING:
                payload["roles"] = [role.id for role in roles]

            data = await self._state.http.edit_custom_emoji(
                self.guild_id, self.id, payload=payload, reason=reason
            )
        return Emoji(guild=self.guild, data=data, state=self._state)
