# SPDX-License-Identifier: MIT

from typing import Any

import pytest

from disnake import Event
from disnake.ext import commands


@pytest.fixture
def bot():
    return commands.Bot(command_prefix=commands.when_mentioned)


# @Client.event


@pytest.mark.parametrize("event", ["message_edit", Event.message_edit])
def test_wait_for(bot: commands.Bot, event) -> None:
    coro = bot.wait_for(event)
    assert len(bot._listeners["message_edit"]) == 1
    coro.close()  # close coroutine to avoid warning


# Bot.add_listener / Bot.remove_listener


@pytest.mark.parametrize("event", ["on_message_edit", Event.message_edit])
def test_addremove_listener(bot: commands.Bot, event) -> None:
    async def callback(self, *args: Any) -> None:
        ...

    bot.add_listener(callback, event)
    assert len(bot.extra_events["on_message_edit"]) == 1

    bot.remove_listener(callback, event)
    assert len(bot.extra_events["on_message_edit"]) == 0


def test_addremove_listener__implicit(bot: commands.Bot) -> None:
    async def on_message_edit(self, *args: Any) -> None:
        ...

    bot.add_listener(on_message_edit)
    assert len(bot.extra_events["on_message_edit"]) == 1

    bot.remove_listener(on_message_edit)
    assert len(bot.extra_events["on_message_edit"]) == 0


# @Bot.listen


@pytest.mark.parametrize("event", ["on_message_edit", Event.message_edit])
def test_listen(bot: commands.Bot, event) -> None:
    @bot.listen(event)
    async def callback(self, *args: Any) -> None:
        ...

    assert len(bot.extra_events["on_message_edit"]) == 1


def test_listen__implicit(bot: commands.Bot) -> None:
    @bot.listen()
    async def on_message_edit(self, *args: Any) -> None:
        ...

    assert len(bot.extra_events["on_message_edit"]) == 1


# @commands.Cog.listener


@pytest.mark.parametrize("event", ["on_message_edit", Event.message_edit])
def test_listener(bot: commands.Bot, event) -> None:
    class Cog(commands.Cog):
        @commands.Cog.listener(event)
        async def callback(self, *args: Any) -> None:
            ...

    bot.add_cog(Cog())
    assert len(bot.extra_events["on_message_edit"]) == 1


def test_listener__implicit(bot: commands.Bot) -> None:
    class Cog(commands.Cog):
        @commands.Cog.listener()
        async def on_message_edit(self, *args: Any) -> None:
            ...

    bot.add_cog(Cog())
    assert len(bot.extra_events["on_message_edit"]) == 1
