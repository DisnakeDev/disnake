# SPDX-License-Identifier: MIT

"""A confirm/cancel button example using views."""

import os
from typing import Optional

import disnake
from disnake.ext import commands


# Define a simple View that gives us a confirmation menu
class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.value: Optional[bool] = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Confirming...", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`.
    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Cancelling...", ephemeral=True)
        self.value = False
        self.stop()


bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def ask(ctx: commands.Context):
    """Asks the user a question to confirm something."""
    # We create the view and assign it to a variable so we can wait for it later.
    view = Confirm()
    message = await ctx.send("Do you want to continue?", view=view)

    # Wait for the View to stop listening for input...
    await view.wait()

    # Check the value to determine which button was pressed, if any.
    if view.value is None:
        print("Timed out.")
    elif view.value:
        print("Confirmed.")
    else:
        print("Cancelled.")

    # Once we're done, disable the buttons.
    for child in view.children:
        if isinstance(child, disnake.ui.Button):
            child.disabled = True
    await message.edit(view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
