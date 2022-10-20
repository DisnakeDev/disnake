# SPDX-License-Identifier: MIT

from __future__ import annotations

from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    Optional,
    Set,
    Tuple,
    overload,
)

from .flags import BaseFlags, alias_flag_value, flag_value
from .utils import _generated, _overload_with_permissions

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = (
    "Permissions",
    "PermissionOverwrite",
)


# A permission alias works like a regular flag but is marked
# So the PermissionOverwrite knows to work with it
class permission_alias(alias_flag_value):
    alias: str


def make_permission_alias(alias: str) -> Callable[[Callable[[Any], int]], permission_alias]:
    def decorator(func: Callable[[Any], int]) -> permission_alias:
        ret = permission_alias(func)
        ret.alias = alias
        return ret

    return decorator


def cached_creation(func):
    @wraps(func)
    def wrapped(cls):
        try:
            value = func.__stored_value__
        except AttributeError:
            value = func(cls).value
            func.__stored_value__ = value
        return cls(value)

    return wrapped


class Permissions(BaseFlags):
    """Wraps up the Discord permission value.

    The properties provided are two way. You can set and retrieve individual
    bits using the properties as if they were regular bools. This allows
    you to edit permissions.

    To construct an object you can pass keyword arguments denoting the permissions
    to enable or disable.
    Arguments are applied in order, which notably also means that supplying a flag
    and its alias will make whatever comes last overwrite the first one; as an example,
    ``Permissions(external_emojis=True, use_external_emojis=False)`` and
    ``Permissions(use_external_emojis=True, external_emojis=False)``
    both result in the same permissions value (``0``).

    .. versionchanged:: 1.3
        You can now use keyword arguments to initialize :class:`Permissions`
        similar to :meth:`update`.

    .. container:: operations

        .. describe:: x == y

            Checks if two permissions are equal.
        .. describe:: x != y

            Checks if two permissions are not equal.
        .. describe:: x <= y

            Checks if a permission is a subset of another permission.
        .. describe:: x >= y

            Checks if a permission is a superset of another permission.
        .. describe:: x < y

            Checks if a permission is a strict subset of another permission.
        .. describe:: x > y

            Checks if a permission is a strict superset of another permission.
        .. describe:: x | y, x |= y

            Returns a new Permissions instance with all enabled permissions from both x and y.
            (Using ``|=`` will update in place).

            .. versionadded:: 2.6
        .. describe:: x & y, x &= y

            Returns a new Permissions instance with only permissions enabled on both x and y.
            (Using ``&=`` will update in place).

            .. versionadded:: 2.6
        .. describe:: x ^ y, x ^= y

            Returns a new Permissions instance with only permissions enabled on one of x or y, but not both.
            (Using ``^=`` will update in place).

            .. versionadded:: 2.6
        .. describe:: ~x

            Returns a new Permissions instance with all permissions from x inverted.

            .. versionadded:: 2.6
        .. describe:: hash(x)

               Return the permission's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(perm, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.
               Note that aliases are not shown.


        Additionally supported are a few operations on class attributes.

        .. describe:: Permissions.y | Permissions.z, Permissions(y=True) | Permissions.z

            Returns a Permissions instance with all provided permissions enabled.

            .. versionadded:: 2.6
        .. describe:: ~Permissions.y

            Returns a Permissions instance with all permissions except ``y`` inverted from their default value.

            .. versionadded:: 2.6

    Attributes
    ----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available permissions. You should query
        permissions via the properties rather than using this raw value.
    """

    __slots__ = ()

    @overload
    @_generated
    def __init__(
        self,
        permissions: int = 0,
        *,
        add_reactions: bool = ...,
        administrator: bool = ...,
        attach_files: bool = ...,
        ban_members: bool = ...,
        change_nickname: bool = ...,
        connect: bool = ...,
        create_forum_threads: bool = ...,
        create_instant_invite: bool = ...,
        create_private_threads: bool = ...,
        create_public_threads: bool = ...,
        deafen_members: bool = ...,
        embed_links: bool = ...,
        external_emojis: bool = ...,
        external_stickers: bool = ...,
        kick_members: bool = ...,
        manage_channels: bool = ...,
        manage_emojis: bool = ...,
        manage_emojis_and_stickers: bool = ...,
        manage_events: bool = ...,
        manage_guild: bool = ...,
        manage_messages: bool = ...,
        manage_nicknames: bool = ...,
        manage_permissions: bool = ...,
        manage_roles: bool = ...,
        manage_threads: bool = ...,
        manage_webhooks: bool = ...,
        mention_everyone: bool = ...,
        moderate_members: bool = ...,
        move_members: bool = ...,
        mute_members: bool = ...,
        priority_speaker: bool = ...,
        read_message_history: bool = ...,
        read_messages: bool = ...,
        request_to_speak: bool = ...,
        send_messages: bool = ...,
        send_messages_in_threads: bool = ...,
        send_tts_messages: bool = ...,
        speak: bool = ...,
        start_embedded_activities: bool = ...,
        stream: bool = ...,
        use_application_commands: bool = ...,
        use_embedded_activities: bool = ...,
        use_external_emojis: bool = ...,
        use_external_stickers: bool = ...,
        use_slash_commands: bool = ...,
        use_voice_activation: bool = ...,
        view_audit_log: bool = ...,
        view_channel: bool = ...,
        view_guild_insights: bool = ...,
    ):
        ...

    @overload
    @_generated
    def __init__(
        self,
        permissions: int = 0,
    ):
        ...

    @_overload_with_permissions
    def __init__(self, permissions: int = 0, **kwargs: bool):
        if not isinstance(permissions, int):
            raise TypeError(
                f"Expected int parameter, received {permissions.__class__.__name__} instead."
            )

        self.value = permissions
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid permission name.")
            setattr(self, key, value)

    def is_subset(self, other: Permissions) -> bool:
        """Returns ``True`` if self has the same or fewer permissions as other."""
        if isinstance(other, Permissions):
            return (self.value & other.value) == self.value
        else:
            raise TypeError(
                f"cannot compare {self.__class__.__name__} with {other.__class__.__name__}"
            )

    def is_superset(self, other: Permissions) -> bool:
        """Returns ``True`` if self has the same or more permissions as other."""
        if isinstance(other, Permissions):
            return (self.value | other.value) == self.value
        else:
            raise TypeError(
                f"cannot compare {self.__class__.__name__} with {other.__class__.__name__}"
            )

    def is_strict_subset(self, other: Permissions) -> bool:
        """Returns ``True`` if the permissions on self are a strict subset of those on other."""
        return self.is_subset(other) and self != other

    def is_strict_superset(self, other: Permissions) -> bool:
        """Returns ``True`` if the permissions on self are a strict superset of those on other."""
        return self.is_superset(other) and self != other

    # the parent uses `Self` for the `other` typehint but we use `Permissions` here for backwards compat.
    __le__ = is_subset  # type: ignore
    __ge__ = is_superset  # type: ignore
    __lt__ = is_strict_subset  # type: ignore
    __gt__ = is_strict_superset  # type: ignore

    @classmethod
    @cached_creation
    def none(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        permissions set to ``False``."""
        return cls(0)

    @classmethod
    @cached_creation
    def all(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        permissions set to ``True``.
        """
        return cls(**dict.fromkeys(cls.VALID_FLAGS.keys(), True))

    @classmethod
    @cached_creation
    def all_channel(cls) -> Self:
        """A :class:`Permissions` with all channel-specific permissions set to
        ``True`` and the guild-specific ones set to ``False``. The guild-specific
        permissions are currently:

        - :attr:`manage_emojis`
        - :attr:`view_audit_log`
        - :attr:`view_guild_insights`
        - :attr:`manage_guild`
        - :attr:`change_nickname`
        - :attr:`manage_nicknames`
        - :attr:`kick_members`
        - :attr:`ban_members`
        - :attr:`administrator`

        .. versionchanged:: 1.7
           Added :attr:`stream`, :attr:`priority_speaker` and :attr:`use_slash_commands` permissions.

        .. versionchanged:: 2.0
           Added :attr:`create_public_threads`, :attr:`create_private_threads`, :attr:`manage_threads`,
           :attr:`use_external_stickers`, :attr:`send_messages_in_threads` and
           :attr:`request_to_speak` permissions.

        .. versionchanged:: 2.3
            Added :attr:`use_embedded_activities` permission.
        """
        guild_specific_perms = {
            "administrator",
            "ban_members",
            "change_nickname",
            "kick_members",
            "manage_emojis",
            "manage_guild",
            "manage_nicknames",
            "moderate_members",
            "view_audit_log",
            "view_guild_insights",
        }
        instance = cls.all()
        instance.update(**dict.fromkeys(guild_specific_perms, False))
        return instance

    @classmethod
    @cached_creation
    def general(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "General" permissions from the official Discord UI set to ``True``.

        .. versionchanged:: 1.7
           Permission :attr:`read_messages` is now included in the general permissions, but
           permissions :attr:`administrator`, :attr:`create_instant_invite`, :attr:`kick_members`,
           :attr:`ban_members`, :attr:`change_nickname` and :attr:`manage_nicknames` are
           no longer part of the general permissions.
        """
        return cls(
            view_channel=True,
            manage_channels=True,
            manage_roles=True,
            manage_emojis_and_stickers=True,
            view_audit_log=True,
            view_guild_insights=True,
            manage_webhooks=True,
            manage_guild=True,
        )

    @classmethod
    @cached_creation
    def membership(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Membership" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7

        .. versionchanged:: 2.3
            Added :attr:`moderate_members` permission.
        """
        return cls(
            create_instant_invite=True,
            change_nickname=True,
            manage_nicknames=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
        )

    @classmethod
    @cached_creation
    def text(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Text" permissions from the official Discord UI set to ``True``.

        .. versionchanged:: 1.7
           Permission :attr:`read_messages` is no longer part of the text permissions.
           Added :attr:`use_slash_commands` permission.

        .. versionchanged:: 2.0
           Added :attr:`create_public_threads`, :attr:`create_private_threads`, :attr:`manage_threads`,
           :attr:`send_messages_in_threads` and :attr:`use_external_stickers` permissions.
        """
        return cls(
            send_messages=True,
            send_messages_in_threads=True,
            create_public_threads=True,
            create_private_threads=True,
            embed_links=True,
            attach_files=True,
            add_reactions=True,
            use_external_emojis=True,
            use_external_stickers=True,
            mention_everyone=True,
            manage_messages=True,
            manage_threads=True,
            read_message_history=True,
            send_tts_messages=True,
            use_slash_commands=True,
        )

    @classmethod
    @cached_creation
    def voice(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Voice" permissions from the official Discord UI set to ``True``.

        .. versionchanged:: 2.3
            Added :attr:`use_embedded_activities` permission.
        """
        return cls(
            connect=True,
            speak=True,
            stream=True,
            use_embedded_activities=True,
            use_voice_activation=True,
            priority_speaker=True,
            mute_members=True,
            deafen_members=True,
            move_members=True,
        )

    @classmethod
    @cached_creation
    def stage(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Stage Channel" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(
            request_to_speak=True,
        )

    @classmethod
    @cached_creation
    def stage_moderator(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Stage Moderator" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(
            manage_channels=True,
            mute_members=True,
            move_members=True,
        )

    @classmethod
    @cached_creation
    def events(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Events" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 2.4
        """
        return cls(
            manage_events=True,
        )

    @classmethod
    @cached_creation
    def advanced(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Advanced" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(
            administrator=True,
        )

    @classmethod
    @cached_creation
    def private_channel(cls) -> Self:
        """A factory method that creates a :class:`Permissions` with the
        best representation of a PrivateChannel's permissions.

        This exists to maintain compatibility with other channel types.

        This is equivalent to :meth:`Permissions.text` with :attr:`~Permissions.view_channel` with the following set to False:

        - :attr:`~Permissions.send_tts_messages`: You cannot send TTS messages in a DM.
        - :attr:`~Permissions.manage_messages`: You cannot delete others messages in a DM.
        - :attr:`~Permissions.manage_threads`: You cannot manage threads in a DM.
        - :attr:`~Permissions.send_messages_in_threads`: You cannot make threads in a DM.
        - :attr:`~Permissions.create_public_threads`: You cannot make public threads in a DM.
        - :attr:`~Permissions.create_private_threads`: You cannot make private threads in a DM.

        .. versionadded:: 2.4
        """
        base = cls.text()
        base.read_messages = True
        base.send_tts_messages = False
        base.manage_messages = False
        base.manage_threads = False
        base.send_messages_in_threads = False
        base.create_public_threads = False
        base.create_private_threads = False
        return base

    @overload
    @_generated
    def update(
        self,
        *,
        add_reactions: bool = ...,
        administrator: bool = ...,
        attach_files: bool = ...,
        ban_members: bool = ...,
        change_nickname: bool = ...,
        connect: bool = ...,
        create_forum_threads: bool = ...,
        create_instant_invite: bool = ...,
        create_private_threads: bool = ...,
        create_public_threads: bool = ...,
        deafen_members: bool = ...,
        embed_links: bool = ...,
        external_emojis: bool = ...,
        external_stickers: bool = ...,
        kick_members: bool = ...,
        manage_channels: bool = ...,
        manage_emojis: bool = ...,
        manage_emojis_and_stickers: bool = ...,
        manage_events: bool = ...,
        manage_guild: bool = ...,
        manage_messages: bool = ...,
        manage_nicknames: bool = ...,
        manage_permissions: bool = ...,
        manage_roles: bool = ...,
        manage_threads: bool = ...,
        manage_webhooks: bool = ...,
        mention_everyone: bool = ...,
        moderate_members: bool = ...,
        move_members: bool = ...,
        mute_members: bool = ...,
        priority_speaker: bool = ...,
        read_message_history: bool = ...,
        read_messages: bool = ...,
        request_to_speak: bool = ...,
        send_messages: bool = ...,
        send_messages_in_threads: bool = ...,
        send_tts_messages: bool = ...,
        speak: bool = ...,
        start_embedded_activities: bool = ...,
        stream: bool = ...,
        use_application_commands: bool = ...,
        use_embedded_activities: bool = ...,
        use_external_emojis: bool = ...,
        use_external_stickers: bool = ...,
        use_slash_commands: bool = ...,
        use_voice_activation: bool = ...,
        view_audit_log: bool = ...,
        view_channel: bool = ...,
        view_guild_insights: bool = ...,
    ) -> None:
        ...

    @overload
    @_generated
    def update(
        self,
    ) -> None:
        ...

    @_overload_with_permissions
    def update(self, **kwargs: bool) -> None:
        """
        Bulk updates this permission object.

        Allows you to set multiple attributes by using keyword
        arguments. The names must be equivalent to the properties
        listed. Extraneous key/value pairs will be silently ignored.

        Arguments are applied in order, similar to the constructor.

        Parameters
        ----------
        **kwargs
            A list of key/value pairs to bulk update permissions with.
        """
        for key, value in kwargs.items():
            if key in self.VALID_FLAGS:
                setattr(self, key, value)

    def handle_overwrite(self, allow: int, deny: int) -> None:
        # Basically this is what's happening here.
        # We have an original bit array, e.g. 1010
        # Then we have another bit array that is 'denied', e.g. 1111
        # And then we have the last one which is 'allowed', e.g. 0101
        # We want original OP denied to end up resulting in
        # whatever is in denied to be set to 0.
        # So 1010 OP 1111 -> 0000
        # Then we take this value and look at the allowed values.
        # And whatever is allowed is set to 1.
        # So 0000 OP2 0101 -> 0101
        # The OP is base  & ~denied.
        # The OP2 is base | allowed.
        self.value = (self.value & ~deny) | allow

    @flag_value
    def create_instant_invite(self) -> int:
        """:class:`bool`: Returns ``True`` if the user can create instant invites."""
        return 1 << 0

    @flag_value
    def kick_members(self) -> int:
        """:class:`bool`: Returns ``True`` if the user can kick users from the guild."""
        return 1 << 1

    @flag_value
    def ban_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can ban users from the guild."""
        return 1 << 2

    @flag_value
    def administrator(self) -> int:
        """:class:`bool`: Returns ``True`` if a user is an administrator. This role overrides all other permissions.

        This also bypasses all channel-specific overrides.
        """
        return 1 << 3

    @flag_value
    def manage_channels(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can edit, delete, or create channels in the guild.

        This also corresponds to the "Manage Channel" channel-specific override."""
        return 1 << 4

    @flag_value
    def manage_guild(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can edit guild properties."""
        return 1 << 5

    @flag_value
    def add_reactions(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can add reactions to messages."""
        return 1 << 6

    @flag_value
    def view_audit_log(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view the guild's audit log."""
        return 1 << 7

    @flag_value
    def priority_speaker(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can be more easily heard while talking."""
        return 1 << 8

    @flag_value
    def stream(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can stream in a voice channel."""
        return 1 << 9

    @flag_value
    def view_channel(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view all or specific channels.

        .. versionadded:: 1.3

        .. versionchanged:: 2.4
            :attr:`~Permissions.read_messages` is now an alias of :attr:`~Permissions.view_channel`.
        """
        return 1 << 10

    @make_permission_alias("view_channel")
    def read_messages(self) -> int:
        """:class:`bool`: An alias for :attr:`view_channel`."""
        return 1 << 10

    @flag_value
    def send_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send messages from all or specific text channels
        and create threads in forum channels."""
        return 1 << 11

    @make_permission_alias("send_messages")
    def create_forum_threads(self) -> int:
        """:class:`bool`: An alias for :attr:`send_messages`.

        .. versionadded:: 2.5
        """
        return 1 << 11

    @flag_value
    def send_tts_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send TTS messages from all or specific text channels."""
        return 1 << 12

    @flag_value
    def manage_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can delete or pin messages in a text channel.

        .. note::

            Note that there are currently no ways to edit other people's messages.
        """
        return 1 << 13

    @flag_value
    def embed_links(self) -> int:
        """:class:`bool`: Returns ``True`` if a user's messages will automatically be embedded by Discord."""
        return 1 << 14

    @flag_value
    def attach_files(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send files in their messages."""
        return 1 << 15

    @flag_value
    def read_message_history(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can read a text channel's previous messages."""
        return 1 << 16

    @flag_value
    def mention_everyone(self) -> int:
        """:class:`bool`: Returns ``True`` if a user's @everyone or @here will mention everyone in the text channel."""
        return 1 << 17

    @flag_value
    def external_emojis(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use emojis from other guilds."""
        return 1 << 18

    @make_permission_alias("external_emojis")
    def use_external_emojis(self) -> int:
        """:class:`bool`: An alias for :attr:`external_emojis`.

        .. versionadded:: 1.3
        """
        return 1 << 18

    @flag_value
    def view_guild_insights(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view the guild's insights.

        .. versionadded:: 1.3
        """
        return 1 << 19

    @flag_value
    def connect(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can connect to a voice channel."""
        return 1 << 20

    @flag_value
    def speak(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can speak in a voice channel."""
        return 1 << 21

    @flag_value
    def mute_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can mute other users."""
        return 1 << 22

    @flag_value
    def deafen_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can deafen other users."""
        return 1 << 23

    @flag_value
    def move_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can move users between other voice channels."""
        return 1 << 24

    @flag_value
    def use_voice_activation(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use voice activation in voice channels."""
        return 1 << 25

    @flag_value
    def change_nickname(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can change their nickname in the guild."""
        return 1 << 26

    @flag_value
    def manage_nicknames(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can change other user's nickname in the guild."""
        return 1 << 27

    @flag_value
    def manage_roles(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create or edit roles less than their role's position.

        This also corresponds to the "Manage Permissions" channel-specific override.
        """
        return 1 << 28

    @make_permission_alias("manage_roles")
    def manage_permissions(self) -> int:
        """:class:`bool`: An alias for :attr:`manage_roles`.

        .. versionadded:: 1.3
        """
        return 1 << 28

    @flag_value
    def manage_webhooks(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create, edit, or delete webhooks."""
        return 1 << 29

    @flag_value
    def manage_emojis(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create, edit, or delete emojis."""
        return 1 << 30

    @make_permission_alias("manage_emojis")
    def manage_emojis_and_stickers(self) -> int:
        """:class:`bool`: An alias for :attr:`manage_emojis`.

        .. versionadded:: 2.0
        """
        return 1 << 30

    @flag_value
    def use_application_commands(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use application commands.

        .. versionadded:: 2.6
        """
        return 1 << 31

    @make_permission_alias("use_application_commands")
    def use_slash_commands(self) -> int:
        """:class:`bool`: An alias for :attr:`use_application_commands`.

        .. versionadded:: 1.7

        .. versionchanged:: 2.6
            Became an alias for :attr:`use_application_commands`.
        """
        return 1 << 31

    @flag_value
    def request_to_speak(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can request to speak in a stage channel.

        .. versionadded:: 1.7
        """
        return 1 << 32

    @flag_value
    def manage_events(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can manage guild events.

        .. versionadded:: 2.0
        """
        return 1 << 33

    @flag_value
    def manage_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can manage threads.

        .. versionadded:: 2.0
        """
        return 1 << 34

    @flag_value
    def create_public_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create public threads.

        .. versionadded:: 2.0
        """
        return 1 << 35

    @flag_value
    def create_private_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create private threads.

        .. versionadded:: 2.0
        """
        return 1 << 36

    @flag_value
    def external_stickers(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use stickers from other guilds.

        .. versionadded:: 2.0
        """
        return 1 << 37

    @make_permission_alias("external_stickers")
    def use_external_stickers(self) -> int:
        """:class:`bool`: An alias for :attr:`external_stickers`.

        .. versionadded:: 2.0
        """
        return 1 << 37

    @flag_value
    def send_messages_in_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send messages in threads.

        .. versionadded:: 2.0
        """
        return 1 << 38

    @flag_value
    def use_embedded_activities(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use activities (applications
        with the :attr:`~ApplicationFlags.embedded` flag) in a voice channel.

        .. versionadded:: 2.6
        """
        return 1 << 39

    @make_permission_alias("use_embedded_activities")
    def start_embedded_activities(self) -> int:
        """:class:`bool`: An alias for :attr:`use_embedded_activities`.

        .. versionadded:: 2.3

        .. versionchanged:: 2.6
            Became an alias for :attr:`use_embedded_activities`.
        """
        return 1 << 39

    @flag_value
    def moderate_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can perform limited moderation actions (timeout).

        .. versionadded:: 2.3
        """
        return 1 << 40


def _augment_from_permissions(cls):
    cls.VALID_NAMES = set(Permissions.VALID_FLAGS)
    aliases = set()

    # make descriptors for all the valid names and aliases
    for name, value in Permissions.__dict__.items():
        if isinstance(value, permission_alias):
            key = value.alias
            aliases.add(name)
        elif isinstance(value, flag_value):
            key = name
        else:
            continue

        # god bless Python
        def getter(self, x=key):
            return self._values.get(x)

        def setter(self, value, x=key):
            self._set(x, value)

        prop = property(getter, setter)
        setattr(cls, name, prop)

    cls.PURE_FLAGS = cls.VALID_NAMES - aliases
    return cls


@_augment_from_permissions
class PermissionOverwrite:
    """
    A type that is used to represent a channel specific permission.

    Unlike a regular :class:`Permissions`\\, the default value of a
    permission is equivalent to ``None`` and not ``False``. Setting
    a value to ``False`` is **explicitly** denying that permission,
    while setting a value to ``True`` is **explicitly** allowing
    that permission.

    The values supported by this are the same as :class:`Permissions`
    with the added possibility of it being set to ``None``.

    .. container:: operations

        .. describe:: x == y

            Checks if two overwrites are equal.
        .. describe:: x != y

            Checks if two overwrites are not equal.
        .. describe:: iter(x)

           Returns an iterator of ``(perm, value)`` pairs. This allows it
           to be, for example, constructed as a dict or a list of pairs.
           Note that aliases are not shown.

    Parameters
    ----------
    **kwargs
        Set the value of permissions by their name.
    """

    __slots__ = ("_values",)

    # n. b. this typechecking block must be first and seperate from the secondary one, due to codemodding
    if TYPE_CHECKING:
        add_reactions: Optional[bool]
        administrator: Optional[bool]
        attach_files: Optional[bool]
        ban_members: Optional[bool]
        change_nickname: Optional[bool]
        connect: Optional[bool]
        create_forum_threads: Optional[bool]
        create_instant_invite: Optional[bool]
        create_private_threads: Optional[bool]
        create_public_threads: Optional[bool]
        deafen_members: Optional[bool]
        embed_links: Optional[bool]
        external_emojis: Optional[bool]
        external_stickers: Optional[bool]
        kick_members: Optional[bool]
        manage_channels: Optional[bool]
        manage_emojis: Optional[bool]
        manage_emojis_and_stickers: Optional[bool]
        manage_events: Optional[bool]
        manage_guild: Optional[bool]
        manage_messages: Optional[bool]
        manage_nicknames: Optional[bool]
        manage_permissions: Optional[bool]
        manage_roles: Optional[bool]
        manage_threads: Optional[bool]
        manage_webhooks: Optional[bool]
        mention_everyone: Optional[bool]
        moderate_members: Optional[bool]
        move_members: Optional[bool]
        mute_members: Optional[bool]
        priority_speaker: Optional[bool]
        read_message_history: Optional[bool]
        read_messages: Optional[bool]
        request_to_speak: Optional[bool]
        send_messages: Optional[bool]
        send_messages_in_threads: Optional[bool]
        send_tts_messages: Optional[bool]
        speak: Optional[bool]
        start_embedded_activities: Optional[bool]
        stream: Optional[bool]
        use_application_commands: Optional[bool]
        use_embedded_activities: Optional[bool]
        use_external_emojis: Optional[bool]
        use_external_stickers: Optional[bool]
        use_slash_commands: Optional[bool]
        use_voice_activation: Optional[bool]
        view_audit_log: Optional[bool]
        view_channel: Optional[bool]
        view_guild_insights: Optional[bool]

    if TYPE_CHECKING:
        VALID_NAMES: ClassVar[Set[str]]
        PURE_FLAGS: ClassVar[Set[str]]

    @overload
    @_generated
    def __init__(
        self,
        *,
        add_reactions: Optional[bool] = ...,
        administrator: Optional[bool] = ...,
        attach_files: Optional[bool] = ...,
        ban_members: Optional[bool] = ...,
        change_nickname: Optional[bool] = ...,
        connect: Optional[bool] = ...,
        create_forum_threads: Optional[bool] = ...,
        create_instant_invite: Optional[bool] = ...,
        create_private_threads: Optional[bool] = ...,
        create_public_threads: Optional[bool] = ...,
        deafen_members: Optional[bool] = ...,
        embed_links: Optional[bool] = ...,
        external_emojis: Optional[bool] = ...,
        external_stickers: Optional[bool] = ...,
        kick_members: Optional[bool] = ...,
        manage_channels: Optional[bool] = ...,
        manage_emojis: Optional[bool] = ...,
        manage_emojis_and_stickers: Optional[bool] = ...,
        manage_events: Optional[bool] = ...,
        manage_guild: Optional[bool] = ...,
        manage_messages: Optional[bool] = ...,
        manage_nicknames: Optional[bool] = ...,
        manage_permissions: Optional[bool] = ...,
        manage_roles: Optional[bool] = ...,
        manage_threads: Optional[bool] = ...,
        manage_webhooks: Optional[bool] = ...,
        mention_everyone: Optional[bool] = ...,
        moderate_members: Optional[bool] = ...,
        move_members: Optional[bool] = ...,
        mute_members: Optional[bool] = ...,
        priority_speaker: Optional[bool] = ...,
        read_message_history: Optional[bool] = ...,
        read_messages: Optional[bool] = ...,
        request_to_speak: Optional[bool] = ...,
        send_messages: Optional[bool] = ...,
        send_messages_in_threads: Optional[bool] = ...,
        send_tts_messages: Optional[bool] = ...,
        speak: Optional[bool] = ...,
        start_embedded_activities: Optional[bool] = ...,
        stream: Optional[bool] = ...,
        use_application_commands: Optional[bool] = ...,
        use_embedded_activities: Optional[bool] = ...,
        use_external_emojis: Optional[bool] = ...,
        use_external_stickers: Optional[bool] = ...,
        use_slash_commands: Optional[bool] = ...,
        use_voice_activation: Optional[bool] = ...,
        view_audit_log: Optional[bool] = ...,
        view_channel: Optional[bool] = ...,
        view_guild_insights: Optional[bool] = ...,
    ):
        ...

    @overload
    @_generated
    def __init__(
        self,
    ):
        ...

    @_overload_with_permissions
    def __init__(self, **kwargs: Optional[bool]):
        self._values: Dict[str, Optional[bool]] = {}

        for key, value in kwargs.items():
            if key not in self.VALID_NAMES:
                raise ValueError(f"{key!r} is not a valid permission name.")

            setattr(self, key, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, PermissionOverwrite) and self._values == other._values

    def _set(self, key: str, value: Optional[bool]) -> None:
        if value not in (True, None, False):
            raise TypeError(f"Expected bool or NoneType, received {value.__class__.__name__}")

        if value is None:
            self._values.pop(key, None)
        else:
            self._values[key] = value

    def pair(self) -> Tuple[Permissions, Permissions]:
        """Tuple[:class:`Permissions`, :class:`Permissions`]: Returns the (allow, deny) pair from this overwrite."""

        allow = Permissions.none()
        deny = Permissions.none()

        for key, value in self._values.items():
            if value is True:
                setattr(allow, key, True)
            elif value is False:
                setattr(deny, key, True)

        return allow, deny

    @classmethod
    def from_pair(cls, allow: Permissions, deny: Permissions) -> Self:
        """Creates an overwrite from an allow/deny pair of :class:`Permissions`."""
        ret = cls()
        for key, value in allow:
            if value is True:
                setattr(ret, key, True)

        for key, value in deny:
            if value is True:
                setattr(ret, key, False)

        return ret

    def is_empty(self) -> bool:
        """Checks if the permission overwrite is currently empty.

        An empty permission overwrite is one that has no overwrites set
        to ``True`` or ``False``.

        Returns
        -------
        :class:`bool`
            Indicates if the overwrite is empty.
        """
        return len(self._values) == 0

    @overload
    @_generated
    def update(
        self,
        *,
        add_reactions: Optional[bool] = ...,
        administrator: Optional[bool] = ...,
        attach_files: Optional[bool] = ...,
        ban_members: Optional[bool] = ...,
        change_nickname: Optional[bool] = ...,
        connect: Optional[bool] = ...,
        create_forum_threads: Optional[bool] = ...,
        create_instant_invite: Optional[bool] = ...,
        create_private_threads: Optional[bool] = ...,
        create_public_threads: Optional[bool] = ...,
        deafen_members: Optional[bool] = ...,
        embed_links: Optional[bool] = ...,
        external_emojis: Optional[bool] = ...,
        external_stickers: Optional[bool] = ...,
        kick_members: Optional[bool] = ...,
        manage_channels: Optional[bool] = ...,
        manage_emojis: Optional[bool] = ...,
        manage_emojis_and_stickers: Optional[bool] = ...,
        manage_events: Optional[bool] = ...,
        manage_guild: Optional[bool] = ...,
        manage_messages: Optional[bool] = ...,
        manage_nicknames: Optional[bool] = ...,
        manage_permissions: Optional[bool] = ...,
        manage_roles: Optional[bool] = ...,
        manage_threads: Optional[bool] = ...,
        manage_webhooks: Optional[bool] = ...,
        mention_everyone: Optional[bool] = ...,
        moderate_members: Optional[bool] = ...,
        move_members: Optional[bool] = ...,
        mute_members: Optional[bool] = ...,
        priority_speaker: Optional[bool] = ...,
        read_message_history: Optional[bool] = ...,
        read_messages: Optional[bool] = ...,
        request_to_speak: Optional[bool] = ...,
        send_messages: Optional[bool] = ...,
        send_messages_in_threads: Optional[bool] = ...,
        send_tts_messages: Optional[bool] = ...,
        speak: Optional[bool] = ...,
        start_embedded_activities: Optional[bool] = ...,
        stream: Optional[bool] = ...,
        use_application_commands: Optional[bool] = ...,
        use_embedded_activities: Optional[bool] = ...,
        use_external_emojis: Optional[bool] = ...,
        use_external_stickers: Optional[bool] = ...,
        use_slash_commands: Optional[bool] = ...,
        use_voice_activation: Optional[bool] = ...,
        view_audit_log: Optional[bool] = ...,
        view_channel: Optional[bool] = ...,
        view_guild_insights: Optional[bool] = ...,
    ) -> None:
        ...

    @overload
    @_generated
    def update(
        self,
    ) -> None:
        ...

    @_overload_with_permissions
    def update(self, **kwargs: Optional[bool]) -> None:
        """
        Bulk updates this permission overwrite object.

        Allows you to set multiple attributes by using keyword
        arguments. The names must be equivalent to the properties
        listed. Extraneous key/value pairs will be silently ignored.

        Parameters
        ----------
        **kwargs
            A list of key/value pairs to bulk update with.
        """
        for key, value in kwargs.items():
            if key not in self.VALID_NAMES:
                continue

            setattr(self, key, value)

    def __iter__(self) -> Iterator[Tuple[str, Optional[bool]]]:
        for key in self.PURE_FLAGS:
            yield key, self._values.get(key)
