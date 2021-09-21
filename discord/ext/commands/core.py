"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz, 2021-present EQUENOS

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

from disnake.ext.commands.core import Any, AnyContextT, ApplicationCommandInteraction, ArgumentParsingError, BadArgument, BadBoolArgument, BadColorArgument, BadColourArgument, BadFlagArgument, BadInviteArgument, BadLiteralArgument, BadUnionArgument, BotMissingAnyRole, BotMissingPermissions, BotMissingRole, BucketType, Callable, ChannelNotFound, ChannelNotReadable, CheckAnyFailure, CheckFailure, Cog, CogT, Command, CommandError, CommandInvokeError, CommandNotFound, CommandOnCooldown, CommandRegistrationError, CommandT, Context, ContextT, ConversionError, Cooldown, CooldownMapping, Dict, DisabledCommand, DynamicCooldownMapping, EmojiNotFound, ErrorT, ExpectedClosingQuoteError, ExtensionAlreadyLoaded, ExtensionError, ExtensionFailed, ExtensionNotFound, ExtensionNotLoaded, FlagError, Generator, Generic, Greedy, Group, GroupMixin, GroupT, GuildNotFound, GuildStickerNotFound, HookT, InvalidEndOfQuotedStringError, List, Literal, MISSING, MaxConcurrency, MaxConcurrencyReached, MemberNotFound, MessageNotFound, MissingAnyRole, MissingFlagArgument, MissingPermissions, MissingRequiredArgument, MissingRequiredFlag, MissingRole, NSFWChannelRequired, NoEntryPointError, NoPrivateMessage, NotOwner, ObjectNotFound, Optional, P, PartialEmojiConversionFailure, PrivateMessageOnly, RoleNotFound, Set, T, TYPE_CHECKING, ThreadNotFound, TooManyArguments, TooManyFlags, Tuple, Type, TypeVar, UnexpectedQuoteError, Union, UserInputError, UserNotFound, _BaseCommand, _CaseInsensitiveDict, after_invoke, annotations, asyncio, before_invoke, bot_has_any_role, bot_has_guild_permissions, bot_has_permissions, bot_has_role, check, check_any, command, cooldown, datetime, disnake, dm_only, dynamic_cooldown, functools, get_converter, get_signature_parameters, group, guild_only, has_any_role, has_guild_permissions, has_permissions, has_role, hooked_wrapped_callback, inspect, is_nsfw, is_owner, max_concurrency, overload, run_converters, unwrap_function, wrap_callback
__all__ = ('Command', 'Group', 'GroupMixin', 'command', 'group', 'has_role', 'has_permissions', 'has_any_role', 'check', 'check_any', 'before_invoke', 'after_invoke', 'bot_has_role', 'bot_has_permissions', 'bot_has_any_role', 'cooldown', 'dynamic_cooldown', 'max_concurrency', 'dm_only', 'guild_only', 'is_owner', 'is_nsfw', 'has_guild_permissions', 'bot_has_guild_permissions')