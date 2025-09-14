# SPDX-License-Identifier: MIT

"""An example making use of ephemeral responses,
to show a message only to the initiating user.
"""

import os

import disnake
from disnake.ext import commands


# Define a simple View that gives us a counter button
class EphemeralCounter(disnake.ui.View):
    # Define the actual button
    # note: The name of the function does not matter to the library
    @disnake.ui.button(label="0", style=disnake.ButtonStyle.red)
    async def count(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # When pressed, this increments the number displayed until it hits 5.
        # When it hits 5, the counter button is disabled and it turns green.
        number = int(button.label) if button.label else 0
        number += 1
        if number >= 5:
            button.style = disnake.ButtonStyle.green
            button.disabled = True
        button.label = str(number)

        # Make sure to update the message with our updated button
        await inter.response.edit_message(view=self)

        if button.disabled:
            # Stop listening, since the user isn't able to press the button anymore
            self.stop()


# Define a View that will allow us to create our own personal counter button
class CreateCounter(disnake.ui.View):
    # When this button is pressed, it will respond with a Counter view that will
    # give the user their own personal button they can press 5 times.
    @disnake.ui.button(label="Click", style=disnake.ButtonStyle.blurple)
    async def receive(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # ephemeral=True makes the message hidden from everyone except the button presser
        await inter.response.send_message("Enjoy!", view=EphemeralCounter(), ephemeral=True)


bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def counter(ctx: commands.Context):
    await ctx.send("Press!", view=CreateCounter())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
