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
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional, Sequence, TypeVar, Union

from disnake.app_commands import MessageCommand, UserCommand

from .base_core import InvokableApplicationCommand, _get_overridden_method
from .errors import *
from .params import safe_call

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
    ----------
    name: :class:`str`
        The name of the user command.
    body: :class:`.UserCommand`
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
        Whether to automatically register the command.
    """

    def __init__(
        self,
        func,
        *,
        name: str = None,
        default_permission: bool = True,
        guild_ids: Sequence[int] = None,
        auto_sync: bool = True,
        **kwargs,
    ):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: Optional[Sequence[int]] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = UserCommand(name=self.name, default_permission=default_permission)

    async def _call_external_error_handlers(
        self, inter: ApplicationCommandInteraction, error: CommandError
    ) -> None:
        stop_propagation = False
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_user_command_error)
                if local is not None:
                    stop_propagation = await local(inter, error)
                    # User has an option to cancel the global error handler by returning True
        finally:
            if stop_propagation:
                return
            inter.bot.dispatch("user_command_error", inter, error)

    async def __call__(
        self, interaction: ApplicationCommandInteraction, target: Any = None, *args, **kwargs
    ) -> None:
        # the target may just not be passed in
        args = (target or interaction.target,) + args
        if self.cog is not None:
            await safe_call(self.callback, self.cog, interaction, *args, **kwargs)
        else:
            await safe_call(self.callback, interaction, *args, **kwargs)


class InvokableMessageCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot message command (context menu).

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    ----------
    name: :class:`str`
        The name of the message command.
    body: :class:`.MessageCommand`
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
        Whether to automatically register the command.
    """

    def __init__(
        self,
        func,
        *,
        name: str = None,
        default_permission: bool = True,
        guild_ids: Sequence[int] = None,
        auto_sync: bool = True,
        **kwargs,
    ):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: Optional[Sequence[int]] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = MessageCommand(name=self.name, default_permission=default_permission)

    async def _call_external_error_handlers(
        self, inter: ApplicationCommandInteraction, error: CommandError
    ) -> None:
        stop_propagation = False
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_message_command_error)
                if local is not None:
                    stop_propagation = await local(inter, error)
                    # User has an option to cancel the global error handler by returning True
        finally:
            if stop_propagation:
                return
            inter.bot.dispatch("message_command_error", inter, error)

    async def __call__(
        self, interaction: ApplicationCommandInteraction, target: Any = None, *args, **kwargs
    ) -> None:
        # the target may just not be passed in
        args = (target or interaction.target,) + args
        if self.cog is not None:
            await safe_call(self.callback, self.cog, interaction, *args, **kwargs)
        else:
            await safe_call(self.callback, interaction, *args, **kwargs)


def user_command(
    *,
    name: str = None,
    default_permission: bool = True,
    guild_ids: Sequence[int] = None,
    auto_sync: bool = True,
    **kwargs,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ],
    InvokableUserCommand,
]:
    """A shortcut decorator that builds a user command.

    Parameters
    ----------
    name: :class:`str`
        The name of the user command (defaults to the function name).
    default_permission: :class:`bool`
        Whether the command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    auto_sync: :class:`bool`
        Whether to automatically register the command. Defaults to ``True``.
    guild_ids: Sequence[:class:`int`]
        If specified, the client will register the command in these guilds.
        Otherwise this command will be registered globally in ~1 hour.

    Returns
    -------
    Callable[..., :class:`InvokableUserCommand`]
        A decorator that converts the provided method into an InvokableUserCommand and returns it.
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
        if guild_ids and not all(isinstance(guild_id, int) for guild_id in guild_ids):
            raise ValueError("guild_ids must be a sequence of int.")
        return InvokableUserCommand(
            func,
            name=name,
            default_permission=default_permission,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            **kwargs,
        )

    return decorator


def message_command(
    *,
    name: str = None,
    default_permission: bool = True,
    guild_ids: Sequence[int] = None,
    auto_sync: bool = True,
    **kwargs,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine],
        ]
    ],
    InvokableMessageCommand,
]:
    """A shortcut decorator that builds a message command.

    Parameters
    ----------
    name: :class:`str`
        The name of the message command (defaults to the function name).
    default_permission: :class:`bool`
        Whether the command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    auto_sync: :class:`bool`
        Whether to automatically register the command. Defaults to ``True``.
    guild_ids: Sequence[:class:`int`]
        If specified, the client will register the command in these guilds.
        Otherwise this command will be registered globally in ~1 hour.

    Returns
    -------
    Callable[..., :class:`InvokableMessageCommand`]
        A decorator that converts the provided method into an InvokableMessageCommand and then returns it.
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
        if guild_ids and not all(isinstance(guild_id, int) for guild_id in guild_ids):
            raise ValueError("guild_ids must be a sequence of int.")
        return InvokableMessageCommand(
            func,
            name=name,
            default_permission=default_permission,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            **kwargs,
        )

    return decorator
