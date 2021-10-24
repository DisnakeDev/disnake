import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))

# Define a simple View with buttons
class MyView(disnake.ui.View):

    def __init__(self):

    # Sets the timeout
        super().__init__(timeout=30.0)

    # The timeout, after which the first button will be disabled and the second button will be removed
    async def on_timeout(self):
        self.children[0].disabled = True    # First button is disabled
        self.remove_item(self.children[1])  # Second button is removed
        await self.message.edit(view=self)  # View is edited

    # Button that will disable the view
    @disnake.ui.button(label="Click to disable the view", style=disnake.ButtonStyle.red)
    async def disable(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):

    # Disabling the view
        for child in self.children:
            child.disabled = True               # Disabling all the components in the view
            await self.message.edit(view=self)  # Editing the view

        # Prevents `on_timeout` from being triggered after the buttons are disabled
        self.stop()

    @disnake.ui.button(label="Click to remove the view", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):

        # view = None removes the view
        await self.message.edit(view=None)

@bot.command()
async def view(ctx):

    # Defines our view so that we can use `self.message` in `on_timeout` to edit it
    view = MyView()

    # Sends a message with the view
    view.message = await ctx.send("These buttons will be disabled or removed", view=view)

bot.run("token")