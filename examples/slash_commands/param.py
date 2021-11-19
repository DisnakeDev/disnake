import disnake
from disnake.ext import commands


bot = commands.Bot("!")


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
    inter: disnake.ApplicationCommandInteraction,
    required: str,
    optional: int = 0,
):
    ...


# builtins are not the only types supported.
# You can also use various other types like User, Member, Role, TextChannel, Emoji, ...
@bot.slash_command()
async def other_types(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.User,
    emoji: disnake.Emoji,
):
    ...


# Adding descriptions is very simple, just use the docstring
@bot.slash_command()
async def description(inter: disnake.ApplicationCommandInteraction, user: disnake.User):
    """A random command"""


# Options can also be added into the docstring
@bot.slash_command()
async def full_description(
    inter: disnake.ApplicationCommandInteraction, user: disnake.User, channel: disnake.TextChannel
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
    self,
    inter: disnake.ApplicationCommandInteraction,
    string: str = None,
    user: disnake.User = commands.Param(lambda inter: inter.author),
):
    ...


# You may limit numbers into a certain range using gt, ge, lt, le (greater than, greater or equal, less than, less or equal)
# Alternatively you may use min_value instead of ge and max_value instead of le
@bot.slash_command()
async def ranges(
    self,
    inter: disnake.ApplicationCommandInteraction,
    ranking: int = commands.Param(gt=0, le=10),
    negative: float = commands.Param(lt=0),
    fraction: float = commands.Param(ge=0, lt=1),
):
    ...
