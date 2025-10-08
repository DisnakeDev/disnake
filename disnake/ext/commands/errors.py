# SPDX-License-Identifier: MIT
# License header (MIT License)

from __future__ import annotations  # Enables forward references in type hints (Python <3.10)

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Union

# Importing base exception classes and utility functions from disnake
from disnake.errors import ClientException, DiscordException
from disnake.utils import humanize_list  # Converts lists to human-readable strings

# TYPE_CHECKING block prevents circular imports at runtime
if TYPE_CHECKING:
    from inspect import Parameter
    from disnake.abc import GuildChannel
    from disnake.threads import Thread
    from disnake.types.snowflake import Snowflake, SnowflakeList

    from .context import AnyContext
    from .cooldowns import BucketType, Cooldown
    from .flag_converter import Flag

# __all__ defines the public API of this module — which exceptions can be imported directly
__all__ = (
    "CommandError",
    "MissingRequiredArgument",
    "BadArgument",
    "PrivateMessageOnly",
    "NoPrivateMessage",
    "CheckFailure",
    "CheckAnyFailure",
    "CommandNotFound",
    "DisabledCommand",
    "CommandInvokeError",
    "TooManyArguments",
    "UserInputError",
    "CommandOnCooldown",
    "MaxConcurrencyReached",
    "NotOwner",
    "MessageNotFound",
    "ObjectNotFound",
    "MemberNotFound",
    "GuildNotFound",
    "UserNotFound",
    "ChannelNotFound",
    "ThreadNotFound",
    "ChannelNotReadable",
    "BadColourArgument",
    "BadColorArgument",
    "RoleNotFound",
    "BadInviteArgument",
    "EmojiNotFound",
    "GuildStickerNotFound",
    "GuildSoundboardSoundNotFound",
    "GuildScheduledEventNotFound",
    "PartialEmojiConversionFailure",
    "BadBoolArgument",
    "LargeIntConversionFailure",
    "MissingRole",
    "BotMissingRole",
    "MissingAnyRole",
    "BotMissingAnyRole",
    "MissingPermissions",
    "BotMissingPermissions",
    "NSFWChannelRequired",
    "ConversionError",
    "BadUnionArgument",
    "BadLiteralArgument",
    "ArgumentParsingError",
    "UnexpectedQuoteError",
    "InvalidEndOfQuotedStringError",
    "ExpectedClosingQuoteError",
    "ExtensionError",
    "ExtensionAlreadyLoaded",
    "ExtensionNotLoaded",
    "NoEntryPointError",
    "ExtensionFailed",
    "ExtensionNotFound",
    "CommandRegistrationError",
    "FlagError",
    "BadFlagArgument",
    "MissingFlagArgument",
    "TooManyFlags",
    "MissingRequiredFlag",
)

# --------------------------------------------------------------------------
# Core Command Error Hierarchy
# --------------------------------------------------------------------------

class CommandError(DiscordException):
    """Base exception for all command-related errors.

    - Inherits from disnake.DiscordException.
    - Caught by Bot's event handler `on_command_error`.
    """

    def __init__(self, message: Optional[str] = None, *args: Any) -> None:
        if message is not None:
            # Sanitizes mentions to prevent accidental @everyone/@here pings
            m = message.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
            super().__init__(m, *args)
        else:
            super().__init__(*args)


# Raised when a Converter fails during argument conversion
class ConversionError(CommandError):
    """Raised when a Converter class raises a non-CommandError exception."""

    def __init__(self, converter: Any, original: Exception) -> None:
        self.converter = converter
        self.original = original


class UserInputError(CommandError):
    """Base class for user-input-related errors."""
    pass


class CommandNotFound(CommandError):
    """Raised when a command name doesn’t match any registered command."""
    pass


class MissingRequiredArgument(UserInputError):
    """Raised when a required command argument is missing."""

    def __init__(self, param: Parameter) -> None:
        self.param = param
        super().__init__(f"{param.name} is a required argument that is missing.")


class TooManyArguments(UserInputError):
    """Raised when too many arguments are passed to a command."""
    pass


class BadArgument(UserInputError):
    """Raised when an argument fails conversion or parsing."""
    pass


# --------------------------------------------------------------------------
# Permission and Check Failures
# --------------------------------------------------------------------------

class CheckFailure(CommandError):
    """Raised when a command’s check predicate fails."""
    pass


class CheckAnyFailure(CheckFailure):
    """Raised when all checks in a `check_any()` fail."""

    def __init__(self, checks: List[CheckFailure], errors: List[Callable[[AnyContext], bool]]) -> None:
        self.checks = checks
        self.errors = errors
        super().__init__("You do not have permission to run this command.")


class PrivateMessageOnly(CheckFailure):
    """Raised when a command can only be used in private messages."""

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "This command can only be used in private messages.")


class NoPrivateMessage(CheckFailure):
    """Raised when a command cannot be used in DMs."""

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "This command cannot be used in private messages.")


class NotOwner(CheckFailure):
    """Raised when a non-owner user tries to run an owner-only command."""
    pass


# --------------------------------------------------------------------------
# "Not Found" and Conversion Exceptions
# --------------------------------------------------------------------------

class ObjectNotFound(BadArgument):
    """Raised when a provided ID or mention is invalid."""
    def __init__(self, argument: str) -> None:
        self.argument = argument
        super().__init__(f"{argument!r} does not follow a valid ID or mention format.")


# The next classes are similar—each indicates that a specific resource could not be found.
class MemberNotFound(BadArgument): ...
class GuildNotFound(BadArgument): ...
class UserNotFound(BadArgument): ...
class MessageNotFound(BadArgument): ...
class ChannelNotFound(BadArgument): ...
class ThreadNotFound(BadArgument): ...
class RoleNotFound(BadArgument): ...
class EmojiNotFound(BadArgument): ...
class GuildStickerNotFound(BadArgument): ...
class GuildSoundboardSoundNotFound(BadArgument): ...
class GuildScheduledEventNotFound(BadArgument): ...

# These override __init__ for a specific error message in each case.
# (See your original code for their details.)

# --------------------------------------------------------------------------
# Command Invocation and Runtime Errors
# --------------------------------------------------------------------------

class DisabledCommand(CommandError):
    """Raised when a command is disabled."""
    pass


class CommandInvokeError(CommandError):
    """Raised when the command itself raises an unhandled exception."""

    def __init__(self, e: Exception) -> None:
        self.original = e
        super().__init__(f"Command raised an exception: {e.__class__.__name__}: {e}")


class CommandOnCooldown(CommandError):
    """Raised when a command is on cooldown (rate-limited)."""

    def __init__(self, cooldown, retry_after, type):
        self.cooldown = cooldown
        self.retry_after = retry_after
        self.type = type
        super().__init__(f"You are on cooldown. Try again in {retry_after:.2f}s")


class MaxConcurrencyReached(CommandError):
    """Raised when a command exceeds its maximum concurrent uses."""

    def __init__(self, number: int, per):
        self.number = number
        self.per = per
        name = per.name
        suffix = f"per {name}" if name != "default" else "globally"
        fmt = f"{number} times {suffix}" if number > 1 else f"{number} time {suffix}"
        super().__init__(
            f"Too many people are using this command. It can only be used {fmt} concurrently."
        )

# --------------------------------------------------------------------------
# Role and Permission Related Errors
# --------------------------------------------------------------------------

class MissingRole(CheckFailure): ...
class BotMissingRole(CheckFailure): ...
class MissingAnyRole(CheckFailure): ...
class BotMissingAnyRole(CheckFailure): ...
class MissingPermissions(CheckFailure): ...
class BotMissingPermissions(CheckFailure): ...
class NSFWChannelRequired(CheckFailure): ...

# These handle missing roles, permissions, or NSFW-only restrictions,
# providing detailed human-readable feedback.

# --------------------------------------------------------------------------
# Argument Parsing Errors
# --------------------------------------------------------------------------

class BadUnionArgument(UserInputError): ...
class BadLiteralArgument(UserInputError): ...
class ArgumentParsingError(UserInputError): ...
class UnexpectedQuoteError(ArgumentParsingError): ...
class InvalidEndOfQuotedStringError(ArgumentParsingError): ...
class ExpectedClosingQuoteError(ArgumentParsingError): ...

# These cover all parsing errors, such as:
# - Unexpected or missing quotes
# - Invalid argument literals
# - Failed conversions using Union types

# --------------------------------------------------------------------------
# Extension (Cog) System Errors
# --------------------------------------------------------------------------

class ExtensionError(DiscordException):
    """Base exception for extension (Cog) related issues."""

    def __init__(self, message: Optional[str] = None, *args: Any, name: str) -> None:
        self.name = name
        message = message or f"Extension {name!r} had an error."
        m = message.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
        super().__init__(m, *args)


# Subclasses describe different extension (plugin) failure cases:
class ExtensionAlreadyLoaded(ExtensionError): ...
class ExtensionNotLoaded(ExtensionError): ...
class NoEntryPointError(ExtensionError): ...
class ExtensionFailed(ExtensionError): ...
class ExtensionNotFound(ExtensionError): ...


# --------------------------------------------------------------------------
# Command Registration Errors
# --------------------------------------------------------------------------

class CommandRegistrationError(ClientException):
    """Raised when two commands or aliases share the same name."""
    def __init__(self, name: str, *, alias_conflict: bool = False) -> None:
        self.name = name
        self.alias_conflict = alias_conflict
        type_ = "alias" if alias_conflict else "command"
        super().__init__(f"The {type_} {name} is already an existing command or alias.")


# --------------------------------------------------------------------------
# Flag (Argument Parser) Errors
# --------------------------------------------------------------------------

class FlagError(BadArgument): ...
class TooManyFlags(FlagError): ...
class BadFlagArgument(FlagError): ...
class MissingRequiredFlag(FlagError): ...
class MissingFlagArgument(FlagError): ...

# These exceptions are used when parsing command-line-like flag arguments fails.
# For example: too many values, missing required flag, invalid type conversion, etc.
