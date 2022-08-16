import disnake
from disnake.ext import commands


async def test_autocomp(inter, string):
    return ["XD", ":D", ":)", ":|", ":("]


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command()
    async def hello(self, inter: disnake.CommandInteraction):
        await inter.response.send_message("Hello world!")

    @commands.slash_command()
    async def auto(self, inter: disnake.CommandInteraction, mood: str):
        """
        Has an autocomplete option.

        Parameters
        ----------
        mood: Dude
        """
        await inter.send(mood)

    @auto.autocomplete("mood")
    async def test_autocomp(self, inter: disnake.CommandInteraction, string: str):
        return ["XD", ":D", ":)", ":|", ":("]

    @commands.slash_command()
    async def alt_auto(
        self,
        inter: disnake.AppCmdInter,
        mood: str = commands.Param(autocomplete=test_autocomp),
    ):
        await inter.send(mood)

    @commands.slash_command()
    async def guild_only(self, inter: disnake.GuildCommandInteraction, option: str = None):
        await inter.send(f"guild: {inter.guild} | option: {option!r}")

    @commands.slash_command()
    async def ranges(
        self,
        inter: disnake.CommandInteraction,
        a: int = commands.Param(None, lt=0),
        b: commands.Range[1, ...] = None,
        c: commands.Range[0, 10] = None,
        d: commands.Range[0, 10.0] = None,
    ):
        """limit slash command options to a range of values

        Parameters
        ----------
        a: Negative
        b: Positive
        c: 0 - 10 integer
        d: 0 - 10 float
        """
        await inter.send(f"{inter.options}")

    @commands.slash_command()
    async def largenumber(self, inter: disnake.CommandInteraction, largenum: commands.LargeInt):
        await inter.send(f"Is int: {isinstance(largenum, int)}")


def setup(bot):
    bot.add_cog(SlashCommands(bot))
