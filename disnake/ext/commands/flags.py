"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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

from typing import TYPE_CHECKING

from disnake.flags import BaseFlags, alias_flag_value, all_flags_value, fill_with_flags, flag_value

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("ApplicationCommandSyncFlags",)


@fill_with_flags()
class ApplicationCommandSyncFlags(BaseFlags):
    """Controls the library's application command syncing policy.

    This allows for finer grained control over what commands are synced automatically and in what cases.

    To construct an object you can pass keyword arguments denoting the flags
    to enable or disable.

    The default value is all flags enabled.

    .. versionadded:: 2.6

    .. container:: operations

        .. describe:: x == y

            Checks if two ApplicationCommandSyncFlags instances are equal.
        .. describe:: x != y

            Checks if two ApplicationCommandSyncFlags instances are not equal.
        .. describe:: x <= y

            Checks if an ApplicationCommandSyncFlags instance is a subset of another ApplicationCommandSyncFlags instance.
        .. describe:: x >= y

            Checks if an ApplicationCommandSyncFlags instance is a superset of another ApplicationCommandSyncFlags instance.
        .. describe:: x < y

            Checks if an ApplicationCommandSyncFlags instance is a strict subset of another ApplicationCommandSyncFlags instance.
        .. describe:: x > y

            Checks if an ApplicationCommandSyncFlags instance is a strict superset of another ApplicationCommandSyncFlags instance.
        .. describe:: x | y, x |= y

            Returns a new ApplicationCommandSyncFlags instance with all enabled flags from both x and y.
            (Using ``|=`` will update in place).
        .. describe:: x & y, x &= y

            Returns a new ApplicationCommandSyncFlags instance with only flags enabled on both x and y.
            (Using ``&=`` will update in place).
        .. describe:: x ^ y, x ^= y

            Returns a new ApplicationCommandSyncFlags instance with only flags enabled on one of x or y, but not both.
            (Using ``^=`` will update in place).
        .. describe:: ~x

            Returns a new ApplicationCommandSyncFlags instance with all flags from x inverted.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.


        Additionally supported are a few operations on class attributes.

        .. describe:: ApplicationCommandSyncFlags.y | ApplicationCommandSyncFlags.z, ApplicationCommandSyncFlags(y=True) | ApplicationCommandSyncFlags.z

            Returns a ApplicationCommandSyncFlags instance with all provided flags enabled.

        .. describe:: ~ApplicationCommandSyncFlags.y

            Returns a ApplicationCommandSyncFlags instance with all flags except ``y`` inverted from their default value.

    .. versionadded:: 2.6
    Attributes
    ----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    def __init__(self, **kwargs: bool):
        self.value = all_flags_value(self.VALID_FLAGS)
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def all(cls) -> Self:
        """A factory method that creates a :class:`ApplicationCommandSyncFlags` with everything enabled."""
        self = cls.__new__(cls)
        self.value = all_flags_value(cls.VALID_FLAGS)
        return self

    @classmethod
    def none(cls) -> Self:
        """A factory method that creates a :class:`ApplicationCommandSyncFlags` with everything disabled."""
        self = cls.__new__(cls)
        self.value = self.DEFAULT_VALUE
        return self

    @classmethod
    def default(cls) -> Self:
        """A factory method that creates a :class:`ApplicationCommandSyncFlags` with the default settings."""
        instance = cls.all()
        instance.sync_commands_debug = False
        return instance

    @alias_flag_value
    def sync_commands(self):
        """:class:`bool`: Whether to sync app commands at all."""
        return 1 << 5 | 1 << 6

    @flag_value
    def sync_commands_debug(self):
        """:class:`bool`: Whether or not to show app command sync debug messages"""
        return 1 << 1

    @alias_flag_value
    def on_cog_actions(self):
        """:class:`bool`: Whether or not to sync app commands on cog load, unload, or reload."""
        return 1 << 2 | 1 << 4

    @flag_value
    def on_cog_unload(self):
        """:class:`bool`: Whether or not to sync app commands on cog unload or reload."""
        return 1 << 2

    @flag_value
    def allow_command_deletion(self):
        return 1 << 3

    @flag_value
    def global_commands(self):
        return 1 << 5

    @flag_value
    def guild_commands(self):
        return 1 << 6
