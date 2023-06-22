# SPDX-License-Identifier: MIT

"""Shhhh! It's a secret."""

import os
from typing import Union

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned, description="Nothing to see here!")


# the `hidden` keyword argument hides this command group from the help command.
@bot.group(hidden=True)
async def secret(ctx: commands.Context):
    """What is this "secret" you speak of?"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Shh!", delete_after=5)


def create_overwrites(ctx: commands.GuildContext, *objects: Union[disnake.Role, disnake.Member]):
    """A helper function that creates the overwrites for the voice/text channels.

    A `disnake.PermissionOverwrite` allows you to determine the permissions
    of an object, whether it be a `disnake.Role` or a `disnake.Member`.

    In this case, the `view_channel` permission is being used to hide the channel
    from being viewed by whoever does not meet the criteria, thus creating a
    secret channel.
    """
    # a dict comprehension is being utilised here to set the same permission overwrites
    # for each `disnake.Role` or `disnake.Member`.
    overwrites = {obj: disnake.PermissionOverwrite(view_channel=True) for obj in objects}

    # prevents the default role (@everyone) from viewing the channel
    # if it isn't already allowed to view the channel.
    overwrites.setdefault(ctx.guild.default_role, disnake.PermissionOverwrite(view_channel=False))

    # makes sure the client is always allowed to view the channel.
    overwrites[ctx.guild.me] = disnake.PermissionOverwrite(view_channel=True)

    return overwrites


# since these commands rely on guild related features,
# it is best to lock it to be guild-only.
@secret.command()
@commands.guild_only()
async def text(
    ctx: commands.GuildContext, name: str, *objects: Union[disnake.Role, disnake.Member]
):
    """Creates a text channel with the specified name
    that is only visible to the specified roles and/or members.
    """
    overwrites = create_overwrites(ctx, *objects)

    await ctx.guild.create_text_channel(
        name,
        overwrites=overwrites,
        topic="Top secret text channel. Any leakage of this channel may result in serious trouble.",
        reason="Very secret business.",
    )


@secret.command()
@commands.guild_only()
async def voice(
    ctx: commands.GuildContext, name: str, *objects: Union[disnake.Role, disnake.Member]
):
    """Does the same thing as the `text` subcommand but instead creates a voice channel."""
    overwrites = create_overwrites(ctx, *objects)

    await ctx.guild.create_voice_channel(
        name, overwrites=overwrites, reason="Very secret business."
    )


@secret.command()
@commands.guild_only()
async def emoji(ctx: commands.GuildContext, emoji: disnake.PartialEmoji, *roles: disnake.Role):
    """Clones a specified emoji that only specified roles are allowed to use."""
    # fetch the emoji asset and read it as bytes.
    emoji_bytes = await emoji.read()

    # the key parameter here is `roles`, which controls
    # what roles are able to use the emoji.
    await ctx.guild.create_custom_emoji(
        name=emoji.name, image=emoji_bytes, roles=roles, reason="Very secret business."
    )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
