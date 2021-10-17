import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix="-")


# Defines a simple view of buttons for the embed.
class Menu(disnake.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        
        # Creates the embeds.
        self.embed1 = disnake.Embed(title="Menu example", description="This is the first embed.", colour=disnake.Colour.random())
        self.embed1.set_footer(text="Page 1 of 3")
        self.embed2 = disnake.Embed(title="Menu example", description="This is the second embed.", colour=disnake.Color.random())
        self.embed2.set_footer(text="Page 2 of 3")
        self.embed3 = disnake.Embed(title="Menu example", description="This is the third embed.", colour=disnake.Color.random())
        self.embed3.set_footer(text="Page 3 of 3")

        # Current embed number.
        self.embedCount = 1

    @disnake.ui.button(label="Previous page", emoji="◀️", style=disnake.ButtonStyle.red)
    async def nextPage(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.embedCount == 1: # If current embed is the first embed then, do not do anything.
            pass
        else: # If current embed is not the first embed then, edits the message with the preview embed.
            self.embedCount -= 1

            # Gets embed object
            embed = getattr(self, f"embed{self.embedCount}")

            await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Next page", emoji="▶️", style=disnake.ButtonStyle.green)
    async def lastPage(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.embedCount == 3: # If current embed is the last embed then, do not do anything.
            pass
        else: # If current embed is not the last embed then, edits the message with the next embed.
            self.embedCount += 1

            # Gets embed object
            embed = getattr(self, f"embed{self.embedCount}")

            await interaction.response.edit_message(embed=embed)

@bot.command()
async def menu(ctx):

    # Creates the first embed and sends it with the buttons.
    embed = disnake.Embed(title="Menu example", description="This is the first embed.", colour=disnake.Colour.random())
    embed.set_footer(text="Page 1 of 3")

    await ctx.send(embed=embed, view=Menu())

bot.run("token")
