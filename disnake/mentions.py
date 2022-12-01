# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Union

from .enums import MessageType

__all__ = ("AllowedMentions",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from .abc import Snowflake
    from .message import Message
    from .types.message import AllowedMentions as AllowedMentionsPayload


class _FakeBool:
    def __repr__(self) -> str:
        return "True"

    def __eq__(self, other) -> bool:
        return other is True

    def __bool__(self) -> bool:
        return True


default: Any = _FakeBool()


class AllowedMentions:
    """A class that represents what mentions are allowed in a message.

    This class can be set during :class:`Client` initialisation to apply
    to every message sent. It can also be applied on a per message basis
    via :meth:`abc.Messageable.send` for more fine-grained control.

    Attributes
    ----------
    everyone: :class:`bool`
        Whether to allow everyone and here mentions. Defaults to ``True``.
    users: Union[:class:`bool`, List[:class:`abc.Snowflake`]]
        Controls the users being mentioned. If ``True`` (the default) then
        users are mentioned based on the message content. If ``False`` then
        users are not mentioned at all. If a list of :class:`abc.Snowflake`
        is given then only the users provided will be mentioned, provided those
        users are in the message content.
    roles: Union[:class:`bool`, List[:class:`abc.Snowflake`]]
        Controls the roles being mentioned. If ``True`` (the default) then
        roles are mentioned based on the message content. If ``False`` then
        roles are not mentioned at all. If a list of :class:`abc.Snowflake`
        is given then only the roles provided will be mentioned, provided those
        roles are in the message content.
    replied_user: :class:`bool`
        Whether to mention the author of the message being replied to. Defaults
        to ``True``.

        .. versionadded:: 1.6
    """

    __slots__ = ("everyone", "users", "roles", "replied_user")

    def __init__(
        self,
        *,
        everyone: bool = default,
        users: Union[bool, List[Snowflake]] = default,
        roles: Union[bool, List[Snowflake]] = default,
        replied_user: bool = default,
    ) -> None:
        self.everyone = everyone
        self.users = users
        self.roles = roles
        self.replied_user = replied_user

    @classmethod
    def all(cls) -> Self:
        """A factory method that returns a :class:`AllowedMentions` with all fields explicitly set to ``True``

        .. versionadded:: 1.5
        """
        return cls(everyone=True, users=True, roles=True, replied_user=True)

    @classmethod
    def none(cls) -> Self:
        """A factory method that returns a :class:`AllowedMentions` with all fields set to ``False``

        .. versionadded:: 1.5
        """
        return cls(everyone=False, users=False, roles=False, replied_user=False)

    @classmethod
    def from_message(cls, message: Message) -> Self:
        """A factory method that returns a :class:`AllowedMentions` derived from the current :class:`.Message` state.

        Note that this is not what AllowedMentions the message was sent with, but what the message actually mentioned.
        For example, a message that successfully mentioned everyone will have :attr:`~AllowedMentions.everyone` set to ``True``.

        .. versionadded:: 2.6
        """
        # circular import
        from .message import Message

        return cls(
            everyone=message.mention_everyone,
            users=message.mentions.copy(),  # type: ignore # mentions is a list of Snowflakes
            roles=message.role_mentions.copy(),  # type: ignore # mentions is a list of Snowflakes
            replied_user=bool(
                message.type is MessageType.reply
                and message.reference
                and isinstance(message.reference.resolved, Message)
                and message.reference.resolved.author in message.mentions
            ),
        )

    def to_dict(self) -> AllowedMentionsPayload:
        parse = []
        data = {}

        if self.everyone:
            parse.append("everyone")

        if self.users == True:  # noqa: E712
            parse.append("users")
        elif self.users != False:  # noqa: E712
            data["users"] = [x.id for x in self.users]

        if self.roles == True:  # noqa: E712
            parse.append("roles")
        elif self.roles != False:  # noqa: E712
            data["roles"] = [x.id for x in self.roles]

        if self.replied_user:
            data["replied_user"] = True

        data["parse"] = parse
        return data  # type: ignore

    def merge(self, other: AllowedMentions) -> AllowedMentions:
        # Creates a new AllowedMentions by merging from another one.
        # Merge is done by using the 'self' values unless explicitly
        # overridden by the 'other' values.
        everyone = self.everyone if other.everyone is default else other.everyone
        users = self.users if other.users is default else other.users
        roles = self.roles if other.roles is default else other.roles
        replied_user = self.replied_user if other.replied_user is default else other.replied_user
        return AllowedMentions(
            everyone=everyone, roles=roles, users=users, replied_user=replied_user
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(everyone={self.everyone}, "
            f"users={self.users}, roles={self.roles}, replied_user={self.replied_user})"
        )
