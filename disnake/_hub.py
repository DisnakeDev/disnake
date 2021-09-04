from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple


if TYPE_CHECKING:
    from .ext.commands import (
        InvokableApplicationCommand,
        InvokableSlashCommand,
        InvokableUserCommand,
        InvokableMessageCommand
    )
    from disnake.app_commands import ApplicationCommand


def _get_all_commands() -> List[InvokableApplicationCommand]:
    all_commands = []
    for cmd in _ApplicationCommandStore.slash_commands.values():
        all_commands.append(cmd)
    for cmd in _ApplicationCommandStore.user_commands.values():
        all_commands.append(cmd)
    for cmd in _ApplicationCommandStore.message_commands.values():
        all_commands.append(cmd)
    return all_commands


def _ordered_unsynced_commands(
    test_guilds: List[int] = None
) -> Tuple[List[ApplicationCommand], Dict[int, List[ApplicationCommand]]]:
    global_cmds = []
    guilds = {}
    all_commands = _get_all_commands()
    for cmd in all_commands:
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


class _ApplicationCommandStore:
    # I feel like this is a terrible solution,
    # but I don't know any exact reasons why.
    # If you know them, please tell me.
    slash_commands: Dict[str, InvokableSlashCommand] = {}
    user_commands: Dict[str, InvokableUserCommand] = {}
    message_commands: Dict[str, InvokableMessageCommand] = {}
