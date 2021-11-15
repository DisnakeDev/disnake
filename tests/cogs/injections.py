from typing import Any, Tuple
import disnake
from disnake.ext import commands
from pprint import pformat


async def injected(option: disnake.User, other: disnake.TextChannel):
    return (option.id, other.name)


class InjectionSlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.exponent = 2
    
    async def injected_method(self, number: int = 0):
        return number ** self.exponent

    @commands.slash_command()
    async def injection_command(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        some: Tuple[int, str] = commands.inject(injected),
        other: int = commands.inject(injected_method),
    ):
        await inter.response.send_message(f"```py\n{pformat(locals())}\n```")


def setup(bot):
    bot.add_cog(InjectionSlashCommands(bot))
    print(f"> Extension {__name__} is ready\n")
