# SPDX-License-Identifier: MIT

"""An example to showcase the disnake.ext.commands extension module.

There are a number of utility commands being showcased here.
"""

import os
import random

import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


@bot.command()
async def add(ctx: commands.Context, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(str(left + right))


@bot.command()
async def roll(ctx: commands.Context, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split("d"))
    except Exception:
        await ctx.send("Format has to be in NdN!")
        return

    result = ", ".join(str(random.randint(1, limit)) for _ in range(rolls))
    await ctx.send(result)


@bot.command(description="For when you wanna settle the score some other way")
async def choose(ctx: commands.Context, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx: commands.Context, times: int, content: str = "repeating..."):
    """Repeats a message multiple times."""
    for _ in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx: commands.Context, member: disnake.Member):
    """Says when a member joined."""
    if member.joined_at:
        # formats the join time/date like "5 years ago"
        date_str = disnake.utils.format_dt(member.joined_at, "R")
    else:
        date_str = "<unknown>"
    await ctx.send(f"{member} joined {date_str}")


@bot.group()
async def cool(ctx: commands.Context):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


@cool.command(name="bot")
async def bot_subcommand(ctx: commands.Context):
    """Is the bot cool?"""
    await ctx.send("Yes, the bot is cool.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
