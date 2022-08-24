import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# Disnake can use annotations to create slash commands.
# That means instead of using the options keyword you will be
# setting the default of your parameters.
# It should allow you to create more readable commands and make the more complicated
# features easier to use.
# Not only that but using Param even adds support for a ton of other features.

# We create a new command named "simple" with two options: "required" (a required string) and "optional" (an integer).
# disnake takes care of parsing the annotation and adding a description for it.
@bot.slash_command()
async def simple(
    inter: disnake.CommandInteraction,
    required: str,
    optional: int = 0,
):
    ...


# builtins are not the only types supported.
# You can also use various other types like User, Member, Role, TextChannel, Emoji, ...
@bot.slash_command()
async def other_types(
    inter: disnake.CommandInteraction,
    user: disnake.User,
    emoji: disnake.Emoji,
):
    ...


# Adding descriptions is very simple, just use the docstring
@bot.slash_command()
async def description(inter: disnake.CommandInteraction, user: disnake.User):
    """A random command"""


# Options can also be added into the docstring
@bot.slash_command()
async def full_description(
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


# To make an option optional you can simply give it a default value.
# In case the default value is supposed to be callable you should use commands.Param
# This is so the annotation actually stays correct.
@bot.slash_command()
async def defaults(
    inter: disnake.CommandInteraction,
    string: str = None,
    user: disnake.User = commands.Param(lambda inter: inter.author),
):
    ...


# You may limit numbers into a certain range using commands.Range
# "..." is impicitly infinity. Range[0, ...] therefore means any integer from 0 to infinity and Range[..., 0] means from -inf to 0
# The 1.0 in fraction is very important, the usage of a float says that the argument may be any float in that range.
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


# You can also allow large numbers with commands.LargeInt.
# Since Discord only allows numbers between -2^53 and 2^53, this allows you to use larger numbers.
@bot.slash_command()
async def large(inter: disnake.CommandInteraction, largenumber: commands.LargeInt):
    ...


bot.run(os.getenv("BOT_TOKEN"))
