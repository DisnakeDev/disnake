from typing import Any, Literal

import disnake
from disnake.ext import commands

bot = commands.Bot("!")

conn: Any = ...  # a placeholder for an actual database connection

# Instead of repeating boiler-plate code you may use injections
# Here we give each command a config and a few options in case they're not set
# very useful with sub commands


class Config:
    locale: str = "en-us"
    timezone: str = "UTC"
    theme: str = "dark"


async def get_config(
    inter: disnake.ApplicationCommandInteraction,
    locale: str = None,
    timezone: str = None,
    theme: str = None,
) -> Config:
    config: Config = await conn.get_user_config(inter.author.id)

    if locale:
        config.locale = locale
    if timezone:
        config.timezone = timezone
    if theme:
        config.theme = theme

    return config


@bot.slash_command()
async def injected1(
    inter: disnake.ApplicationCommandInteraction,
    number: int,
    config: Config = commands.inject(get_config),
):
    ...


@bot.slash_command()
async def injected2(
    inter: disnake.ApplicationCommandInteraction,
    string: str,
    config: Config = commands.inject(get_config),
):
    ...


# If the injection returns a custom object and has a return type annotation
# then even the inject can be left out of the commands
class GameUser:
    username: str
    level: int
    ...


@commands.register_injection
async def get_game_user(
    inter: disnake.ApplicationCommandInteraction,
    user: str = None,
    server: Literal["eu", "us", "cn"] = None,
) -> GameUser:
    if user is None:
        return await conn.get_game_user(id=inter.author.id)

    return await conn.search_user(username=user, server=server)


@bot.slash_command()
async def implicit_injection(inter: disnake.ApplicationCommandInteraction, user: GameUser):
    ...
