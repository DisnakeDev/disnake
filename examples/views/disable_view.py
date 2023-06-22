# SPDX-License-Identifier: MIT

"""An example showing how to edit view components, use timeouts, and disable views."""

import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


class MyView(disnake.ui.View):
    message: disnake.Message

    def __init__(self):
        # Set a timeout of 30 seconds, after which `on_timeout` will be called
        super().__init__(timeout=30.0)

    async def on_timeout(self):
        # Once the view times out, we disable the first button and remove the second button
        self.disable_button.disabled = True
        self.remove_item(self.remove_button)

        # make sure to update the message with the new buttons
        await self.message.edit(view=self)

    @disnake.ui.button(label="Disable the view", style=disnake.ButtonStyle.grey)
    async def disable_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # We disable every single component in this view
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        # make sure to update the message with the new buttons
        await inter.response.edit_message(view=self)

        # Prevents on_timeout from being triggered after the buttons are disabled
        self.stop()

    @disnake.ui.button(label="Remove the view", style=disnake.ButtonStyle.red)
    async def remove_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # view=None removes the view
        await inter.response.edit_message(view=None)

        # Prevents on_timeout from being triggered after the view is removed
        self.stop()


@bot.command()
async def view(ctx: commands.Context):
    # Create our view
    view = MyView()

    # Send a message with the view
    message = await ctx.send("These buttons will be disabled or removed!", view=view)

    # Assign the message to the view, so that we can use it in on_timeout to edit it
    view.message = message


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
