import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix="-")

# Defines a simple view of buttons for the embed.
class Menu(disnake.ui.View):

    def __init__(self, embeds: list[disnake.Embed]):
        super().__init__(timeout=None)
        
        # Sets the embed list variable.
        self.embeds = embeds

        # Current embed number.
        self.embedCount = 0

    @disnake.ui.button(label="Previous page", emoji="◀️", style=disnake.ButtonStyle.red)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.embedCount == 0: # If current embed is the first embed then, do not do anything.
            pass
        else: # If current embed is not the first embed then, sends the preview embed.
            self.embedCount -= 1

            # Gets the embed object.
            embed = self.embeds[self.embedCount]

            # Sets the footer of the embed with current page and then sends it.
            embed.set_footer(text=f"Page {self.embedCount + 1} of {len(self.embeds)}")
            await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Next page", emoji="▶️", style=disnake.ButtonStyle.green)
    async def last_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.embedCount == (len(self.embeds) - 1): # If current embed is the last embed then, do not do anything.
            pass
        else: # If current embed is not the last embed then, sends the next embed.
            self.embedCount += 1

            # Gets the embed object.
            embed = self.embeds[self.embedCount]

            # Sets the footer of the embed with current page and then sends it.
            embed.set_footer(text=f"Page {self.embedCount + 1} of {len(self.embeds)}")
            await interaction.response.edit_message(embed=embed)

@bot.command()
async def menu(ctx):

    # Creates the embeds as a list.
    embeds = [
        disnake.Embed(title="Menu example", description="This is the first embed.", colour=disnake.Colour.random()),
        disnake.Embed(title="Menu example", description="This is the second embed.", colour=disnake.Color.random()),
        disnake.Embed(title="Menu example", description="This is the third embed.", colour=disnake.Color.random())
    ]

    # Sets the footer of the first embed.
    embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")

    # Sends first embed with the buttons, it also passes the embeds list into the View class.
    await ctx.send(embed=embeds[0], view=Menu(embeds))

bot.run("token")
