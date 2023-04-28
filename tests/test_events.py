# SPDX-License-Identifier: MIT

from typing import Any, Coroutine

import pytest
from typing_extensions import assert_type

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


def _test_typing_wait_for(client: disnake.Client, bot: commands.Bot) -> None:
    expected_type = Coroutine[Any, Any, disnake.Guild]

    # valid enum event
    _ = assert_type(client.wait_for(Event.guild_join), expected_type)
    _ = assert_type(client.wait_for(Event.guild_join, check=lambda g: True), expected_type)

    # valid str event
    _ = assert_type(client.wait_for("guild_join"), expected_type)
    _ = assert_type(client.wait_for("guild_join", check=lambda g: True), expected_type)

    # invalid check type
    _ = client.wait_for(Event.guild_join, check=lambda: True)  # type: ignore
    # n.b. this one isn't ideal, but there's no way to prevent type-checkers from using the fallback in this case
    _ = assert_type(client.wait_for("guild_join", check=lambda: True), Coroutine[Any, Any, Any])

    # bot-specific events
    _ = client.wait_for(Event.slash_command_error)  # type: ignore  # this should error
    _ = assert_type(
        bot.wait_for(Event.slash_command),
        Coroutine[Any, Any, disnake.ApplicationCommandInteraction],
    )


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
