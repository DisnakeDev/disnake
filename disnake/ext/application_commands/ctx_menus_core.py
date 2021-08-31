from __future__ import annotations
from typing import List
from .base_core import InvokableApplicationCommand

from ..commands.errors import *

from discord.app_commands import UserCommand, MessageCommand
from discord._hub import _ApplicationCommandStore

import asyncio

__all__ = (
    'InvokableUserCommand',
    'InvokableMessageCommand',
    'user_command',
    'message_command'
)


class InvokableUserCommand(InvokableApplicationCommand):
    def __init__(self, func, *, name: str, guild_ids: List[int] = None, auto_sync: bool = True, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: List[int] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = UserCommand(name=self.name)


class InvokableMessageCommand(InvokableApplicationCommand):
    def __init__(self, func, *, name: str, guild_ids: List[int] = None, auto_sync: bool = True, **kwargs):
        super().__init__(func, name=name, **kwargs)
        self.guild_ids: List[int] = guild_ids
        self.auto_sync: bool = auto_sync
        self.body = MessageCommand(name=self.name)


def user_command(
    *,
    name: str = None,
    guild_ids: List[int] = None,
    auto_sync: bool = True,
    **kwargs
) -> InvokableUserCommand:
    """
    A decorator that builds a user command.

    Parameters
    ----------
    auto_sync: :class:`bool`
        whether to automatically register the command or not. Defaults to ``True``
    name: :class:`str`
        name of the user command you want to respond to (equals to function name by default).
    guild_ids: List[:class:`int`]
        if specified, the client will register the command in these guilds.
        Otherwise this command will be registered globally.
    """

    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f'<{func.__qualname__}> must be a coroutine function')
        new_func = InvokableUserCommand(
            func,
            name=name,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            **kwargs
        )
        _ApplicationCommandStore.user_commands[new_func.name] = new_func
        return new_func
    return decorator


def message_command(
    *,
    name: str = None,
    guild_ids: List[int] = None,
    auto_sync: bool = True,
    **kwargs
) -> InvokableMessageCommand:
    """
    A decorator that builds a message command.

    Parameters
    ----------
    auto_sync: :class:`bool`
        whether to automatically register the command or not. Defaults to ``True``
    name: :class:`str`
        name of the message command you want to respond to (equals to function name by default).
    guild_ids: List[:class:`int`]
        if specified, the client will register the command in these guilds.
        Otherwise this command will be registered globally.
    """

    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f'<{func.__qualname__}> must be a coroutine function')
        new_func = InvokableMessageCommand(
            func,
            name=name,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            **kwargs
        )
        _ApplicationCommandStore.message_commands[new_func.name] = new_func
        return new_func
    return decorator
