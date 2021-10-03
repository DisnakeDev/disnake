"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

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


import asyncio
import collections
import collections.abc
import inspect
import importlib.util
import logging
import os
import sys
import traceback
import time
import types
from typing import Any, Callable, Mapping, List, Dict, TYPE_CHECKING, Optional, TypeVar, Type, Union, Set, Tuple, Coroutine

import disnake

from .core import GroupMixin
from .base_core import InvokableApplicationCommand
from .slash_core import InvokableSlashCommand
from .ctx_menus_core import InvokableUserCommand, InvokableMessageCommand
from .view import StringView
from .context import Context
from .errors import CommandRegistrationError
from . import errors
from .help import HelpCommand, DefaultHelpCommand
from .cog import Cog
from .slash_core import slash_command
from .ctx_menus_core import user_command, message_command

from disnake.app_commands import ApplicationCommand
from disnake.enums import ApplicationCommandType

if TYPE_CHECKING:
    import importlib.machinery

    from typing_extensions import Concatenate, ParamSpec
    from disnake.message import Message
    from disnake.interactions import (
        ApplicationCommandInteraction,
        MessageCommandInteraction,
        UserCommandInteraction,
    )
    from ._types import (
        Check,
        CoroFunc,
    )
    ApplicationCommandInteractionT = TypeVar('ApplicationCommandInteractionT', bound=ApplicationCommandInteraction, covariant=True)
    AnyMessageCommandInter = Any # Union[ApplicationCommandInteraction, UserCommandInteraction]
    AnyUserCommandInter = Any # Union[ApplicationCommandInteraction, UserCommandInteraction]
    
    P = ParamSpec('P')

__all__ = (
    'when_mentioned',
    'when_mentioned_or',
    'Bot',
    'AutoShardedBot',
)

MISSING: Any = disnake.utils.MISSING

T = TypeVar('T')
CFT = TypeVar('CFT', bound='CoroFunc')
CXT = TypeVar('CXT', bound='Context')

def when_mentioned(bot: Union[Bot, AutoShardedBot], msg: Message) -> List[str]:
    """A callable that implements a command prefix equivalent to being mentioned.

    These are meant to be passed into the :attr:`.Bot.command_prefix` attribute.
    """
    # bot.user will never be None when this is called
    return [f'<@{bot.user.id}> ', f'<@!{bot.user.id}> ']  # type: ignore

def when_mentioned_or(*prefixes: str) -> Callable[[Union[Bot, AutoShardedBot], Message], List[str]]:
    """A callable that implements when mentioned or other prefixes provided.

    These are meant to be passed into the :attr:`.Bot.command_prefix` attribute.

    Example
    --------

    .. code-block:: python3

        bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))


    .. note::

        This callable returns another callable, so if this is done inside a custom
        callable, you must call the returned callable, for example:

        .. code-block:: python3

            async def get_prefix(bot, message):
                extras = await prefixes_for(message.guild) # returns a list
                return commands.when_mentioned_or(*extras)(bot, message)


    See Also
    ----------
    :func:`.when_mentioned`
    """
    def inner(bot, msg):
        r = list(prefixes)
        r = when_mentioned(bot, msg) + r
        return r

    return inner

def _is_submodule(parent: str, child: str) -> bool:
    return parent == child or child.startswith(parent + ".")

class _DefaultRepr:
    def __repr__(self):
        return '<default-help-command>'

_default: Any = _DefaultRepr()


class BotBase(GroupMixin):
    def __init__(
        self,
        command_prefix: Optional[Union[str, List[str], Callable]] = None,
        help_command: HelpCommand = _default,
        description: str = None,
        **options: Any,
    ):
        super().__init__(**options)
        self.command_prefix = command_prefix
        self.extra_events: Dict[str, List[CoroFunc]] = {}
        self.__cogs: Dict[str, Cog] = {}
        self.__extensions: Dict[str, types.ModuleType] = {}

        self._checks: List[Check] = []
        self._check_once = []
        self._slash_command_checks = []
        self._slash_command_check_once = []
        self._user_command_checks = []
        self._user_command_check_once = []
        self._message_command_checks = []
        self._message_command_check_once = []

        self._before_invoke = None
        self._after_invoke = None
        self._before_slash_command_invoke = None
        self._after_slash_command_invoke = None
        self._before_user_command_invoke = None
        self._after_user_command_invoke = None
        self._before_message_command_invoke = None
        self._after_message_command_invoke = None

        self._help_command = None
        self.description: str = inspect.cleandoc(description) if description else ''
        self.strip_after_prefix: bool = options.get('strip_after_prefix', False)
        self.reload: bool = options.get('reload', False)

        self.owner_id: Optional[int] = options.get('owner_id')
        self.owner_ids: Set[int] = options.get('owner_ids', set())
        self.owner: Optional[disnake.User] = None
        self.owners: Set[disnake.TeamMember] = set()

        self.all_slash_commands: Dict[str, InvokableSlashCommand] = {}
        self.all_user_commands: Dict[str, InvokableUserCommand] = {}
        self.all_message_commands: Dict[str, InvokableMessageCommand] = {}

        if self.owner_id and self.owner_ids:
            raise TypeError('Both owner_id and owner_ids are set.')

        if self.owner_ids and not isinstance(self.owner_ids, collections.abc.Collection):
            raise TypeError(f'owner_ids must be a collection not {self.owner_ids.__class__!r}')

        if help_command is _default:
            self.help_command = DefaultHelpCommand()
        else:
            self.help_command = help_command
        
        loop = asyncio.get_event_loop()
        loop.create_task(self._fill_owners())

        if self.reload:
            loop.create_task(self._watchdog())

    @property
    def application_commands(self) -> Set[InvokableApplicationCommand]:
        result = set()
        for cmd in self.all_slash_commands.values():
            result.add(cmd)
        for cmd in self.all_user_commands.values():
            result.add(cmd)
        for cmd in self.all_message_commands.values():
            result.add(cmd)
        return result

    @property
    def slash_commands(self) -> Set[InvokableSlashCommand]:
        return set(self.all_slash_commands.values())

    @property
    def user_commands(self) -> Set[InvokableUserCommand]:
        return set(self.all_user_commands.values())

    @property
    def message_commands(self) -> Set[InvokableMessageCommand]:
        return set(self.all_message_commands.values())

    def add_slash_command(self, slash_command: InvokableSlashCommand) -> None:
        """Adds an :class:`.InvokableSlashCommand` into the internal list of slash commands.

        This is usually not called, instead the :meth:`~.BotBase.slash_command` or
        shortcut decorators are used.

        Parameters
        -----------
        slash_command: :class:`InvokableSlashCommand`
            The slash command to add.

        Raises
        -------
        :exc:`.CommandRegistrationError`
            If the slash command is already registered.
        TypeError
            If the slash command passed is not an instance of :class:`.InvokableSlashCommand`.
        """

        if not isinstance(slash_command, InvokableSlashCommand):
            raise TypeError('The slash_command passed must be an instance of InvokableSlashCommand')

        if slash_command.name in self.all_slash_commands:
            raise CommandRegistrationError(slash_command.name)

        self.all_slash_commands[slash_command.name] = slash_command

    def add_user_command(self, user_command: InvokableUserCommand) -> None:
        """Adds an :class:`.InvokableUserCommand` into the internal list of user commands.

        This is usually not called, instead the :meth:`~.BotBase.user_command` or
        shortcut decorators are used.

        Parameters
        -----------
        user_command: :class:`InvokableUserCommand`
            The user command to add.

        Raises
        -------
        :exc:`.CommandRegistrationError`
            If the user command is already registered.
        TypeError
            If the user command passed is not an instance of :class:`.InvokableUserCommand`.
        """

        if not isinstance(user_command, InvokableUserCommand):
            raise TypeError('The user_command passed must be an instance of InvokableUserCommand')

        if user_command.name in self.all_user_commands:
            raise CommandRegistrationError(user_command.name)

        self.all_user_commands[user_command.name] = user_command

    def add_message_command(self, message_command: InvokableMessageCommand) -> None:
        """Adds an :class:`.InvokableMessageCommand` into the internal list of message commands.

        This is usually not called, instead the :meth:`~.BotBase.message_command` or
        shortcut decorators are used.

        Parameters
        -----------
        message_command: :class:`InvokableMessageCommand`
            The message command to add.

        Raises
        -------
        :exc:`.CommandRegistrationError`
            If the message command is already registered.
        TypeError
            If the message command passed is not an instance of :class:`.InvokableMessageCommand`.
        """

        if not isinstance(message_command, InvokableMessageCommand):
            raise TypeError('The message_command passed must be an instance of InvokableMessageCommand')

        if message_command.name in self.all_message_commands:
            raise CommandRegistrationError(message_command.name)

        self.all_message_commands[message_command.name] = message_command

    def remove_slash_command(self, name: str) -> Optional[InvokableSlashCommand]:
        """Remove a :class:`.InvokableSlashCommand` from the internal list
        of slash commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the command to remove.

        Returns
        --------
        Optional[:class:`.InvokableSlashCommand`]
            The command that was removed. If the name is not valid then
            ``None`` is returned instead.
        """
        command = self.all_slash_commands.pop(name, None)
        if command is None:
            return None
        return command

    def remove_user_command(self, name: str) -> Optional[InvokableUserCommand]:
        """Remove a :class:`.InvokableUserCommand` from the internal list
        of user commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the command to remove.

        Returns
        --------
        Optional[:class:`.InvokableUserCommand`]
            The command that was removed. If the name is not valid then
            ``None`` is returned instead.
        """
        command = self.all_user_commands.pop(name, None)
        if command is None:
            return None
        return command
    
    def remove_message_command(self, name: str) -> Optional[InvokableMessageCommand]:
        """Remove a :class:`.InvokableMessageCommand` from the internal list
        of message commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the command to remove.

        Returns
        --------
        Optional[:class:`.InvokableMessageCommand`]
            The command that was removed. If the name is not valid then
            ``None`` is returned instead.
        """
        command = self.all_message_commands.pop(name, None)
        if command is None:
            return None
        return command

    def get_slash_command(self, name: str) -> Optional[InvokableSlashCommand]:
        """Get a :class:`.InvokableSlashCommand` from the internal list
        of commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the slash command to get.

        Returns
        --------
        Optional[:class:`InvokableSlashCommand`]
            The slash command that was requested. If not found, returns ``None``.
        """
        return self.all_slash_commands.get(name)

    def get_user_command(self, name: str) -> Optional[InvokableUserCommand]:
        """Get a :class:`.InvokableUserCommand` from the internal list
        of commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the user command to get.

        Returns
        --------
        Optional[:class:`InvokableUserCommand`]
            The user command that was requested. If not found, returns ``None``.
        """
        return self.all_user_commands.get(name)

    def get_message_command(self, name: str) -> Optional[InvokableMessageCommand]:
        """Get a :class:`.InvokableMessageCommand` from the internal list
        of commands.

        Parameters
        -----------
        name: :class:`str`
            The name of the message command to get.

        Returns
        --------
        Optional[:class:`InvokableMessageCommand`]
            The message command that was requested. If not found, returns ``None``.
        """
        return self.all_message_commands.get(name)

    def slash_command(
        self,
        *,
        name: str = None,
        description: str = None,
        options: List[disnake.app_commands.Option] = None,
        default_permission: bool = True,
        guild_ids: List[int] = None,
        connectors: Dict[str, str] = None,
        auto_sync: bool = True,
        **kwargs
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[Cog, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
            ]
        ],
        InvokableSlashCommand
    ]:
        """
        A shortcut decorator that invokes :func:`.slash_command` and adds it to
        the internal command list.

        Parameters
        ----------
        auto_sync: :class:`bool`
            whether to automatically register the command or not. Defaults to ``True``
        name: :class:`str`
            name of the slash command you want to respond to (equals to function name by default).
        description: :class:`str`
            the description of the slash command. It will be visible in Discord.
        options: List[:class:`Option`]
            the list of slash command options. The options will be visible in Discord.
            This is the old way of specifying options. Consider using :ref:`param_syntax` instead.
        default_permission: :class:`bool`
            whether the command is enabled by default when the app is added to a guild.
        guild_ids: List[:class:`int`]
            if specified, the client will register a command in these guilds.
            Otherwise this command will be registered globally in ~1 hour.
        connectors: Dict[:class:`str`, :class:`str`]
            binds function names to option names. If the name
            of an option already matches the corresponding function param,
            you don't have to specify the connectors. Connectors template:
            ``{"option-name": "param_name", ...}``.
            If you're using :ref:`param_syntax`, you don't need to specify this.
        
        Returns
        --------
        Callable[..., :class:`InvokableSlashCommand`]
            A decorator that converts the provided method into a InvokableSlashCommand, adds it to the bot, then returns it.
        """
        def decorator(
            func: Union[
                Callable[Concatenate[Cog, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
            ]
        ) -> InvokableSlashCommand:
            result = slash_command(
                name=name,
                description=description,
                options=options,
                default_permission=default_permission,
                guild_ids=guild_ids,
                connectors=connectors,
                auto_sync=auto_sync,
                **kwargs
            )(func)
            self.add_slash_command(result)
            return result
        return decorator

    def user_command(
        self,
        *,
        name: str = None,
        guild_ids: List[int] = None,
        auto_sync: bool = True,
        **kwargs
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[Cog, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
            ]
        ],
        InvokableUserCommand
    ]:
        """
        A shortcut decorator that invokes :func:`.user_command` and adds it to
        the internal command list.

        Parameters
        ----------
        auto_sync: :class:`bool`
            whether to automatically register the command or not. Defaults to ``True``
        name: :class:`str`
            name of the user command you want to respond to (equals to function name by default).
        guild_ids: List[:class:`int`]
            if specified, the client will register the command in these guilds.
            Otherwise this command will be registered globally in ~1 hour.
        
        Returns
        --------
        Callable[..., :class:`InvokableUserCommand`]
            A decorator that converts the provided method into a InvokableUserCommand, adds it to the bot, then returns it.
        """
        def decorator(
            func: Union[
                Callable[Concatenate[Cog, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
            ]
        ) -> InvokableUserCommand:
            result = user_command(name=name, guild_ids=guild_ids, auto_sync=auto_sync, **kwargs)(func)
            self.add_user_command(result)
            return result
        return decorator

    def message_command(
        self,
        *,
        name: str = None,
        guild_ids: List[int] = None,
        auto_sync: bool = True,
        **kwargs
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[Cog, AnyMessageCommandInter, P], Coroutine],
                Callable[Concatenate[AnyMessageCommandInter, P], Coroutine]
            ]
        ],
        InvokableMessageCommand
    ]:
        """
        A shortcut decorator that invokes :func:`.message_command` and adds it to
        the internal command list.

        Parameters
        ----------
        auto_sync: :class:`bool`
            whether to automatically register the command or not. Defaults to ``True``
        name: :class:`str`
            name of the message command you want to respond to (equals to function name by default).
        guild_ids: List[:class:`int`]
            if specified, the client will register the command in these guilds.
            Otherwise this command will be registered globally in ~1 hour.
        
        Returns
        --------
        Callable[..., :class:`InvokableUserCommand`]
            A decorator that converts the provided method into a InvokableUserCommand, adds it to the bot, then returns it.
        """
        def decorator(
            func: Union[
                Callable[Concatenate[Cog, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
            ]
        ) -> InvokableMessageCommand:
            result = message_command(name=name, guild_ids=guild_ids, auto_sync=auto_sync, **kwargs)(func)
            self.add_message_command(result)
            return result
        return decorator

    # internal helpers

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        # super() will resolve to Client
        super().dispatch(event_name, *args, **kwargs)  # type: ignore
        ev = 'on_' + event_name
        for event in self.extra_events.get(ev, []):
            self._schedule_event(event, ev, *args, **kwargs)  # type: ignore

    def _ordered_unsynced_commands(
        self, test_guilds: List[int] = None
    ) -> Tuple[List[ApplicationCommand], Dict[int, List[ApplicationCommand]]]:
        global_cmds = []
        guilds = {}
        for cmd in self.application_commands:
            if not cmd.auto_sync:
                cmd.body._always_synced = True
            guild_ids = cmd.guild_ids or test_guilds
            if guild_ids is None:
                global_cmds.append(cmd.body)
            else:
                for guild_id in guild_ids:
                    if guild_id not in guilds:
                        guilds[guild_id] = [cmd.body]
                    else:
                        guilds[guild_id].append(cmd.body)
        return global_cmds, guilds

    @disnake.utils.copy_doc(disnake.Client.close)
    async def close(self) -> None:
        for extension in tuple(self.__extensions):
            try:
                self.unload_extension(extension)
            except Exception:
                pass

        for cog in tuple(self.__cogs):
            try:
                self.remove_cog(cog)
            except Exception:
                pass

        await super().close()  # type: ignore

    async def _fill_owners(self) -> None:
        if self.owner_id or self.owner_ids:
            return
        
        await self.wait_until_first_connect() # type: ignore

        app = await self.application_info()  # type: ignore
        if app.team:
            self.owners = set(app.team.members)
            self.owner_ids = {m.id for m in app.team.members}
        else:
            self.owner = app.owner
            self.owner_id = app.owner.id

    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        """|coro|

        The default command error handler provided by the bot.

        By default this prints to :data:`sys.stderr` however it could be
        overridden to have a different implementation.

        This only fires if you do not specify any listeners for command error.
        """
        if self.extra_events.get('on_command_error', None):
            return

        command = context.command
        if command and command.has_error_handler():
            return

        cog = context.cog
        if cog and cog.has_error_handler():
            return

        print(f'Ignoring exception in command {context.command}:', file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def on_slash_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        exception: errors.CommandError
    ) -> None:
        if self.extra_events.get('on_slash_command_error', None):
            return

        command = interaction.application_command
        if command and command.has_error_handler():
            return

        cog = command.cog
        if cog and cog.has_slash_error_handler():
            return

        print(f'Ignoring exception in slash command {command.name!r}:', file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def on_user_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        exception: errors.CommandError
    ) -> None:
        if self.extra_events.get('on_user_command_error', None):
            return
        command = interaction.application_command
        if command and command.has_error_handler():
            return
        cog = command.cog
        if cog and cog.has_user_error_handler():
            return
        print(f'Ignoring exception in user command {command.name!r}:', file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def on_message_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        exception: errors.CommandError
    ) -> None:
        if self.extra_events.get('on_message_command_error', None):
            return
        command = interaction.application_command
        if command and command.has_error_handler():
            return
        cog = command.cog
        if cog and cog.has_message_error_handler():
            return
        print(f'Ignoring exception in message command {command.name!r}:', file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    # global check registration

    def add_check(
        self,
        func: Check,
        *,
        call_once: bool = False,
        text_commands: bool = False,
        slash_commands: bool = False,
        user_commands: bool = False,
        message_commands: bool = False,
    ) -> None:
        """Adds a global check to the bot.

        This is the non-decorator interface to :meth:`.check`,
        :meth:`.check_once`, :meth:`.slash_command_check` and etc.

        If none of bool params are specified, the check is for
        text commands only.

        Parameters
        -----------
        func
            The function that was used as a global check.
        call_once: :class:`bool`
            If the function should only be called once per
            :meth:`.invoke` call.
        text_commands: :class:`bool`
            If this check is for text commands.
        slash_commands: :class:`bool`
            If this check is for slash commands.
        user_commands: :class:`bool`
            If this check is for user commands.
        message_commands: :class:`bool`
            If this check is for message commands.
        """
        if not (
            text_commands or
            slash_commands or
            user_commands or
            message_commands
        ):
            text_commands = True

        if text_commands:
            if call_once:
                self._check_once.append(func)
            else:
                self._checks.append(func)
        
        if slash_commands:
            if call_once:
                self._slash_command_check_once.append(func)
            else:
                self._slash_command_checks.append(func)
        
        if user_commands:
            if call_once:
                self._user_command_check_once.append(func)
            else:
                self._user_command_checks.append(func)
        
        if message_commands:
            if call_once:
                self._message_command_check_once.append(func)
            else:
                self._message_command_checks.append(func)

    def remove_check(
        self,
        func: Check,
        *,
        call_once: bool = False,
        text_commands: bool = False,
        slash_commands: bool = False,
        user_commands: bool = False,
        message_commands: bool = False,
    ) -> None:
        """Removes a global check from the bot.

        This function is idempotent and will not raise an exception
        if the function is not in the global checks.

        If none of bool params are specified, the check is for
        text commands only.

        Parameters
        -----------
        func
            The function to remove from the global checks.
        call_once: :class:`bool`
            If the function was added with ``call_once=True`` in
            the :meth:`.Bot.add_check` call or using :meth:`.check_once`.
        text_commands: :class:`bool`
            If this check was for text commands.
        slash_commands: :class:`bool`
            If this check was for slash commands.
        user_commands: :class:`bool`
            If this check was for user commands.
        message_commands: :class:`bool`
            If this check was for message commands.
        """
        if not (
            text_commands or
            slash_commands or
            user_commands or
            message_commands
        ):
            text_commands = True

        if text_commands:
            l = self._check_once if call_once else self._checks
            try:
                l.remove(func)
            except ValueError:
                pass
        
        if slash_commands:
            l = self._slash_command_check_once if call_once else self._slash_command_checks
            try:
                l.remove(func)
            except ValueError:
                pass
        
        if user_commands:
            l = self._user_command_check_once if call_once else self._user_command_checks
            try:
                l.remove(func)
            except ValueError:
                pass
        
        if message_commands:
            l = self._message_command_check_once if call_once else self._message_command_checks
            try:
                l.remove(func)
            except ValueError:
                pass

    def check(self, func: T) -> T:
        r"""A decorator that adds a global check to the bot.

        A global check is similar to a :func:`.check` that is applied
        on a per command basis except it is run before any command checks
        have been verified and applies to every command the bot has.

        .. note::

            This function can either be a regular function or a coroutine.

        Similar to a command :func:`.check`\, this takes a single parameter
        of type :class:`.Context` and can only raise exceptions inherited from
        :exc:`.CommandError`.

        Example
        ---------

        .. code-block:: python3

            @bot.check
            def check_commands(ctx):
                return ctx.command.qualified_name in allowed_commands

        """
        # T was used instead of Check to ensure the type matches on return
        self.add_check(func)  # type: ignore
        return func

    def check_once(self, func: CFT) -> CFT:
        r"""A decorator that adds a "call once" global check to the bot.

        Unlike regular global checks, this one is called only once
        per :meth:`.invoke` call.

        Regular global checks are called whenever a command is called
        or :meth:`.Command.can_run` is called. This type of check
        bypasses that and ensures that it's called only once, even inside
        the default help command.

        .. note::

            When using this function the :class:`.Context` sent to a group subcommand
            may only parse the parent command and not the subcommands due to it
            being invoked once per :meth:`.Bot.invoke` call.

        .. note::

            This function can either be a regular function or a coroutine.

        Similar to a command :func:`.check`\, this takes a single parameter
        of type :class:`.Context` and can only raise exceptions inherited from
        :exc:`.CommandError`.

        Example
        ---------

        .. code-block:: python3

            @bot.check_once
            def whitelist(ctx):
                return ctx.message.author.id in my_whitelist

        """
        self.add_check(func, call_once=True)
        return func

    def slash_command_check(self, func: T) -> T:
        """Similar to :meth:`.check` but for slash commands."""
        # T was used instead of Check to ensure the type matches on return
        self.add_check(func, slash_commands=True)  # type: ignore
        return func

    def slash_command_check_once(self, func: CFT) -> CFT:
        """Similar to :meth:`.check_once` but for slash commands."""
        self.add_check(func, call_once=True, slash_commands=True)
        return func
    
    def user_command_check(self, func: T) -> T:
        """Similar to :meth:`.check` but for user commands."""
        # T was used instead of Check to ensure the type matches on return
        self.add_check(func, user_commands=True)  # type: ignore
        return func

    def user_command_check_once(self, func: CFT) -> CFT:
        """Similar to :meth:`.check_once` but for user commands."""
        self.add_check(func, call_once=True, user_commands=True)
        return func
    
    def message_command_check(self, func: T) -> T:
        """Similar to :meth:`.check` but for message commands."""
        # T was used instead of Check to ensure the type matches on return
        self.add_check(func, message_commands=True)  # type: ignore
        return func

    def message_command_check_once(self, func: CFT) -> CFT:
        """Similar to :meth:`.check_once` but for message commands."""
        self.add_check(func, call_once=True, message_commands=True)
        return func

    def application_command_check(
        self,
        *,
        call_once: bool = False,
        slash_commands: bool = False,
        user_commands: bool = False,
        message_commands: bool = False,
    ) -> Callable[
        [Callable[[ApplicationCommandInteraction], Any]],
        Callable[[ApplicationCommandInteraction], Any]
    ]:
        r"""A decorator that adds a global check to the bot.

        A global check is similar to a :func:`.check` that is applied
        on a per command basis except it is run before any application command checks
        have been verified and applies to every application command the bot has.

        .. note::

            This function can either be a regular function or a coroutine.

        Similar to a command :func:`.check`\, this takes a single parameter
        of type :class:`.ApplicationCommandInteraction` and can only raise exceptions inherited from
        :exc:`.CommandError`.

        Example
        -------

        .. code-block:: python3

            @bot.application_command_check()
            def check_app_commands(inter):
                return inter.channel_id in whitelisted_channels
        
        Parameters
        ----------
        call_once: :class:`bool`
            If the function should only be called once per
            :meth:`.invoke` call.
        text_commands: :class:`bool`
            If this check is for text commands.
        slash_commands: :class:`bool`
            If this check is for slash commands.
        user_commands: :class:`bool`
            If this check is for user commands.
        message_commands: :class:`bool`
            If this check is for message commands.
        """
        if not (slash_commands or user_commands or message_commands):
            slash_commands = True
            user_commands = True
            message_commands = True
        
        def decorator(
            func: Callable[[ApplicationCommandInteraction], Any]
        ) -> Callable[[ApplicationCommandInteraction], Any]:
            # T was used instead of Check to ensure the type matches on return
            self.add_check(
                func, # type: ignore
                call_once=call_once,
                slash_commands=slash_commands,
                user_commands=user_commands,
                message_commands=message_commands
            )
            return func
        return decorator

    async def can_run(self, ctx: Context, *, call_once: bool = False) -> bool:
        data = self._check_once if call_once else self._checks

        if len(data) == 0:
            return True

        # type-checker doesn't distinguish between functions and methods
        return await disnake.utils.async_all(f(ctx) for f in data)  # type: ignore
    
    async def application_command_can_run(
        self,
        inter: ApplicationCommandInteraction,
        *,
        call_once: bool = False
    ) -> bool:

        if inter.data.type is ApplicationCommandType.chat_input:
            checks = self._slash_command_check_once if call_once else self._slash_command_checks
        
        elif inter.data.type is ApplicationCommandType.user:
            checks = self._user_command_check_once if call_once else self._user_command_checks

        elif inter.data.type is ApplicationCommandType.message:
            checks = self._message_command_check_once if call_once else self._message_command_checks
        
        else:
            return True

        if len(checks) == 0:
            return True

        # type-checker doesn't distinguish between functions and methods
        return await disnake.utils.async_all(f(inter) for f in checks)  # type: ignore

    async def is_owner(self, user: Union[disnake.User, disnake.Member]) -> bool:
        """|coro|

        Checks if a :class:`~disnake.User` or :class:`~disnake.Member` is the owner of
        this bot.

        If an :attr:`owner_id` is not set, it is fetched automatically
        through the use of :meth:`~.Bot.application_info`.

        .. versionchanged:: 1.3
            The function also checks if the application is team-owned if
            :attr:`owner_ids` is not set.

        Parameters
        -----------
        user: :class:`.abc.User`
            The user to check for.

        Returns
        --------
        :class:`bool`
            Whether the user is the owner.
        """

        if self.owner_id:
            return user.id == self.owner_id
        elif self.owner_ids:
            return user.id in self.owner_ids
        else:
            app = await self.application_info()  # type: ignore
            if app.team:
                self.owners = set(app.team.members)
                self.owner_ids = ids = {m.id for m in app.team.members}
                return user.id in ids
            else:
                self.owner = app.owner
                self.owner_id = owner_id = app.owner.id
                return user.id == owner_id

    def before_invoke(self, coro: CFT) -> CFT:
        """A decorator that registers a coroutine as a pre-invoke hook.

        A pre-invoke hook is called directly before the command is
        called. This makes it a useful function to set up database
        connections or any type of set up required.

        This pre-invoke hook takes a sole parameter, a :class:`.Context`.

        .. note::

            The :meth:`~.Bot.before_invoke` and :meth:`~.Bot.after_invoke` hooks are
            only called if all checks and argument parsing procedures pass
            without error. If any check or argument parsing procedures fail
            then the hooks are not called.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the pre-invoke hook.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_invoke = coro
        return coro

    def after_invoke(self, coro: CFT) -> CFT:
        r"""A decorator that registers a coroutine as a post-invoke hook.

        A post-invoke hook is called directly after the command is
        called. This makes it a useful function to clean-up database
        connections or any type of clean up required.

        This post-invoke hook takes a sole parameter, a :class:`.Context`.

        .. note::

            Similar to :meth:`~.Bot.before_invoke`\, this is not called unless
            checks and argument parsing procedures succeed. This hook is,
            however, **always** called regardless of the internal command
            callback raising an error (i.e. :exc:`.CommandInvokeError`\).
            This makes it ideal for clean-up scenarios.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the post-invoke hook.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_invoke = coro
        return coro

    def before_slash_command_invoke(self, coro: CFT) -> CFT:
        """Similar to :meth:`.before_invoke` but for slash commands."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_slash_command_invoke = coro
        return coro

    def after_slash_command_invoke(self, coro: CFT) -> CFT:
        """Similar to :meth:`.after_invoke` but for slash commands."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_slash_command_invoke = coro
        return coro
    
    def before_user_command_invoke(self, coro: CFT) -> CFT:
        """Similar to :meth:`.before_invoke` but for user commands."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_user_command_invoke = coro
        return coro

    def after_user_command_invoke(self, coro: CFT) -> CFT:
        """Similar to :meth:`.after_invoke` but for user commands."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_user_command_invoke = coro
        return coro

    def before_message_command_invoke(self, coro: CFT) -> CFT:
        """Similar to :meth:`.before_invoke` but for message commands."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_message_command_invoke = coro
        return coro

    def after_message_command_invoke(self, coro: CFT) -> CFT:
        """Similar to :meth:`.after_invoke` but for message commands."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_message_command_invoke = coro
        return coro

    # listener registration

    def add_listener(self, func: CoroFunc, name: str = MISSING) -> None:
        """The non decorator alternative to :meth:`.listen`.

        Parameters
        -----------
        func: :ref:`coroutine <coroutine>`
            The function to call.
        name: :class:`str`
            The name of the event to listen for. Defaults to ``func.__name__``.

        Example
        --------

        .. code-block:: python

            async def on_ready(): pass
            async def my_message(message): pass

            bot.add_listener(on_ready)
            bot.add_listener(my_message, 'on_message')

        """
        name = func.__name__ if name is MISSING else name

        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Listeners must be coroutines')

        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def remove_listener(self, func: CoroFunc, name: str = MISSING) -> None:
        """Removes a listener from the pool of listeners.

        Parameters
        -----------
        func
            The function that was used as a listener to remove.
        name: :class:`str`
            The name of the event we want to remove. Defaults to
            ``func.__name__``.
        """

        name = func.__name__ if name is MISSING else name

        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                pass

    def listen(self, name: str = MISSING) -> Callable[[CFT], CFT]:
        """A decorator that registers another function as an external
        event listener. Basically this allows you to listen to multiple
        events from different places e.g. such as :func:`.on_ready`

        The functions being listened to must be a :ref:`coroutine <coroutine>`.

        Example
        --------

        .. code-block:: python3

            @bot.listen()
            async def on_message(message):
                print('one')

            # in some other file...

            @bot.listen('on_message')
            async def my_message(message):
                print('two')

        Would print one and two in an unspecified order.

        Raises
        -------
        TypeError
            The function being listened to is not a coroutine.
        """

        def decorator(func: CFT) -> CFT:
            self.add_listener(func, name)
            return func

        return decorator

    # cogs

    def add_cog(self, cog: Cog, *, override: bool = False) -> None:
        """Adds a "cog" to the bot.

        A cog is a class that has its own event listeners and commands.

        .. versionchanged:: 2.0

            :exc:`.ClientException` is raised when a cog with the same name
            is already loaded.

        Parameters
        -----------
        cog: :class:`.Cog`
            The cog to register to the bot.
        override: :class:`bool`
            If a previously loaded cog with the same name should be ejected
            instead of raising an error.

            .. versionadded:: 2.0

        Raises
        -------
        TypeError
            The cog does not inherit from :class:`.Cog`.
        CommandError
            An error happened during loading.
        .ClientException
            A cog with the same name is already loaded.
        """

        if not isinstance(cog, Cog):
            raise TypeError('cogs must derive from Cog')

        cog_name = cog.__cog_name__
        existing = self.__cogs.get(cog_name)

        if existing is not None:
            if not override:
                raise disnake.ClientException(f'Cog named {cog_name!r} already loaded')
            self.remove_cog(cog_name)

        # NOTE: Should be covariant
        cog = cog._inject(self) # type: ignore
        self.__cogs[cog_name] = cog

    def get_cog(self, name: str) -> Optional[Cog]:
        """Gets the cog instance requested.

        If the cog is not found, ``None`` is returned instead.

        Parameters
        -----------
        name: :class:`str`
            The name of the cog you are requesting.
            This is equivalent to the name passed via keyword
            argument in class creation or the class name if unspecified.

        Returns
        --------
        Optional[:class:`Cog`]
            The cog that was requested. If not found, returns ``None``.
        """
        return self.__cogs.get(name)

    def remove_cog(self, name: str) -> Optional[Cog]:
        """Removes a cog from the bot and returns it.

        All registered commands and event listeners that the
        cog has registered will be removed as well.

        If no cog is found then this method has no effect.

        Parameters
        -----------
        name: :class:`str`
            The name of the cog to remove.

        Returns
        -------
        Optional[:class:`.Cog`]
             The cog that was removed. ``None`` if not found.
        """

        cog = self.__cogs.pop(name, None)
        if cog is None:
            return

        help_command = self._help_command
        if help_command and help_command.cog is cog:
            help_command.cog = None
        # NOTE: Should be covariant
        cog._eject(self) # type: ignore

        return cog

    @property
    def cogs(self) -> Mapping[str, Cog]:
        """Mapping[:class:`str`, :class:`Cog`]: A read-only mapping of cog name to cog."""
        return types.MappingProxyType(self.__cogs)

    # extensions

    def _remove_module_references(self, name: str) -> None:
        # find all references to the module
        # remove the cogs registered from the module
        for cogname, cog in self.__cogs.copy().items():
            if _is_submodule(name, cog.__module__):
                self.remove_cog(cogname)

        # remove all the commands from the module
        for cmd in self.all_commands.copy().values():
            if cmd.module is not None and _is_submodule(name, cmd.module):
                if isinstance(cmd, GroupMixin):
                    cmd.recursively_remove_all_commands()
                self.remove_command(cmd.name)

        # remove all the listeners from the module
        for event_list in self.extra_events.copy().values():
            remove = [
                index
                for index, event in enumerate(event_list)
                if event.__module__ is not None
                and _is_submodule(name, event.__module__)
            ]

            for index in reversed(remove):
                del event_list[index]

    def _call_module_finalizers(self, lib: types.ModuleType, key: str) -> None:
        try:
            func = getattr(lib, 'teardown')
        except AttributeError:
            pass
        else:
            try:
                func(self)
            except Exception:
                pass
        finally:
            self.__extensions.pop(key, None)
            sys.modules.pop(key, None)
            name = lib.__name__
            for module in list(sys.modules.keys()):
                if _is_submodule(name, module):
                    del sys.modules[module]

    def _load_from_module_spec(self, spec: importlib.machinery.ModuleSpec, key: str) -> None:
        # precondition: key not in self.__extensions
        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            del sys.modules[key]
            raise errors.ExtensionFailed(key, e) from e

        try:
            setup = getattr(lib, 'setup')
        except AttributeError:
            del sys.modules[key]
            raise errors.NoEntryPointError(key)

        try:
            setup(self)
        except Exception as e:
            del sys.modules[key]
            self._remove_module_references(lib.__name__)
            self._call_module_finalizers(lib, key)
            raise errors.ExtensionFailed(key, e) from e
        else:
            self.__extensions[key] = lib

    def _resolve_name(self, name: str, package: Optional[str]) -> str:
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError:
            raise errors.ExtensionNotFound(name)

    def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        """Loads an extension.

        An extension is a python module that contains commands, cogs, or
        listeners.

        An extension must have a global function, ``setup`` defined as
        the entry point on what to do when the extension is loaded. This entry
        point must have a single argument, the ``bot``.

        Parameters
        ------------
        name: :class:`str`
            The extension name to load. It must be dot separated like
            regular Python imports if accessing a sub-module. e.g.
            ``foo.test`` if you want to import ``foo/test.py``.
        package: Optional[:class:`str`]
            The package name to resolve relative imports with.
            This is required when loading an extension using a relative path, e.g ``.foo.test``.
            Defaults to ``None``.

            .. versionadded:: 1.7

        Raises
        --------
        ExtensionNotFound
            The extension could not be imported.
            This is also raised if the name of the extension could not
            be resolved using the provided ``package`` parameter.
        ExtensionAlreadyLoaded
            The extension is already loaded.
        NoEntryPointError
            The extension does not have a setup function.
        ExtensionFailed
            The extension or its setup function had an execution error.
        """

        name = self._resolve_name(name, package)
        if name in self.__extensions:
            raise errors.ExtensionAlreadyLoaded(name)

        spec = importlib.util.find_spec(name)
        if spec is None:
            raise errors.ExtensionNotFound(name)

        self._load_from_module_spec(spec, name)

    def unload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        """Unloads an extension.

        When the extension is unloaded, all commands, listeners, and cogs are
        removed from the bot and the module is un-imported.

        The extension can provide an optional global function, ``teardown``,
        to do miscellaneous clean-up if necessary. This function takes a single
        parameter, the ``bot``, similar to ``setup`` from
        :meth:`~.Bot.load_extension`.

        Parameters
        ------------
        name: :class:`str`
            The extension name to unload. It must be dot separated like
            regular Python imports if accessing a sub-module. e.g.
            ``foo.test`` if you want to import ``foo/test.py``.
        package: Optional[:class:`str`]
            The package name to resolve relative imports with.
            This is required when unloading an extension using a relative path, e.g ``.foo.test``.
            Defaults to ``None``.

            .. versionadded:: 1.7

        Raises
        -------
        ExtensionNotFound
            The name of the extension could not
            be resolved using the provided ``package`` parameter.
        ExtensionNotLoaded
            The extension was not loaded.
        """

        name = self._resolve_name(name, package)
        lib = self.__extensions.get(name)
        if lib is None:
            raise errors.ExtensionNotLoaded(name)

        self._remove_module_references(lib.__name__)
        self._call_module_finalizers(lib, name)

    def reload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        """Atomically reloads an extension.

        This replaces the extension with the same extension, only refreshed. This is
        equivalent to a :meth:`unload_extension` followed by a :meth:`load_extension`
        except done in an atomic way. That is, if an operation fails mid-reload then
        the bot will roll-back to the prior working state.

        Parameters
        ------------
        name: :class:`str`
            The extension name to reload. It must be dot separated like
            regular Python imports if accessing a sub-module. e.g.
            ``foo.test`` if you want to import ``foo/test.py``.
        package: Optional[:class:`str`]
            The package name to resolve relative imports with.
            This is required when reloading an extension using a relative path, e.g ``.foo.test``.
            Defaults to ``None``.

            .. versionadded:: 1.7

        Raises
        -------
        ExtensionNotLoaded
            The extension was not loaded.
        ExtensionNotFound
            The extension could not be imported.
            This is also raised if the name of the extension could not
            be resolved using the provided ``package`` parameter.
        NoEntryPointError
            The extension does not have a setup function.
        ExtensionFailed
            The extension setup function had an execution error.
        """

        name = self._resolve_name(name, package)
        lib = self.__extensions.get(name)
        if lib is None:
            raise errors.ExtensionNotLoaded(name)

        # get the previous module states from sys modules
        modules = {
            name: module
            for name, module in sys.modules.items()
            if _is_submodule(lib.__name__, name)
        }

        try:
            # Unload and then load the module...
            self._remove_module_references(lib.__name__)
            self._call_module_finalizers(lib, name)
            self.load_extension(name)
        except Exception:
            # if the load failed, the remnants should have been
            # cleaned from the load_extension function call
            # so let's load it from our old compiled library.
            lib.setup(self)  # type: ignore
            self.__extensions[name] = lib

            # revert sys.modules back to normal and raise back to caller
            sys.modules.update(modules)
            raise

    @property
    def extensions(self) -> Mapping[str, types.ModuleType]:
        """Mapping[:class:`str`, :class:`py:types.ModuleType`]: A read-only mapping of extension name to extension."""
        return types.MappingProxyType(self.__extensions)

    # help command stuff

    @property
    def help_command(self) -> Optional[HelpCommand]:
        return self._help_command

    @help_command.setter
    def help_command(self, value: Optional[HelpCommand]) -> None:
        if value is not None:
            if not isinstance(value, HelpCommand):
                raise TypeError('help_command must be a subclass of HelpCommand')
            if self._help_command is not None:
                self._help_command._remove_from_bot(self)
            self._help_command = value
            value._add_to_bot(self)
        elif self._help_command is not None:
            self._help_command._remove_from_bot(self)
            self._help_command = None
        else:
            self._help_command = None

    # command processing

    async def get_prefix(self, message: Message) -> Optional[Union[List[str], str]]:
        """|coro|

        Retrieves the prefix the bot is listening to
        with the message as a context.

        Parameters
        -----------
        message: :class:`disnake.Message`
            The message context to get the prefix of.

        Returns
        --------
        Optional[Union[List[:class:`str`], :class:`str`]]
            A list of prefixes or a single prefix that the bot is
            listening for. None if the bot isn't listening for prefixes.
        """
        prefix = ret = self.command_prefix
        if callable(prefix):
            ret = await disnake.utils.maybe_coroutine(prefix, self, message)
        
        if ret is None:
            return None

        if not isinstance(ret, str):
            try:
                ret = list(ret) # type: ignore
            except TypeError:
                # It's possible that a generator raised this exception.  Don't
                # replace it with our own error if that's the case.
                if isinstance(ret, collections.abc.Iterable):
                    raise

                raise TypeError("command_prefix must be plain string, iterable of strings, or callable "
                                f"returning either of these, not {ret.__class__.__name__}")

            if not ret:
                raise ValueError("Iterable command_prefix must contain at least one prefix")

        return ret

    async def get_context(self, message: Message, *, cls: Type[CXT] = Context) -> CXT:
        r"""|coro|

        Returns the invocation context from the message.

        This is a more low-level counter-part for :meth:`.process_commands`
        to allow users more fine grained control over the processing.

        The returned context is not guaranteed to be a valid invocation
        context, :attr:`.Context.valid` must be checked to make sure it is.
        If the context is not valid then it is not a valid candidate to be
        invoked under :meth:`~.Bot.invoke`.

        Parameters
        -----------
        message: :class:`disnake.Message`
            The message to get the invocation context from.
        cls
            The factory class that will be used to create the context.
            By default, this is :class:`.Context`. Should a custom
            class be provided, it must be similar enough to :class:`.Context`\'s
            interface.

        Returns
        --------
        :class:`.Context`
            The invocation context. The type of this can change via the
            ``cls`` parameter.
        """

        view = StringView(message.content)
        ctx = cls(prefix=None, view=view, bot=self, message=message)

        if message.author.id == self.user.id:  # type: ignore
            return ctx

        prefix = await self.get_prefix(message)
        invoked_prefix = prefix

        if prefix is None:
            return ctx
        elif isinstance(prefix, str):
            if not view.skip_string(prefix):
                return ctx
        else:
            try:
                # if the context class' __init__ consumes something from the view this
                # will be wrong.  That seems unreasonable though.
                if message.content.startswith(tuple(prefix)):
                    invoked_prefix = disnake.utils.find(view.skip_string, prefix)
                else:
                    return ctx

            except TypeError:
                if not isinstance(prefix, list):
                    raise TypeError("get_prefix must return either a string or a list of string, "
                                    f"not {prefix.__class__.__name__}")

                # It's possible a bad command_prefix got us here.
                for value in prefix:
                    if not isinstance(value, str):
                        raise TypeError("Iterable command_prefix or list returned from get_prefix must "
                                        f"contain only strings, not {value.__class__.__name__}")

                # Getting here shouldn't happen
                raise

        if self.strip_after_prefix:
            view.skip_ws()

        invoker = view.get_word()
        ctx.invoked_with = invoker
        # type-checker fails to narrow invoked_prefix type.
        ctx.prefix = invoked_prefix  # type: ignore
        ctx.command = self.all_commands.get(invoker)
        return ctx

    async def invoke(self, ctx: Context) -> None:
        """|coro|

        Invokes the command given under the invocation context and
        handles all the internal event dispatch mechanisms.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to invoke.
        """
        if ctx.command is not None:
            self.dispatch('command', ctx)
            try:
                if await self.can_run(ctx, call_once=True):
                    await ctx.command.invoke(ctx)
                else:
                    raise errors.CheckFailure('The global check once functions failed.')
            except errors.CommandError as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.dispatch('command_completion', ctx)
        elif ctx.invoked_with:
            exc = errors.CommandNotFound(f'Command "{ctx.invoked_with}" is not found')
            self.dispatch('command_error', ctx, exc)

    async def process_commands(self, message: Message) -> None:
        """|coro|

        This function processes the commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        commands will be triggered.

        By default, this coroutine is called inside the :func:`.on_message`
        event. If you choose to override the :func:`.on_message` event, then
        you should invoke this coroutine as well.

        This is built using other low level tools, and is equivalent to a
        call to :meth:`~.Bot.get_context` followed by a call to :meth:`~.Bot.invoke`.

        This also checks if the message's author is a bot and doesn't
        call :meth:`~.Bot.get_context` or :meth:`~.Bot.invoke` if so.

        Parameters
        -----------
        message: :class:`disnake.Message`
            The message to process commands for.
        """
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        await self.invoke(ctx)
    
    async def process_app_command_autocompletion(self, inter: ApplicationCommandInteraction) -> None:
        """|coro|

        This function processes the application command autocompletions.
        Without this coroutine, none of the autocompletions will be performed.

        By default, this coroutine is called inside the :func:`.on_application_command_autocompletion`
        event. If you choose to override the :func:`.on_application_command_autocompletion` event, then
        you should invoke this coroutine as well.

        Parameters
        -----------
        inter: :class:`disnake.ApplicationCommandInteraction`
            The interaction to process.
        """
        slash_command = self.all_slash_commands.get(inter.data.name)
        
        if slash_command is None:
            return
        
        inter.bot = self # type: ignore
        if slash_command.guild_ids is None or inter.guild_id in slash_command.guild_ids:
            await slash_command._call_relevant_autocompleter(inter)

    async def process_application_commands(self, interaction: ApplicationCommandInteraction) -> None:
        """|coro|

        This function processes the application commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        application commands will be triggered.

        By default, this coroutine is called inside the :func:`.on_application_command`
        event. If you choose to override the :func:`.on_application_command` event, then
        you should invoke this coroutine as well.

        Parameters
        -----------
        interaction: :class:`disnake.ApplicationCommandInteraction`
            The interaction to process commands for.
        """
        interaction.bot = self # type: ignore
        command_type = interaction.data.type
        command_name = interaction.data.name
        app_command = None
        event_name = None

        if command_type is ApplicationCommandType.chat_input:
            app_command = self.all_slash_commands.get(command_name)
            event_name = 'slash_command'
        
        elif command_type is ApplicationCommandType.user:
            app_command = self.all_user_commands.get(command_name)
            event_name = 'user_command'
        
        elif command_type is ApplicationCommandType.message:
            app_command = self.all_message_commands.get(command_name)
            event_name = 'message_command'
        
        if event_name is None or app_command is None:
            # TODO: unregister this command from API
            return
        
        if app_command.guild_ids is None or interaction.guild_id in app_command.guild_ids:
            self.dispatch(event_name, interaction)
            try:
                if await self.application_command_can_run(interaction, call_once=True):
                    await app_command.invoke(interaction)
                else:
                    raise errors.CheckFailure('The global check once functions failed.')
            except errors.CommandError as exc:
                await app_command.dispatch_error(interaction, exc)
        else:
            # TODO: unregister this command from API
            pass

    async def on_message(self, message):
        await self.process_commands(message)
    
    async def on_application_command(self, interaction: ApplicationCommandInteraction):
        await self.process_application_commands(interaction)
    
    async def on_application_command_autocomplete(self, interaction: ApplicationCommandInteraction):
        await self.process_app_command_autocompletion(interaction)
    
    async def _watchdog(self):
        """|coro|
        
        Starts the bot watchdog which will watch currently loaded extensions 
        and reload them when they're modified.
        """
        if isinstance(self, disnake.Client):
            await self.wait_until_ready()
        
        reload_log = logging.getLogger(__name__)
        # ensure the message actually shows up
        if logging.root.level > logging.INFO:
            logging.basicConfig()
            reload_log.setLevel(logging.INFO)
        
        if isinstance(self, disnake.Client):
            is_closed = self.is_closed
        else:
            is_closed = lambda: False
        
        reload_log.info(f"WATCHDOG: Watching extensions")
        
        last = time.time()
        while not is_closed():
            t = time.time()
            
            extensions = set()
            for name, module in self.extensions.items():
                file = module.__file__
                if os.stat(file).st_mtime > last:
                    extensions.add(name)
            
            for name in extensions:
                try:
                    self.reload_extension(name)
                except errors.ExtensionError as e:
                    reload_log.exception(e)
                else:
                    reload_log.info(f"WATCHDOG: Reloaded '{name}'")
            
            await asyncio.sleep(1)
            last = t


class Bot(BotBase, disnake.Client):
    """Represents a disnake bot.

    This class is a subclass of :class:`disnake.Client` and as a result
    anything that you can do with a :class:`disnake.Client` you can do with
    this bot.

    This class also subclasses :class:`.GroupMixin` to provide the functionality
    to manage commands.

    Attributes
    -----------
    command_prefix
        The command prefix is what the message content must contain initially
        to have a command invoked. This prefix could either be a string to
        indicate what the prefix should be, or a callable that takes in the bot
        as its first parameter and :class:`disnake.Message` as its second
        parameter and returns the prefix. This is to facilitate "dynamic"
        command prefixes. This callable can be either a regular function or
        a coroutine.

        An empty string as the prefix always matches, enabling prefix-less
        command invocation. While this may be useful in DMs it should be avoided
        in servers, as it's likely to cause performance issues and unintended
        command invocations.

        The command prefix could also be an iterable of strings indicating that
        multiple checks for the prefix should be used and the first one to
        match will be the invocation prefix. You can get this prefix via
        :attr:`.Context.prefix`. To avoid confusion empty iterables are not
        allowed.

        .. note::

            When passing multiple prefixes be careful to not pass a prefix
            that matches a longer prefix occurring later in the sequence.  For
            example, if the command prefix is ``('!', '!?')``  the ``'!?'``
            prefix will never be matched to any message as the previous one
            matches messages starting with ``!?``. This is especially important
            when passing an empty string, it should always be last as no prefix
            after it will be matched.
    case_insensitive: :class:`bool`
        Whether the commands should be case insensitive. Defaults to ``False``. This
        attribute does not carry over to groups. You must set it to every group if
        you require group commands to be case insensitive as well.
    description: :class:`str`
        The content prefixed into the default help message.
    help_command: Optional[:class:`.HelpCommand`]
        The help command implementation to use. This can be dynamically
        set at runtime. To remove the help command pass ``None``. For more
        information on implementing a help command, see :ref:`ext_commands_help_command`.
    owner_id: Optional[:class:`int`]
        The user ID that owns the bot. If this is not set and is then queried via
        :meth:`.is_owner` then it is fetched automatically using
        :meth:`~.Bot.application_info`.
    owner_ids: Optional[Collection[:class:`int`]]
        The user IDs that owns the bot. This is similar to :attr:`owner_id`.
        If this is not set and the application is team based, then it is
        fetched automatically using :meth:`~.Bot.application_info`.
        For performance reasons it is recommended to use a :class:`set`
        for the collection. You cannot set both ``owner_id`` and ``owner_ids``.

        .. versionadded:: 1.3
    strip_after_prefix: :class:`bool`
        Whether to strip whitespace characters after encountering the command
        prefix. This allows for ``!   hello`` and ``!hello`` to both work if
        the ``command_prefix`` is set to ``!``. Defaults to ``False``.

        .. versionadded:: 1.7
    reload: :class:`bool`
        Whether to enable automatic extension reloading on file modification for debugging.
        Whenever you save an extension with reloading enabled the file will be automatically
        reloaded for you so you do not have to reload the extension manually.
        
        .. versionadded:: 2.0
    """
    pass


class AutoShardedBot(BotBase, disnake.AutoShardedClient):
    """This is similar to :class:`.Bot` except that it is inherited from
    :class:`disnake.AutoShardedClient` instead.
    """
    pass
