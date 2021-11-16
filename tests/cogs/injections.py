from typing import Any, Tuple
import disnake
from disnake.ext import commands
from pprint import pformat


def injected(option: disnake.User, other: disnake.TextChannel):
    return (option.id, other.name)


async def converter(interaction, number: float) -> float:
    return number ** 0.5


class HopeToGod:
    def __init__(self, username: str, discriminator: str) -> None:
        self.username = username
        self.discriminator = discriminator

    @commands.converter_method
    async def convert(cls, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        return cls(user.name, user.discriminator)

    def __repr__(self) -> str:
        return f"HopeToGod({self.username!r}, {self.discriminator!r})"


class PerhapsThis:
    def __init__(self, a: int, b: float) -> None:
        self.a = a
        self.b = b

    def __repr__(self) -> str:
        return f"PerhapsThis({self.a!r}, {self.b!r})"


@commands.register_injection
async def perhaps_this_is_it(
    a: disnake.TextChannel = commands.Param(lambda i: i.channel), b: float = 0
) -> PerhapsThis:
    return PerhapsThis(a.id, b / 2)


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
        converted: float = commands.Param(None, converter=lambda i, x: x ** 0.5),
        other: Tuple[int, str] = commands.inject(injected),
        some: int = commands.inject(injected_method),
    ):
        await inter.response.send_message(f"```py\n{pformat(locals())}\n```")

    @commands.slash_command()
    async def discerned_injections(
        self,
        inter: disnake.ApplicationCommandInteraction,
        perhaps: PerhapsThis,
        god: HopeToGod = None,
    ):
        await inter.response.send_message(f"```py\n{pformat(locals())}\n```")


def setup(bot):
    bot.add_cog(InjectionSlashCommands(bot))
    print(f"> Extension {__name__} is ready\n")
