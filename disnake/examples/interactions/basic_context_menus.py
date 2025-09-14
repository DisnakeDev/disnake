# SPDX-License-Identifier: MIT

"""A simple example showing context menu commands.
User commands show up in the context menu (right-click/tap) of users,
while message commands show up in the context menu of messages.
"""

import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# The decorated function only has one required parameter, the interaction.
# Optionally, the function may also take a second parameter,
# which is the target of the interaction, i.e. the user/member or message
# (a shortcut to `inter.target`).


@bot.user_command(name="Avatar")  # name is optional
async def avatar(inter: disnake.UserCommandInteraction, user: disnake.User):
    embed = disnake.Embed(title=f"{user}'s avatar")
    embed.set_image(url=user.display_avatar.url)
    await inter.response.send_message(embed=embed)


@bot.message_command(name="Reverse")  # name is optional
async def reverse(inter: disnake.MessageCommandInteraction, message: disnake.Message):
    # Let's reverse it and send it back
    await inter.response.send_message(message.content[::-1])


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
