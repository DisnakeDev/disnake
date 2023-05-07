# SPDX-License-Identifier: MIT

from typing import Any

import pytest

import disnake
from disnake import Event
from disnake.ext import commands

# n.b. the specific choice of events used in this file is irrelevant


@pytest.fixture
def client():
    return disnake.Client()


@pytest.fixture
def bot():
    return commands.Bot(
        command_prefix=commands.when_mentioned,
        command_sync_flags=commands.CommandSyncFlags.none(),
    )


# @Client.event


def test_client_event(client: disnake.Client) -> None:
    assert not hasattr(client, "on_message_edit")

    @client.event
    async def on_message_edit(self, *args: Any) -> None:
        ...

    assert client.on_message_edit is on_message_edit  # type: ignore


# Bot.wait_for


@pytest.mark.parametrize("event", ["thread_create", Event.thread_create])
def test_wait_for(bot: commands.Bot, event) -> None:
    coro = bot.wait_for(event)
    assert len(bot._listeners["thread_create"]) == 1
    coro.close()  # close coroutine to avoid warning


# Bot.add_listener / Bot.remove_listener


@pytest.mark.parametrize("event", ["on_guild_remove", Event.guild_remove])
def test_addremove_listener(bot: commands.Bot, event) -> None:
    async def callback(self, *args: Any) -> None:
        ...

    bot.add_listener(callback, event)
    assert len(bot.extra_events["on_guild_remove"]) == 1

    bot.remove_listener(callback, event)
    assert len(bot.extra_events["on_guild_remove"]) == 0


def test_addremove_listener__implicit(bot: commands.Bot) -> None:
    async def on_guild_remove(self, *args: Any) -> None:
        ...

    bot.add_listener(on_guild_remove)
    assert len(bot.extra_events["on_guild_remove"]) == 1

    bot.remove_listener(on_guild_remove)
    assert len(bot.extra_events["on_guild_remove"]) == 0


# @Bot.listen


@pytest.mark.parametrize("event", ["on_guild_role_create", Event.guild_role_create])
def test_listen(bot: commands.Bot, event) -> None:
    @bot.listen(event)
    async def callback(self, *args: Any) -> None:
        ...

    assert len(bot.extra_events["on_guild_role_create"]) == 1


def test_listen__implicit(bot: commands.Bot) -> None:
    @bot.listen()
    async def on_guild_role_create(self, *args: Any) -> None:
        ...

    assert len(bot.extra_events["on_guild_role_create"]) == 1


# @commands.Cog.listener


@pytest.mark.parametrize("event", ["on_automod_rule_update", Event.automod_rule_update])
def test_listener(bot: commands.Bot, event) -> None:
    class Cog(commands.Cog):
        @commands.Cog.listener(event)
        async def callback(self, *args: Any) -> None:
            ...

    bot.add_cog(Cog())
    assert len(bot.extra_events["on_automod_rule_update"]) == 1


def test_listener__implicit(bot: commands.Bot) -> None:
    class Cog(commands.Cog):
        @commands.Cog.listener()
        async def on_automod_rule_update(self, *args: Any) -> None:
            ...

    bot.add_cog(Cog())
    assert len(bot.extra_events["on_automod_rule_update"]) == 1
