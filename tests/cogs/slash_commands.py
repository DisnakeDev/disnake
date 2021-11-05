import disnake
from disnake.ext import commands


async def test_autocomp(inter, string):
    return ["XD", ":D", ":)", ":|", ":("]


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command()
    async def hello(self, inter: disnake.AppCmdInter):
        await inter.response.send_message("Hello world!")

    @commands.slash_command()
    async def auto(self, inter: disnake.AppCmdInter, mood: str):
        """
        Has an autocomplete option.

        Parameters
        ----------
        mood: Dude
        """
        await inter.send(mood)

    @auto.autocomplete("mood")
    async def test_autocomp(self, inter: disnake.AppCmdInter, string: str):
        return ["XD", ":D", ":)", ":|", ":("]

    @commands.slash_command()
    @commands.guild_permissions(768247229840359465, roles={815866581233041428: False})
    async def alt_auto(
        self,
        inter: disnake.AppCmdInter,
        mood: str = commands.Param(autocomp=test_autocomp)
    ):
        await inter.send(mood)

    @commands.slash_command()
    async def check(self, inter):
        pass

    @check.sub_command_group()
    async def out(self, inter):
        pass

    @out.sub_command(description="Nested command")
    async def events(self, inter: disnake.GuildCommandInteraction):
        await inter.send(f"{inter.guild.scheduled_events}")


def setup(bot):
    bot.add_cog(SlashCommands(bot))
    print(f"> Extension {__name__} is ready\n")
