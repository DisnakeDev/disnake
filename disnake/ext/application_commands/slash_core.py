from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union, TYPE_CHECKING
from .base_core import InvokableApplicationCommand

from discord.app_commands import SlashCommand, Option
from discord.enums import OptionType
from discord._hub import _ApplicationCommandStore

from ..commands.errors import *

import asyncio

__all__ = (
    'InvokableSlashCommand',
    'SubCommandGroup',
    'SubCommand',
    'slash_command'
)

if TYPE_CHECKING:
    from discord.interactions import ApplicationCommandInteraction


def options_as_route(options: Dict[str, Any]) -> Tuple[Tuple[str, ...], Dict[str, Any]]:
    if not options:
        return (), {}
    name, value = next(iter(options.items()))
    if isinstance(value, dict):
        chain, kwargs = options_as_route(value)
        return (name,) + chain, kwargs
    return (), options


class SubCommandGroup(InvokableApplicationCommand):
    def __init__(self, func, *, name: str = None, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.children: Dict[str, SubCommand] = {}
        self.option = Option(
            name=self.name,
            description='-',
            type=OptionType.sub_command_group,
            options=[]
        )

    def sub_command(
        self,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: dict = None,
        **kwargs
    ) -> SubCommand:
        """
        A decorator that creates a subcommand in the
        subcommand group.
        Parameters are the same as in :class:`InvokableSlashCommand.sub_command`
        """

        def decorator(func):
            new_func = SubCommand(
                func,
                name=name,
                description=description,
                options=options,
                connectors=connectors,
                **kwargs
            )
            self.children[new_func.name] = new_func
            self.option.options.append(new_func.option)
            return new_func
        return decorator


class SubCommand(InvokableApplicationCommand):
    def __init__(
        self,
        func,
        *,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: Dict[str, str] = None,
        **kwargs
    ):
        super().__init__(func, name=name, **kwargs)
        self.connectors: Dict[str, str] = connectors
        self.option = Option(
            name=self.name,
            description=description or '-',
            type=OptionType.sub_command,
            options=options
        )
    
    async def invoke(self, inter: ApplicationCommandInteraction, *args, **kwargs):
        await self.prepare(inter)
        try:
            await self(inter, *args, **kwargs)
        except Exception as exc:
            inter.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter)


class InvokableSlashCommand(InvokableApplicationCommand):
    def __init__(
        self,
        func,
        *,
        name: str = None,
        description: str = None,
        options: List[Option] = None,
        default_permission: bool = True,
        guild_ids: List[int] = None,
        connectors: Dict[str, str] = None,
        auto_sync: bool = True,
        **kwargs
    ):
        super().__init__(func, name=name, **kwargs)
        self.connectors: Dict[str, str] = connectors
        self.children: Dict[str, Union[SubCommand, SubCommandGroup]] = {}
        self.auto_sync: bool = auto_sync
        self.guild_ids: List[int] = guild_ids
        self.body = SlashCommand(
            name=self.name,
            description=description or '-',
            options=options or [],
            default_permission=default_permission,
        )
    
    def sub_command(
        self,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: dict = None,
        **kwargs
    ) -> SubCommand:
        """
        A decorator that creates a subcommand under the base command.

        Parameters
        ----------
        name: :class:`str`
            the name of the subcommand. Defaults to the function name
        description: :class:`str`
            the description of the subcommand
        options: List[:class:`Option`]
            the options of the subcommand for registration in API
        connectors: Dict[:class:`str`, :class:`str`]
            which function param states for each option. If the name
            of an option already matches the corresponding function param,
            you don't have to specify the connectors. Connectors template:
            ``{"option-name": "param_name", ...}``
        """
        def decorator(func):
            if not self.children:
                if len(self.body.options) > 0:
                    self.body.options = []
            new_func = SubCommand(
                func,
                name=name,
                description=description,
                options=options,
                connectors=connectors,
                **kwargs
            )
            self.children[new_func.name] = new_func
            self.body.options.append(new_func.option)
            return new_func
        return decorator

    def sub_command_group(
        self,
        name: str = None,
        **kwargs
    ) -> SubCommandGroup:
        """
        A decorator that creates a subcommand group under the base command.
        Remember that the group must have at least one subcommand.

        Parameters
        ----------
        name : :class:`str`
            the name of the subcommand group. Defaults to the function name
        """
        def decorator(func):
            if not self.children:
                if len(self.body.options) > 0:
                    self.body.options = []

            new_func = SubCommandGroup(func, name=name, **kwargs)
            self.children[new_func.name] = new_func
            self.body.options.append(new_func.option)
            return new_func
        return decorator

    async def invoke_children(self, inter: ApplicationCommandInteraction):
        chain, kwargs = options_as_route(inter.options)
        if len(chain) == 0:
            group = None
            subcmd = None
        elif len(chain) == 1:
            group = None
            subcmd = self.children.get(chain[0])
        elif len(chain) == 2:
            group = self.children.get(chain[0])
            subcmd = group.children.get(chain[1]) if group else None

        if group is not None:
            try:
                await group.invoke(inter)
            except Exception as err:
                group.dispatch_error(inter, err)
                raise err

        if subcmd is not None:
            try:
                await subcmd.invoke(inter, **kwargs)
            except Exception as err:
                subcmd.dispatch_error(inter, err)
                raise err

    async def invoke(self, inter: ApplicationCommandInteraction):
        # interaction._wrap_choices(self.body)
        inter.application_command = self
        await self.prepare(inter)
        try:
            if self.children:
                await self(inter)
                await self.invoke_children(inter)
            else:
                await self(inter, **inter.options)
        except Exception as exc:
            inter.command_failed = True
            self.dispatch_error(inter, exc)
            raise CommandInvokeError(exc) from exc
        finally:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter)


def slash_command(
    *,
    name: str = None,
    description: str = None,
    options: List[Option] = None,
    default_permission: bool = True,
    guild_ids: List[int] = None,
    connectors: Dict[str, str] = None,
    auto_sync: bool = True,
    **kwargs
) -> InvokableSlashCommand:
    """
    A decorator that builds a slash command.

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
    default_permission: :class:`bool`
        whether the command is enabled by default when the app is added to a guild.
    guild_ids: List[:class:`int`]
        if specified, the client will register a command in these guilds.
        Otherwise this command will be registered globally.
    connectors: Dict[:class:`str`, :class:`str`]
        binds function names to option names. If the name
        of an option already matches the corresponding function param,
        you don't have to specify the connectors. Connectors template:
        ``{"option-name": "param_name", ...}``
    """

    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f'<{func.__qualname__}> must be a coroutine function')
        new_func = InvokableSlashCommand(
            func,
            name=name,
            description=description,
            options=options,
            default_permission=default_permission,
            guild_ids=guild_ids,
            connectors=connectors,
            auto_sync=auto_sync,
            **kwargs
        )
        _ApplicationCommandStore.slash_commands[new_func.name] = new_func
        return new_func
    return decorator
