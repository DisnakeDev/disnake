# SPDX-License-Identifier: MIT

"""An example demonstrating two methods of sending modals and handling modal responses."""

import asyncio
import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# One way of sending modals is using a "high-level" implementation similar to views,
# in which a class representing the modal is defined, complete with a callback and error handler.

# Sent modals are stored internally for a certain amount of time, taking up some amount of memory.
# Since there is no way of knowing whether the user closed the modal without submitting it,
# they time out after 10 minutes by default, at which point they will be removed
# from the internal storage, and any submission by the user will fail.
# This timeout can be adjusted through the use of the `timeout` parameter of the modal class.


class MyModal(disnake.ui.Modal):
    def __init__(self) -> None:
        components = [
            disnake.ui.TextInput(
                label="Name",
                placeholder="The name of the tag",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Content",
                placeholder="The content of the tag",
                custom_id="content",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
            ),
        ]
        super().__init__(title="Create Tag", custom_id="create_tag", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        tag_name = inter.text_values["name"]
        tag_content = inter.text_values["content"]

        embed = disnake.Embed(title=f"Tag created: `{tag_name}`")
        embed.add_field(name="Content", value=tag_content)
        await inter.response.send_message(embed=embed)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)


@bot.slash_command()
async def create_tag(inter: disnake.CommandInteraction):
    await inter.response.send_modal(modal=MyModal())


# Similar to the views and low-level components duality,
# you can also send modals using a more "low-level" implementation
# without creating a custom modal class, and instead using event listeners.

# Naturally, these are persistent, unlike modal classes which don't persist
# over bot restarts and generally time out after a certain period of time.
# Similarly, the listener approach doesn't impact memory usage for every sent modal
# as much as the method shown above.


@bot.slash_command()
async def create_tag_low(inter: disnake.CommandInteraction):
    # Works same as the above code but using a low level interface.
    # It's recommended to use this if you don't want to increase cache usage.
    await inter.response.send_modal(
        title="Create Tag",
        custom_id="create_tag_low",
        components=[
            disnake.ui.TextInput(
                label="Name",
                placeholder="The name of the tag",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Content",
                placeholder="The content of the tag",
                custom_id="content",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
            ),
        ],
    )

    # Waits until the user submits the modal.
    try:
        modal_inter: disnake.ModalInteraction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_tag_low" and i.author.id == inter.author.id,
            timeout=600,
        )
    except asyncio.TimeoutError:
        # The user didn't submit the modal in the specified period of time.
        # This is done since Discord doesn't dispatch any event for when a modal is closed/dismissed.
        return

    tag_name = modal_inter.text_values["name"]
    tag_content = modal_inter.text_values["content"]

    embed = disnake.Embed(title=f"Tag created: `{tag_name}`")
    embed.add_field(name="Content", value=tag_content)
    await modal_inter.response.send_message(embed=embed)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
