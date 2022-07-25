from dataclasses import dataclass
from typing import Any, Literal, Optional

import disnake

# this file uses pytz in one of its examples but it is completely optional
import pytz
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)

# Instead of repeating boiler-plate code you may use injections
# Here we give each command a config and a few options in case they're not set
# very useful with sub commands


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
        The docstring header of injections does not show up in the final command description,
        only the option descriptions matter

    Parameters
    ----------
    locale: The prefered locale, defaults to the server's locale
    timezone: Your current timezone, must be in the format of "US/Eastern" or "Europe/London"
    theme: Your prefered theme, defaults to the dark theme
    """
    # if a locale is not provided use the guild's locale
    if locale is None:
        locale = inter.guild and str(inter.guild.preferred_locale) or "en-US"

    # parse a timezone from a string using pytz (maybe even use the locale if you feel like it)
    tzinfo = pytz.timezone(timezone)

    return Config(locale, tzinfo, theme)


# Note that the following command will have 4 options: `number`, `locale`, `timezone` and `theme`.
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


# If the injection returns a custom object and has a return type annotation
# then even the `commands.inject()` can be left out of the command signature
class GameUser:
    username: str
    level: int
    ...


conn: Any = ...  # a placeholder for an actual database connection


@commands.register_injection
async def get_game_user(
    inter: disnake.CommandInteraction,
    user: str = None,
    server: Literal["eu", "us", "cn"] = None,
) -> GameUser:
    """Search a game user from the database

    Parameters
    ----------
    user: The username of the user, uses the author by default
    server: The server to search
    """
    if user is None:
        return await conn.get_game_user(id=inter.author.id)

    game_user: GameUser = await conn.search_game_user(username=user, server=server)
    if game_user is None:
        raise commands.CommandError(f"User with username {user!r} could not be found")

    return game_user


@bot.slash_command()
async def implicit_injection(inter: disnake.CommandInteraction, user: GameUser):
    """A command which uses an implicit injection"""
