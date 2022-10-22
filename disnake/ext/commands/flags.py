# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn, overload

from disnake.flags import BaseFlags, alias_flag_value, all_flags_value, flag_value
from disnake.utils import _generated

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("CommandSyncFlags",)


class CommandSyncFlags(BaseFlags):
    """Controls the library's application command syncing policy.

    This allows for finer grained control over what commands are synced automatically and in what cases.

    To construct an object you can pass keyword arguments denoting the flags
    to enable or disable.

    The default value is all flags enabled.

    .. versionadded:: 2.7

    .. container:: operations

        .. describe:: x == y

            Checks if two CommandSyncFlags instances are equal.
        .. describe:: x != y

            Checks if two CommandSyncFlags instances are not equal.
        .. describe:: x <= y

            Checks if an CommandSyncFlags instance is a subset of another CommandSyncFlags instance.
        .. describe:: x >= y

            Checks if an CommandSyncFlags instance is a superset of another CommandSyncFlags instance.
        .. describe:: x < y

            Checks if an CommandSyncFlags instance is a strict subset of another CommandSyncFlags instance.
        .. describe:: x > y

            Checks if an CommandSyncFlags instance is a strict superset of another CommandSyncFlags instance.
        .. describe:: x | y, x |= y

            Returns a new CommandSyncFlags instance with all enabled flags from both x and y.
            (Using ``|=`` will update in place).
        .. describe:: x & y, x &= y

            Returns a new CommandSyncFlags instance with only flags enabled on both x and y.
            (Using ``&=`` will update in place).
        .. describe:: x ^ y, x ^= y

            Returns a new CommandSyncFlags instance with only flags enabled on one of x or y, but not both.
            (Using ``^=`` will update in place).
        .. describe:: ~x

            Returns a new CommandSyncFlags instance with all flags from x inverted.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.


        Additionally supported are a few operations on class attributes.

        .. describe:: CommandSyncFlags.y | CommandSyncFlags.z, CommandSyncFlags(y=True) | CommandSyncFlags.z

            Returns a CommandSyncFlags instance with all provided flags enabled.

        .. describe:: ~CommandSyncFlags.y

            Returns a CommandSyncFlags instance with all flags except ``y`` inverted from their default value.

    Attributes
    ----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    @overload
    @_generated
    def __init__(
        self,
        *,
        allow_command_deletion: bool = ...,
        on_cog_unload: bool = ...,
        sync_commands: bool = ...,
        sync_commands_debug: bool = ...,
        sync_global_commands: bool = ...,
        sync_guild_commands: bool = ...,
    ):
        ...

    @overload
    @_generated
    def __init__(self: NoReturn):
        ...

    def __init__(self, **kwargs: bool):
        self.value = all_flags_value(self.VALID_FLAGS)
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def all(cls) -> Self:
        """A factory method that creates a :class:`CommandSyncFlags` with everything enabled."""
        self = cls.__new__(cls)
        self.value = all_flags_value(cls.VALID_FLAGS)
        return self

    @classmethod
    def none(cls) -> Self:
        """A factory method that creates a :class:`CommandSyncFlags` with everything disabled."""
        self = cls.__new__(cls)
        self.value = self.DEFAULT_VALUE
        return self

    @classmethod
    def default(cls) -> Self:
        """A factory method that creates a :class:`CommandSyncFlags` with the default settings."""
        instance = cls.all()
        instance.sync_commands_debug = False
        return instance

    @property
    def _sync_enabled(self):
        return self.sync_global_commands or self.sync_guild_commands

    @alias_flag_value
    def sync_commands(self):
        """:class:`bool`: Whether to sync app commands at all."""
        return 1 << 5 | 1 << 6

    @flag_value
    def sync_commands_debug(self):
        """:class:`bool`: Whether or not to show app command sync debug messages"""
        return 1 << 1

    @flag_value
    def on_cog_unload(self):
        """:class:`bool`: Whether or not to sync app commands on cog unload or reload."""
        return 1 << 2

    @flag_value
    def allow_command_deletion(self):
        """:class:`bool`: Whether to allow commands to be deleted by automatic command sync."""
        return 1 << 3

    @flag_value
    def sync_global_commands(self):
        """:class:`bool`: Whether to sync global commands."""
        return 1 << 5

    @flag_value
    def sync_guild_commands(self):
        """:class:`bool`: Whether to sync per-guild commands."""
        return 1 << 6
