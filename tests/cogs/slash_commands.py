import disnake
from disnake.ext import commands


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command()
    async def hello(self, inter: disnake.AppCmdInter):
        await inter.response.send_message("Hello world!")


def setup(bot):
    bot.add_cog(SlashCommands(bot))
    print(f"> Extension {__name__} is ready\n")
