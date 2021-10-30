import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix="-")

# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(disnake.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
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

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f"Your favourite colour is {self.values[0]}")


class DropdownView(disnake.ui.View):
    def __init__(self, timeout=None):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


# Define a simple View that gives us a confirmation menu
class Button(disnake.ui.View):
    def __init__(self, timeout=None):
        super().__init__()

    # Create some simple buttons.
    @disnake.ui.button(label="Hi", style=disnake.ButtonStyle.green)
    async def hi(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Hello!", ephemeral=True)

    @disnake.ui.button(label="Bye", style=disnake.ButtonStyle.red)
    async def bye(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Goodbye!", ephemeral=True)


@bot.command()
async def dropdown(ctx: commands.Context):

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our view
    await ctx.send("Pick your favourite colour:", view=view)


@bot.command()
async def button(ctx: commands.Context):

    # Create the view containing our buttons
    view = Button()

    # Sending a message containing our view
    await ctx.send("Hi!", view=view)


bot.run("token")
