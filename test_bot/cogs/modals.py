import disnake
from disnake.enums import InputTextStyle
from disnake.ext import commands


class MyModal(disnake.ui.Modal):
    def __init__(self) -> None:
        components = [
            disnake.ui.InputText(
                label="Name",
                placeholder="The name of the tag",
                custom_id="name",
                style=InputTextStyle.short,
                max_length=50,
            ),
            disnake.ui.InputText(
                label="Description",
                placeholder="The description of the tag",
                custom_id="description",
                style=InputTextStyle.paragraph,
            ),
        ]
        super().__init__(title="Create Tag", custom_id="create_tag", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        embed = disnake.Embed(title="Tag Creation")
        for key, value in inter.values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)
        await inter.response.send_message(embed=embed)


class Modals(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def create_tag(self, inter: disnake.AppCmdInter) -> None:
        """Sends a Modal to create a tag."""
        await inter.response.send_modal(modal=MyModal())

    @commands.slash_command()
    async def create_tag_low(self, inter: disnake.AppCmdInter) -> None:
        """Sends a Modal to create a tag but with a low-level implementation."""
        await inter.response.send_modal(
            title="Create Tag",
            custom_id="create_tag2",
            components=[
                disnake.ui.InputText(
                    label="Name",
                    placeholder="The name of the tag",
                    custom_id="name",
                    style=InputTextStyle.short,
                    max_length=50,
                ),
                disnake.ui.InputText(
                    label="Description",
                    placeholder="The description of the tag",
                    custom_id="description",
                    style=InputTextStyle.paragraph,
                ),
            ],
        )

        modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_tag2" and i.author.id == inter.author.id,
        )

        embed = disnake.Embed(title="Tag Creation")
        for key, value in modal_inter.values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)
        await modal_inter.response.send_message(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Modals(bot))
