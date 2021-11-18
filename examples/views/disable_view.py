import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))


class MyView(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Click to disable the view", style=disnake.ButtonStyle.red)
    async def disable(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):

        # We disable every single component in this view
        for child in self.children:
            child.disabled = True
        # Make sure to update the message with the disabled buttons
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(label="Click to remove the view", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        # view = None removes the view
        await interaction.response.edit_message(view=None)


@bot.command()
async def view(ctx):

    # Defines our view
    view = MyView()

    # Sends a message with the view
    view.message = await ctx.send("These buttons will be disabled or removed", view=view)


bot.run("token")
