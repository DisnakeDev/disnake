from disnake import ApplicationCommandInteraction
from disnake.ext import commands


bot = commands.Bot("!")

# Slash command subcommands differ from classic text subcommands & groups
#
# The gist of it is:
#   You may define any slash command which takes no arguments as the subcommand parent.
#   A parent has children which are subcommands or subcommand groups
#   Groups have subcommand children themselves
# For a full proper explanation see https://discord.com/developers/docs/interactions/application-commands#subcommands-and-subcommand-groups


# Define a new command with two children:
@bot.slash_command()
async def command(_inter: ApplicationCommandInteraction) -> None:
    print("This code is ran every time any subcommand is invoked")


@command.sub_command()
async def foo(inter: ApplicationCommandInteraction, option: str) -> None:
    await inter.response.send_message(f"Received {option}")


@command.sub_command()
async def bar(inter: ApplicationCommandInteraction, option: int) -> None:
    await inter.response.send_message(f"Gotten {option}")


# Define a new command with sub command groups (this time in a cog)
class MyCog(commands.Cog):
    @bot.slash_command()
    async def command(self, _inter: ApplicationCommandInteraction) -> None:
        print("This code is ran every time any subcommand is invoked")

    @command.sub_command_group()
    async def foo(self, _inter: ApplicationCommandInteraction) -> None:
        print("This code is ran every time any subcommand of foo is invoked")

    @foo.sub_command()
    async def a(self, inter: ApplicationCommandInteraction, option: int) -> None:
        await inter.response.send_message(f"You ran /command foo a {option}")

    @command.sub_command_group()
    async def bar(self, _inter: ApplicationCommandInteraction) -> None:
        print("This code is ran every time any subcommand of bar is invoked")

    @bar.sub_command()
    async def b(self, inter: ApplicationCommandInteraction, option: float) -> None:
        await inter.response.send_message(f"You ran /command bar b {option}")
