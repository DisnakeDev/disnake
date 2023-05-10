# SPDX-License-Identifier: MIT

"""An example using the `on_message_edit` and `on_message_delete` events."""

import asyncio
import os

import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


# When a message gets edited, the `on_message_edit` event will be called
# with the old and new message objects.
# NOTE: This only works as long as the message is in the bot's message cache.
@bot.event
async def on_message_edit(before: disnake.Message, after: disnake.Message):
    msg = f"**{before.author}** edited their message:\n{before.content} -> {after.content}"
    await before.channel.send(msg)


# Similarly, when a message gets deleted, the `on_message_delete` event will be called
# with the now deleted message.
@bot.event
async def on_message_delete(message: disnake.Message):
    msg = f"The message by **{message.author}** was deleted:\n{message.content}"
    await message.channel.send(msg)


@bot.command()
async def edit(ctx: commands.Context):
    msg = await ctx.channel.send("10")
    await asyncio.sleep(3.0)
    await msg.edit(content="40")


@bot.command()
async def delete(ctx: commands.Context):
    # send and immediately delete a message
    msg = await ctx.channel.send("I will delete myself now...")
    await msg.delete()

    # `delete_after` can also be used
    await ctx.channel.send("Goodbye in 3 seconds...", delete_after=3.0)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
