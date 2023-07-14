# SPDX-License-Identifier: MIT

"""An example showing how to use a dropdown menu using views."""

import os

import disnake
from disnake.ext import commands


# Defines a custom StringSelect containing colour options that the user can choose.
# The callback function of this class is called when the user changes their choice.
class Dropdown(disnake.ui.StringSelect):
    def __init__(self):
        # Define the options that will be presented inside the dropdown
        options = [
            disnake.SelectOption(
                label="Red", description="Your favourite colour is red", emoji="🟥"
            ),
            disnake.SelectOption(
                label="Green", description="Your favourite colour is green", emoji="🟩"
            ),
            disnake.SelectOption(
                label="Blue", description="Your favourite colour is blue", emoji="🟦"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen.
        # The min and max values indicate we can only pick one of the three options.
        # The options parameter defines the dropdown options, see above.
        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The `self` object refers to the
        # StringSelect object, and the `values` attribute gets a list of the user's
        # selected options. We only want the first one.
        await inter.response.send_message(f"Your favourite colour is {self.values[0]}")


class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__()

        # Add the dropdown to our view object.
        self.add_item(Dropdown())


bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def colour(ctx):
    """Sends a message with our dropdown containing colours"""
    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our view
    await ctx.send("Pick your favourite colour:", view=view)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
