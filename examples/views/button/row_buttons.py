# SPDX-License-Identifier: MIT

"""An example with multiple rows of buttons in a view."""

# The end result would look like this: https://i.imgur.com/ZYdX1Jw.png

import os

import disnake
from disnake.enums import ButtonStyle
from disnake.ext import commands


# Defines a simple view of row buttons.
class RowButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Hi", style=ButtonStyle.red)
    async def first_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is the first button.")

    @disnake.ui.button(label="this is", style=ButtonStyle.red)
    async def second_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is the second button.")

    @disnake.ui.button(label="a row of", style=ButtonStyle.blurple, row=1)
    async def third_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is the third button.")

    @disnake.ui.button(label="buttons.", style=ButtonStyle.blurple, row=1)
    async def fourth_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is the fourth button.")

    @disnake.ui.button(emoji="🥳", style=ButtonStyle.green, row=2)
    async def fifth_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is the fifth button.")


bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def buttons(ctx):
    # Sends a message with a row of buttons.
    await ctx.send("Here are some buttons!", view=RowButtons())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
