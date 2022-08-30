import os

from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)

# Slash command subcommands differ from classic text subcommands & groups
#
# The gist of it is:
#   You may define any slash command which takes no arguments as the subcommand parent.
#   A parent has children which are subcommands or subcommand groups
#   Groups have subcommand children themselves
# For a full proper explanation see https://discord.com/developers/docs/interactions/application-commands#subcommands-and-subcommand-groups


# Define a new command with two children:
@bot.slash_command()
async def command(inter):
    print("This code is ran every time any subcommand is invoked")


@command.sub_command()
async def foo(inter, option: str):
    await inter.response.send_message(f"Received {option}")


@command.sub_command()
async def bar(inter, option: int):
    await inter.response.send_message(f"Gotten {option}")


# Define a new command with sub command groups (this time in a cog)
class MyCog(commands.Cog):
    @commands.slash_command()
    async def command_in_cog(self, inter):
        print("This code is ran every time any subcommand is invoked")

    @command_in_cog.sub_command_group()
    async def foo(self, inter):
        print("This code is ran every time any subcommand of foo is invoked")

    @foo.sub_command()
    async def a(self, inter, option: int):
        await inter.response.send_message(f"You ran /command foo a {option}")

    @command_in_cog.sub_command_group()
    async def bar(self, inter):
        print("This code is ran every time any subcommand of bar is invoked")

    @bar.sub_command()
    async def b(self, inter, option: float):
        await inter.response.send_message(f"You ran /command bar b {option}")


bot.add_cog(MyCog())

bot.run(os.getenv("BOT_TOKEN"))
