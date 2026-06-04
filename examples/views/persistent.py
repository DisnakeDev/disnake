# SPDX-License-Identifier: MIT

"""An advanced example on how to persist views between bot restarts."""

import os

import disnake
from disnake.ext import commands

# In order a view to persist between restarts it needs to meet the following conditions:
# 1) The `timeout` of the view has to be set to `None`
# 2) Every item in the view has to have a `custom_id` set

# It is recommended that the custom_id be sufficiently unique to
# prevent conflicts with other buttons the bot may send.
# For this example, the custom_ids are prefixed with `persistent_example:` to avoid possible conflicts.
# Note that there is no fixed structure for custom_ids, however they can only be up to 100 characters long.


class PersistentView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Green", style=disnake.ButtonStyle.green, custom_id="persistent_example:green"
    )
    async def green(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is green.", ephemeral=True)

    @disnake.ui.button(
        label="Red", style=disnake.ButtonStyle.red, custom_id="persistent_example:red"
    )
    async def red(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is red.", ephemeral=True)

    @disnake.ui.button(
        label="Grey", style=disnake.ButtonStyle.grey, custom_id="persistent_example:grey"
    )
    async def grey(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("This is grey.", ephemeral=True)


class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned)
        self.persistent_views_added = False

    async def on_ready(self):
        # `on_ready` can be fired multiple times during a bot's lifetime,
        # we only want to register the persistent view once.
        if not self.persistent_views_added:
            # Register the persistent view for listening here.
            # Note that this does not send the view to any message.
            # In order to do this you need to first send a message with the View, which is shown below.
            # If you have the message_id you can also pass it as a keyword argument, but for this example
            # we don't have one.
            self.add_view(PersistentView())
            self.persistent_views_added = True

        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")


bot = PersistentViewBot()


# In order for a persistent view to be listened to, it needs to be sent with an actual message.
# Call this command once just to create the view.
# Since the view is persistent, the buttons will continue to work even after the bot is restarted.
@bot.command()
async def prepare(ctx: commands.Context):
    """Starts a persistent view."""
    # In a more complicated program you might fetch the message_id from a database for use later,
    # however this is outside of the scope of this example.
    await ctx.send("What's your favourite colour?", view=PersistentView())


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
