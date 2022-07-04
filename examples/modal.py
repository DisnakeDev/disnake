import asyncio

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


class MyModal(disnake.ui.Modal):
    def __init__(self) -> None:

        select_options = [
            disnake.SelectOption(label="Yes"),
            disnake.SelectOption(label="No", default=True),
        ]
        components = [
            disnake.ui.TextInput(
                label="Name",
                placeholder="The name of the tag",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="The description of the tag",
                custom_id="description",
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
            disnake.ui.Select(
                custom_id="select",
                placeholder="Send as an embed.",
                min_values=1,
                max_values=1,
                options=select_options,
            ),
        ]

        super().__init__(title="Create Tag", custom_id="create_tag", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        embed = disnake.Embed(title="Tag Creation")

        # text_values is a dict of TextInput.custom_id to the inputted value.
        for key, value in inter.text_values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)

        # select_values is a dict of Select.custom_id to the selected value.
        for key, value in inter.select_values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)

        await inter.response.send_message(embed=embed)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)


@bot.slash_command()
async def create_tag(inter: disnake.CommandInteraction):
    # Sends a modal using a high level implementation.
    await inter.response.send_modal(modal=MyModal())


@bot.slash_command()
async def create_tag_low(inter: disnake.CommandInteraction):
    # Works same as the above code but using a low level interface.
    # It's recommended to use this if you don't want to increase cache usage.
    select_options = [
        disnake.SelectOption(label="Yes"),
        disnake.SelectOption(label="No", default=True),
    ]
    components = [
        disnake.ui.TextInput(
            label="Name",
            placeholder="The name of the tag",
            custom_id="name",
            style=disnake.TextInputStyle.short,
            max_length=50,
        ),
        disnake.ui.TextInput(
            label="Description",
            placeholder="The description of the tag",
            custom_id="description",
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
        disnake.ui.Select(
            custom_id="select",
            placeholder="Send as an embed.",
            min_values=1,
            max_values=1,
            options=select_options,
        ),
    ]

    await inter.response.send_modal(
        title="Create Tag", custom_id="create_tag_low", components=components
    )

    # Waits until the user submits the modal.
    try:
        modal_inter: disnake.ModalInteraction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_tag_low" and i.author.id == inter.author.id,
            timeout=300,
        )
    except asyncio.TimeoutError:
        # The user didn't submit the modal in the specified period of time.
        # This is done since Discord doesn't dispatch any event for when a modal is closed/dismissed.
        return

    embed = disnake.Embed(title="Tag Creation")

    # text_values is a dict of TextInput.custom_id to the entered value.
    for key, value in modal_inter.text_values.items():
        embed.add_field(name=key.capitalize(), value=value, inline=False)

    # select_values is a dict of Select.custom_id to the selected values.
    for key, value in modal_inter.select_values.items():
        embed.add_field(name=key.capitalize(), value=value, inline=False)

    await modal_inter.response.send_message(embed=embed)


bot.run("token")
