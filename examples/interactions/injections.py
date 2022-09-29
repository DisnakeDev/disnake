# SPDX-License-Identifier: MIT

import os
from dataclasses import dataclass
from typing import Any, Literal, Optional

import disnake

# this file uses pytz in one of its examples but it is completely optional
import pytz
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)

# Instead of repeating boiler-plate code you may use injections.
# Here we give each command a config with a few default options.


@dataclass
class Config:
    locale: str
    timezone: pytz.BaseTzInfo
    theme: str


async def get_config(
    inter: disnake.CommandInteraction,
    locale: Optional[str] = None,
    timezone: str = "UTC",
    theme: Literal["light", "dark", "amoled"] = "dark",
) -> Config:
    """Let the user enter a config

    Note:
        The docstring description of injections does not show up in the final command description,
        only the option descriptions matter.

    Parameters
    ----------
    locale: The prefered locale, defaults to the server's locale
    timezone: Your current timezone, must be in the format of "US/Eastern" or "Europe/London"
    theme: Your prefered theme, defaults to the dark theme
    """
    # if a locale is not provided use the guild's locale
    if locale is None:
        locale = str(inter.guild_locale or "en-US")

    # parse a timezone from a string using pytz (maybe even use the locale if you feel like it)
    tzinfo = pytz.timezone(timezone)

    return Config(locale, tzinfo, theme)


# Note that the following command will have 4 options:
# `number`, `locale`, `timezone` and `theme`.
# `config` will be whatever `get_config()` returns.
@bot.slash_command()
async def injected1(
    inter: disnake.CommandInteraction,
    number: int,
    config: Config = commands.inject(get_config),
):
    """A command which takes in a number and some config parameters

    Parameters
    ----------
    number: A number
    """


@bot.slash_command()
async def injected2(
    inter: disnake.CommandInteraction,
    string: str,
    config: Config = commands.inject(get_config),
):
    """A command which takes in a string and some config parameters

    Parameters
    ----------
    string: A string
    """


# If the injection returns a custom type and has a return type annotation,
# then `commands.inject()` can be left out of the command signature,
# and `@register_injection` can be used instead.

# This stores the injection callback in an internal registry,
# which allows you to use just `user: GameUser` in the command signature.


class GameUser:
    username: str
    level: int
    ...


@commands.register_injection
async def get_game_user(
    inter: disnake.CommandInteraction,
    user: Optional[str] = None,
    server: Optional[Literal["eu", "us", "cn"]] = None,
) -> GameUser:
    """Search a game user from the database

    Parameters
    ----------
    user: The username of the user, uses the author by default
    server: The server to search
    """
    db: Any = ...  # a placeholder for an actual database connection

    if user is None:
        return await db.get_game_user(id=inter.author.id)

    game_user: GameUser = await db.search_game_user(username=user, server=server)
    if game_user is None:
        raise commands.CommandError(f"User with username {user!r} could not be found")

    return game_user


@bot.slash_command()
async def implicit_injection(inter: disnake.CommandInteraction, user: GameUser):
    """A command which uses an implicit injection"""


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
