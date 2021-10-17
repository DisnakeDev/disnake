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
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional, TypeVar, Union, Sequence

from .base_core import InvokableApplicationCommand, _get_overridden_method
from .errors import *

from disnake.app_commands import UserCommand, MessageCommand

import asyncio

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec
    from disnake.interactions import ApplicationCommandInteraction

    ApplicationCommandInteractionT = TypeVar(
        "ApplicationCommandInteractionT", bound=ApplicationCommandInteraction, covariant=True
    )
    from .cog import CogT

    P = ParamSpec("P")

__all__ = ("InvokableUserCommand", "InvokableMessageCommand", "user_command", "message_command")


class InvokableUserCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot user command (context menu).

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    -----------
    name: :class:`str`
        The name of the user command.
    body: :class:`UserCommand`
        An object being registered in the API.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the user command is called.
    cog: Optional[:class:`Cog`]
        The cog that this user command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_user_command_error`
        event.
    guild_ids: Optional[List[:class:`int`]]
        The list of IDs of the guilds where the command is synced. ``None`` if this command is global.
    auto_sync: :class:`bool`
        Whether to sync the command in the API with ``body`` or not.
    """

    def __init__(self, func, *, name: str = None, default_permission: bool = True, guild_ids: Sequence[int] = None, auto_sync: bool = True, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: Optional[Sequence[int]] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = UserCommand(name=self.name, default_permission=default_permission)

    async def _call_external_error_handlers(self, inter: ApplicationCommandInteraction, error: CommandError) -> None:
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_user_command_error)
                if local is not None:
                    await local(inter, error)
        finally:
            inter.bot.dispatch("user_command_error", inter, error)

    async def __call__(self, inter: ApplicationCommandInteraction, target: Any = None, *args, **kwargs) -> None:
        # the target may just not be passed in
        target = target or inter.target
        try:
            await super().__call__(inter, *args, **kwargs)
        except TypeError as e:
            if e.args and e.args[0].startswith(f"{self.callback.__name__}() takes "):
                await super().__call__(inter, target, *args, **kwargs)
            else:
                raise


class InvokableMessageCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot message command (context menu).

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    -----------
    name: :class:`str`
        The name of the message command.
    body: :class:`MessageCommand`
        An object being registered in the API.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the message command is called.
    cog: Optional[:class:`Cog`]
        The cog that this message command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_message_command_error`
        event.
    guild_ids: Optional[List[:class:`int`]]
        The list of IDs of the guilds where the command is synced. ``None`` if this command is global.
    auto_sync: :class:`bool`
        Whether to sync the command in the API with ``body`` or not.
    """

    def __init__(self, func, *, name: str = None, default_permission: bool = True, guild_ids: Sequence[int] = None, auto_sync: bool = True, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: Optional[Sequence[int]] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = MessageCommand(name=self.name, default_permission=default_permission)

    async def _call_external_error_handlers(self, inter: ApplicationCommandInteraction, error: CommandError) -> None:
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_message_command_error)
                if local is not None:
                    await local(inter, error)
        finally:
            inter.bot.dispatch("message_command_error", inter, error)

    async def __call__(self, inter: ApplicationCommandInteraction, target: Any = None, *args, **kwargs) -> None:
        # the target may just not be passed in
        target = target or inter.target
        try:
            await super().__call__(inter, *args, **kwargs)
        except TypeError as e:
            if e.args and e.args[0].startswith(f"{self.callback.__name__}() takes "):
                await super().__call__(inter, target, *args, **kwargs)
            else:
                raise


def user_command(
    *, name: str = None, default_permission: bool = True, guild_ids: Sequence[int] = None, auto_sync: bool = True, **kwargs
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ],
    InvokableUserCommand,
]:
    """
    A shortcut decorator that builds a user command.

    Parameters
    ----------
    auto_sync: :class:`bool`
        whether to automatically register / edit the command or not. Defaults to ``True``
    name: :class:`str`
        name of the user command you want to respond to (equals to function name by default).
    guild_ids: List[:class:`int`]
        if specified, the client will register the command in these guilds.
        Otherwise this command will be registered globally in ~1 hour.

    Returns
    --------
    Callable[..., :class:`InvokableUserCommand`]
        A decorator that converts the provided method into a InvokableUserCommand and returns it.
    """

    def decorator(
        func: Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ) -> InvokableUserCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"<{func.__qualname__}> must be a coroutine function")
        if hasattr(func, "__command_flag__"):
            raise TypeError("Callback is already a command.")
        return InvokableUserCommand(func, name=name, default_permission=default_permission, guild_ids=guild_ids, auto_sync=auto_sync, **kwargs)

    return decorator


def message_command(
    *, name: str = None, default_permission: bool = True, guild_ids: Sequence[int] = None, auto_sync: bool = True, **kwargs
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ],
    InvokableMessageCommand,
]:
    """
    A decorator that builds a message command.

    Parameters
    ----------
    auto_sync: :class:`bool`
        whether to automatically register / edit the command or not. Defaults to ``True``
    name: :class:`str`
        name of the message command you want to respond to (equals to function name by default).
    guild_ids: List[:class:`int`]
        if specified, the client will register the command in these guilds.
        Otherwise this command will be registered globally in ~1 hour.

    Returns
    --------
    Callable[..., :class:`InvokableMessageCommand`]
        A decorator that converts the provided method into a InvokableMessageCommand and then returns it.
    """

    def decorator(
        func: Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ) -> InvokableMessageCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"<{func.__qualname__}> must be a coroutine function")
        if hasattr(func, "__command_flag__"):
            raise TypeError("Callback is already a command.")
        return InvokableMessageCommand(func, name=name, default_permission=default_permission, guild_ids=guild_ids, auto_sync=auto_sync, **kwargs)

    return decorator
