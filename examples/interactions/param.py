# SPDX-License-Identifier: MIT

"""Some examples showing how to customize slash command options."""

import os
from typing import Union

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# disnake will parse the signatures of commands,
# using the annotations for determining option types,
# and automatically handling default values.
# On top of that, using `Param` adds support for many other features.


# We create a new command named "simple" with two options:
# "required" (a required string) and "optional" (an optional integer).
@bot.slash_command()
async def simple(
    inter: disnake.CommandInteraction,
    required: str,
    optional: int = 0,
):
    ...


# builtins are not the only types supported.
# You can also use various other types like User, Member, Role, TextChannel, Emoji, ...,
# as well as `Union`s of those types in many cases (see the documentation for more details).
@bot.slash_command()
async def other_types(
    inter: disnake.CommandInteraction,
    user: disnake.User,
    emoji: disnake.Emoji,
    member_or_role: Union[disnake.Member, disnake.Role],
):
    ...


# Adding descriptions to the command itself and to its options is
# easy through the use of docstrings, which will be parsed automatically.
@bot.slash_command()
async def description(
    inter: disnake.CommandInteraction,
    user: disnake.User,
    channel: disnake.TextChannel,
):
    """A random command

    Parameters
    ----------
    user: A random user
    channel: A random channel
    """


# To make an option optional, you can simply give it a default value.
# If you'd like to dynamically compute a default value, you can do so
# by using `Param` and passing a callable.
@bot.slash_command()
async def defaults(
    inter: disnake.CommandInteraction,
    string: str = "this is a default value",
    user: disnake.User = commands.Param(lambda inter: inter.author),
):
    ...


# You may limit numbers to a certain range using `commands.Range`.
# "..." is impicitly infinity. Range[0, ...] therefore means any integer from 0 to infinity,
# and Range[..., 0] means anything from -inf to 0.


# The 1.0 in the `fraction` parameter below is important - the usage of a float specifies
# that the argument may be a float in that range, not just an integer.
# All of these bounds are inclusive, meaning `Range[1, 4]` would allow any of 1, 2, 3, or 4.
@bot.slash_command()
async def ranges(
    inter: disnake.CommandInteraction,
    ranking: commands.Range[1, 10],
    negative: commands.Range[..., 0],
    fraction: commands.Range[0, 1.0],
):
    """Command with limited ranges

    Parameters
    ----------
    ranking: An integer between 1 and 10
    negative: An integer lower than 0
    fraction: A floating point number between 0 and 1
    """


# Since Discord only allows numbers between -2^53 and 2^53,
# using `commands.LargeInt` allows you to use larger numbers.
# This results in the slash command using a string option, which will be
# converted to an integer locally, allowing for a wider range of numbers.
@bot.slash_command()
async def large(inter: disnake.CommandInteraction, largenumber: commands.LargeInt):
    ...


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
