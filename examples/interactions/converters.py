# SPDX-License-Identifier: MIT

"""An example using converters with slash commands."""

import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# Classic commands.Converter classes have been replaced by more user-friendly converter functions,
# which can be set using `Param` and the `converter` argument.
@bot.slash_command()
async def clean_command(
    inter: disnake.CommandInteraction,
    text: str = commands.Param(converter=lambda inter, text: text.replace("@", "\\@")),
):
    ...


# Converters may also set the type of the option using annotations.
# Here the converter (and therefore, the slash command) is actually using a user option,
# while the command callback will receive a str.
def avatar_converter(inter: disnake.CommandInteraction, user: disnake.User) -> str:
    return user.display_avatar.url


@bot.slash_command()
async def command_with_avatar(
    inter: disnake.CommandInteraction,
    avatar: str = commands.Param(converter=avatar_converter),
):
    ...


# Converting to custom classes is also very easy using class methods.
class SomeCustomClass:
    def __init__(self, username: str, discriminator: str) -> None:
        self.username = username
        self.discriminator = discriminator

    @classmethod
    async def from_option(cls, inter: disnake.CommandInteraction, user: disnake.User):
        return cls(user.name, user.discriminator)


@bot.slash_command()
async def command_with_clsmethod(
    inter: disnake.CommandInteraction,
    some: SomeCustomClass = commands.Param(converter=SomeCustomClass.from_option),
):
    ...


# An even better approach is to register a method as the class converter,
# to be able to use only an annotation for the slash command option.
# `@converter_method` works like `@classmethod`,
# except it also stores the converter callback in an internal registry.
class OtherCustomClass:
    def __init__(self, username: str, discriminator: str) -> None:
        self.username = username
        self.discriminator = discriminator

    @commands.converter_method
    async def convert(cls, inter: disnake.CommandInteraction, user: disnake.User):
        return cls(user.name, user.discriminator)


@bot.slash_command()
async def command_with_convmethod(
    inter: disnake.CommandInteraction,
    other: OtherCustomClass,
):
    ...


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
