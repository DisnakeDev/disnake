import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))


class MyView(disnake.ui.View):

    def __init__(self):
        super().__init__(timeout=30.0)

    async def on_timeout(self):
    	# Once the view times out we disable the first button and remove the second button
        self.children[0].disabled = True
        self.remove_item(self.children[1])
        # make sure to update the message with the new buttons
        await self.message.edit(view=self)

    @disnake.ui.button(label="Click to disable the view", style=disnake.ButtonStyle.red)
    async def disable(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):

        # We disable every single component in this view
        for child in self.children:
            child.disabled = True
        # make sure to update the message with the new buttons
        await self.message.edit(view=self)

        # Prevents on_timeout from being triggered after the buttons are disabled
        self.stop()

    @disnake.ui.button(label="Click to remove the view", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        # view = None removes the view
        await self.message.edit(view=None)

@bot.command()
async def view(ctx):

    # Defines our view so that we can use the message in on_timeout to edit it
    view = MyView()

    # Sends a message with the view
    view.message = await ctx.send("These buttons will be disabled or removed", view=view)

bot.run("token")
