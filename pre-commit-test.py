import time

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix="-")


@bot.slash_command()
async def m(inter: disnake.ApplicationCommandInteraction, text: str = "m"):
    print(text)


bot.run("token")
