import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=">")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run("BOT_TOKEN")