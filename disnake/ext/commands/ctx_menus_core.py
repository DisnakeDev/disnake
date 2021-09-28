from __future__ import annotations
from typing import List, TYPE_CHECKING, Callable, Coroutine, Optional, TypeVar, Union

from .base_core import InvokableApplicationCommand, _get_overridden_method
from .errors import *

from disnake.app_commands import UserCommand, MessageCommand

import asyncio

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec
    from disnake.interactions import ApplicationCommandInteraction
    
    ApplicationCommandInteractionT = TypeVar('ApplicationCommandInteractionT', bound=ApplicationCommandInteraction, covariant=True)
    from .cog import CogT

    P = ParamSpec('P')

__all__ = (
    'InvokableUserCommand',
    'InvokableMessageCommand',
    'user_command',
    'message_command'
)


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

    def __init__(self, func, *, name: str, guild_ids: List[int] = None, auto_sync: bool = True, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: Optional[List[int]] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = UserCommand(name=self.name)
    
    async def _call_external_error_handlers(self, inter: ApplicationCommandInteraction, error: CommandError) -> None:
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_user_command_error)
                if local is not None:
                    await local(inter, error)
        finally:
            inter.bot.dispatch('user_command_error', inter, error)


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

    def __init__(self, func, *, name: str, guild_ids: List[int] = None, auto_sync: bool = True, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: Optional[List[int]] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = MessageCommand(name=self.name)

    async def _call_external_error_handlers(self, inter: ApplicationCommandInteraction, error: CommandError) -> None:
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_message_command_error)
                if local is not None:
                    await local(inter, error)
        finally:
            inter.bot.dispatch('message_command_error', inter, error)


def user_command(
    *,
    name: str = None,
    guild_ids: List[int] = None,
    auto_sync: bool = True,
    **kwargs
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
        ]
    ],
    InvokableUserCommand
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
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
        ]
    ) -> InvokableUserCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f'<{func.__qualname__}> must be a coroutine function')
        if hasattr(func, '__command_flag__'):
            raise TypeError('Callback is already a command.')
        return InvokableUserCommand(
            func,
            name=name,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            **kwargs
        )
    return decorator


def message_command(
    *,
    name: str = None,
    guild_ids: List[int] = None,
    auto_sync: bool = True,
    **kwargs
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ApplicationCommandInteractionT, P], Coroutine],
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
        ]
    ],
    InvokableMessageCommand
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
            Callable[Concatenate[ApplicationCommandInteractionT, P], Coroutine]
        ]
    ) -> InvokableMessageCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f'<{func.__qualname__}> must be a coroutine function')
        if hasattr(func, '__command_flag__'):
            raise TypeError('Callback is already a command.')
        return InvokableMessageCommand(
            func,
            name=name,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            **kwargs
        )
    return decorator
