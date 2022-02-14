# The MIT License (MIT)

# Copyright (c) 2021-present EQUENOS

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import asyncio
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from disnake import utils
from disnake.app_commands import Option, SlashCommand
from disnake.enums import OptionType
from disnake.interactions import ApplicationCommandInteraction

from .base_core import InvokableApplicationCommand, _get_overridden_method
from .errors import *
from .params import call_param_func, expand_params

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    from disnake.app_commands import Choices

    from .cog import CogT

    ApplicationCommandInteractionT = TypeVar(
        "ApplicationCommandInteractionT", bound=ApplicationCommandInteraction, covariant=True
    )

    P = ParamSpec("P")

__all__ = ("InvokableSlashCommand", "SubCommandGroup", "SubCommand", "slash_command")


def _autocomplete(
    self: Union[SubCommand, InvokableSlashCommand], option_name: str
) -> Callable[[Callable], Callable]:
    exists = False
    for option in self.body.options:
        if option.name == option_name:
            option.autocomplete = True
            exists = True
            break

    if not exists:
        raise ValueError(f"Option '{option_name}' doesn't exist in '{self.qualified_name}'")

    def decorator(func: Callable) -> Callable:
        func.__slash_command__ = self
        self.autocompleters[option_name] = func
        return func

    return decorator


async def _call_autocompleter(
    self: Union[InvokableSlashCommand, SubCommand],
    param: str,
    inter: ApplicationCommandInteraction,
    user_input: str,
) -> Optional[Choices]:
    autocomp = self.autocompleters.get(param)
    if autocomp is None:
        return None
    if not callable(autocomp):
        return autocomp

    try:
        cog = autocomp.__slash_command__.cog
    except AttributeError:
        cog = None

    filled = inter.filled_options
    del filled[inter.data.focused_option.name]
    try:
        if cog is None:
            choices = autocomp(inter, user_input, **filled)
        else:
            choices = autocomp(cog, inter, user_input, **filled)
    except TypeError:
        if cog is None:
            choices = autocomp(inter, user_input)
        else:
            choices = autocomp(cog, inter, user_input)

    if inspect.isawaitable(choices):
        return await choices
    return choices


class SubCommandGroup(InvokableApplicationCommand):
    """A class that implements the protocol for a bot slash command group.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    ----------
    name: :class:`str`
        The name of the group.
    option: :class:`.Option`
        API representation of this subcommand.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the command group is invoked.
    cog: Optional[:class:`Cog`]
        The cog that this group belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the group could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_slash_command_error`
        event.
    """

    def __init__(self, func, *, name: str = None, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.children: Dict[str, SubCommand] = {}
        self.option = Option(
            name=self.name, description="-", type=OptionType.sub_command_group, options=[]
        )
        self.name = self.option.name
        self.qualified_name: str = ""

    @property
    def body(self) -> Option:
        return self.option

    def sub_command(
        self,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: dict = None,
        **kwargs,
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
            ]
        ],
        SubCommand,
    ]:
        """
        A decorator that creates a subcommand in the subcommand group.
        Parameters are the same as in :class:`InvokableSlashCommand.sub_command`

        Returns
        -------
        Callable[..., :class:`SubCommand`]
            A decorator that converts the provided method into a SubCommand, adds it to the bot, then returns it.
        """

        def decorator(
            func: Union[
                Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
            ]
        ) -> SubCommand:
            new_func = SubCommand(
                func,
                name=name,
                description=description,
                options=options,
                connectors=connectors,
                **kwargs,
            )
            qualified_name = self.qualified_name or self.name
            new_func.qualified_name = f"{qualified_name} {new_func.name}"
            self.children[new_func.name] = new_func
            self.option.options.append(new_func.option)
            return new_func

        return decorator


class SubCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot slash subcommand.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    ----------
    name: :class:`str`
        The name of the subcommand.
    option: :class:`.Option`
        API representation of this subcommand.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the subcommand is called.
    cog: Optional[:class:`Cog`]
        The cog that this subcommand belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the subcommand could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_slash_command_error`
        event.
    connectors: Dict[:class:`str`, :class:`str`]
        A mapping of option names to function parameter names, mainly for internal processes.
    """

    def __init__(
        self,
        func,
        *,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: Dict[str, str] = None,
        **kwargs,
    ):
        super().__init__(func, name=name, **kwargs)
        self.connectors: Dict[str, str] = connectors or {}
        self.autocompleters: Dict[str, Any] = kwargs.get("autocompleters", {})

        self.docstring = utils.parse_docstring(func)
        description = description or self.docstring["description"]

        if options is None:
            options = expand_params(self)

        self.option = Option(
            name=self.name,
            description=description or "-",
            type=OptionType.sub_command,
            options=options,
        )
        self.name = self.option.name
        self.qualified_name = ""

    @property
    def body(self) -> Option:
        return self.option

    async def _call_autocompleter(
        self, param: str, inter: ApplicationCommandInteraction, user_input: str
    ) -> Optional[Choices]:
        return await _call_autocompleter(self, param, inter, user_input)

    async def invoke(self, inter: ApplicationCommandInteraction, *args, **kwargs) -> None:
        if self.guild_only and inter.guild_id is None:
            await inter.response.send_message("This command cannot be used in DMs", ephemeral=True)
            return

        for k, v in self.connectors.items():
            if k in kwargs:
                kwargs[v] = kwargs.pop(k)

        await self.prepare(inter)

        try:
            await call_param_func(self.callback, inter, self.cog, **kwargs)
        except CommandError:
            inter.command_failed = True
            raise
        except asyncio.CancelledError:
            inter.command_failed = True
            return
        except Exception as exc:
            inter.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter)  # type: ignore

            await self.call_after_hooks(inter)

    def autocomplete(self, option_name: str) -> Callable[[Callable], Callable]:
        """A decorator that registers an autocomplete function for the specified option.

        Parameters
        ----------
        option_name: :class:`str`
            The name of the slash command option.
        """
        return _autocomplete(self, option_name)


class InvokableSlashCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot slash command.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    ----------
    name: :class:`str`
        The name of the command.
    body: :class:`.SlashCommand`
        An object being registered in the API.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the command is called.
    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_slash_command_error`
        event.
    guild_ids: Optional[List[:class:`int`]]
        The list of IDs of the guilds where the command is synced. ``None`` if this command is global.
    connectors: Dict[:class:`str`, :class:`str`]
        A mapping of option names to function parameter names, mainly for internal processes.
    auto_sync: :class:`bool`
        Whether to automatically register the command.
    """

    def __init__(
        self,
        func,
        *,
        name: str = None,
        description: str = None,
        options: List[Option] = None,
        default_permission: bool = True,
        guild_ids: Sequence[int] = None,
        connectors: Dict[str, str] = None,
        auto_sync: bool = True,
        **kwargs,
    ):
        super().__init__(func, name=name, **kwargs)
        self.connectors: Dict[str, str] = connectors or {}
        self.children: Dict[str, Union[SubCommand, SubCommandGroup]] = {}
        self.auto_sync: bool = auto_sync
        self.guild_ids: Optional[Sequence[int]] = guild_ids
        self.autocompleters: Dict[str, Any] = kwargs.get("autocompleters", {})

        self.docstring = utils.parse_docstring(func)
        description = description or self.docstring["description"]

        if options is None:
            options = expand_params(self)

        self.body: SlashCommand = SlashCommand(
            name=self.name,
            description=description or "-",
            options=options or [],
            default_permission=default_permission,
        )
        # `SlashCommand.__init__` converts names to lowercase, need to use that name here as well
        self.qualified_name = self.name = self.body.name

    @property
    def description(self) -> str:
        return self.body.description

    @property
    def options(self) -> List[Option]:
        return self.body.options

    @property
    def default_permission(self) -> bool:
        return self.body.default_permission

    def sub_command(
        self,
        name: str = None,
        description: str = None,
        options: list = None,
        connectors: dict = None,
        **kwargs,
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
            ]
        ],
        SubCommand,
    ]:
        """
        A decorator that creates a subcommand under the base command.

        Parameters
        ----------
        name: :class:`str`
            the name of the subcommand. Defaults to the function name
        description: :class:`str`
            the description of the subcommand
        options: List[:class:`.Option`]
            the options of the subcommand for registration in API
        connectors: Dict[:class:`str`, :class:`str`]
            which function param states for each option. If the name
            of an option already matches the corresponding function param,
            you don't have to specify the connectors. Connectors template:
            ``{"option-name": "param_name", ...}``

        Returns
        -------
        Callable[..., :class:`SubCommand`]
            A decorator that converts the provided method into a :class:`SubCommand`, adds it to the bot, then returns it.
        """

        def decorator(
            func: Union[
                Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
            ]
        ) -> SubCommand:
            if len(self.children) == 0 and len(self.body.options) > 0:
                self.body.options = []
            new_func = SubCommand(
                func,
                name=name,
                description=description,
                options=options,
                connectors=connectors,
                **kwargs,
            )
            new_func.qualified_name = f"{self.qualified_name} {new_func.name}"
            self.children[new_func.name] = new_func
            self.body.options.append(new_func.option)
            return new_func

        return decorator

    def sub_command_group(
        self, name: str = None, **kwargs
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
            ]
        ],
        SubCommandGroup,
    ]:
        """
        A decorator that creates a subcommand group under the base command.

        Parameters
        ----------
        name : :class:`str`
            the name of the subcommand group. Defaults to the function name

        Returns
        -------
        Callable[..., :class:`SubCommandGroup`]
            A decorator that converts the provided method into a :class:`SubCommandGroup`, adds it to the bot, then returns it.
        """

        def decorator(
            func: Union[
                Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
                Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
            ]
        ) -> SubCommandGroup:
            if len(self.children) == 0 and len(self.body.options) > 0:
                self.body.options = []
            new_func = SubCommandGroup(func, name=name, **kwargs)
            new_func.qualified_name = f"{self.qualified_name} {new_func.name}"
            self.children[new_func.name] = new_func
            self.body.options.append(new_func.option)
            return new_func

        return decorator

    def autocomplete(self, option_name: str) -> Callable[[Callable], Callable]:
        """
        A decorator that registers an autocomplete function for the specified option.

        Parameters
        ----------
        option_name: :class:`str`
            The name of the slash command option.
        """
        return _autocomplete(self, option_name)

    async def _call_external_error_handlers(
        self, inter: ApplicationCommandInteraction, error: CommandError
    ) -> None:
        stop_propagation = False
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_slash_command_error)
                if local is not None:
                    stop_propagation = await local(inter, error)
                    # User has an option to cancel the global error handler by returning True
        finally:
            if stop_propagation:
                return
            inter.bot.dispatch("slash_command_error", inter, error)  # type: ignore

    async def _call_autocompleter(
        self, param: str, inter: ApplicationCommandInteraction, user_input: str
    ) -> Optional[Choices]:
        return await _call_autocompleter(self, param, inter, user_input)

    async def _call_relevant_autocompleter(self, inter: ApplicationCommandInteraction) -> None:
        chain, _ = inter.data._get_chain_and_kwargs()

        if len(chain) == 0:
            subcmd = None
        elif len(chain) == 1:
            subcmd = self.children.get(chain[0])
        elif len(chain) == 2:
            group = self.children.get(chain[0])
            assert isinstance(group, SubCommandGroup)
            subcmd = group.children.get(chain[1]) if group is not None else None
        else:
            raise ValueError("Command chain is too long")

        focused_option = inter.data.focused_option

        if subcmd is None or isinstance(subcmd, SubCommandGroup):
            call_autocompleter = self._call_autocompleter
        else:
            call_autocompleter = subcmd._call_autocompleter

        choices = await call_autocompleter(focused_option.name, inter, focused_option.value)

        if choices is not None:
            await inter.response.autocomplete(choices=choices)

    async def invoke_children(self, inter: ApplicationCommandInteraction):
        chain, kwargs = inter.data._get_chain_and_kwargs()

        if len(chain) == 0:
            group = None
            subcmd = None
        elif len(chain) == 1:
            group = None
            subcmd = self.children.get(chain[0])
        elif len(chain) == 2:
            group = self.children.get(chain[0])
            assert isinstance(group, SubCommandGroup)
            subcmd = group.children.get(chain[1]) if group is not None else None
        else:
            raise ValueError("Command chain is too long")

        if group is not None:
            try:
                await group.invoke(inter)
            except CommandError as exc:
                if not await group._call_local_error_handler(inter, exc):
                    raise

        if subcmd is not None:
            try:
                await subcmd.invoke(inter, **kwargs)
            except CommandError as exc:
                if not await subcmd._call_local_error_handler(inter, exc):
                    raise

    async def invoke(self, inter: ApplicationCommandInteraction):
        if self.guild_only and inter.guild_id is None:
            await inter.response.send_message("This command cannot be used in DMs", ephemeral=True)
            return

        await self.prepare(inter)

        try:
            if len(self.children) > 0:
                await self(inter)
                await self.invoke_children(inter)
            else:
                kwargs = inter.filled_options
                for k, v in self.connectors.items():
                    if k in kwargs:
                        kwargs[v] = kwargs.pop(k)
                await call_param_func(self.callback, inter, self.cog, **kwargs)
        except CommandError:
            inter.command_failed = True
            raise
        except asyncio.CancelledError:
            inter.command_failed = True
            return
        except Exception as exc:
            inter.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter)  # type: ignore

            await self.call_after_hooks(inter)


def slash_command(
    *,
    name: str = None,
    description: str = None,
    options: List[Option] = None,
    default_permission: bool = True,
    guild_ids: Sequence[int] = None,
    connectors: Dict[str, str] = None,
    auto_sync: bool = True,
    **kwargs,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ],
    InvokableSlashCommand,
]:
    """A decorator that builds a slash command.

    Parameters
    ----------
    auto_sync: :class:`bool`
        Whether to automatically register the command. Defaults to ``True``
    name: :class:`str`
        The name of the slash command. (equals to function name by default).
    description: :class:`str`
        The description of the slash command. It will be visible in Discord.
    options: List[:class:`.Option`]
        The list of slash command options. The options will be visible in Discord.
        This is the old way of specifying options. Consider using :ref:`param_syntax` instead.
    default_permission: :class:`bool`
        Whether the command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    guild_ids: List[:class:`int`]
        If specified, the client will register a command in these guilds.
        Otherwise this command will be registered globally in ~1 hour.
    connectors: Dict[:class:`str`, :class:`str`]
        Binds function names to option names. If the name
        of an option already matches the corresponding function param,
        you don't have to specify the connectors. Connectors template:
        ``{"option-name": "param_name", ...}``.
        If you're using :ref:`param_syntax`, you don't need to specify this.

    Returns
    -------
    Callable[..., :class:`InvokableSlashCommand`]
        A decorator that converts the provided method into an InvokableSlashCommand and returns it.
    """

    def decorator(
        func: Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ) -> InvokableSlashCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"<{func.__qualname__}> must be a coroutine function")
        if hasattr(func, "__command_flag__"):
            raise TypeError("Callback is already a command.")
        if guild_ids and not all(isinstance(guild_id, int) for guild_id in guild_ids):
            raise ValueError("guild_ids must be a sequence of int.")
        return InvokableSlashCommand(
            func,
            name=name,
            description=description,
            options=options,
            default_permission=default_permission,
            guild_ids=guild_ids,
            connectors=connectors,
            auto_sync=auto_sync,
            **kwargs,
        )

    return decorator
