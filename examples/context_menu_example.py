import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=">", test_guilds=[12345])

@bot.user_command()
async def avatar(inter, user):
    embed = disnake.Embed(title=str(user))
    embed.set_image(url=user.display_avatar.url)
    await inter.response.send_message(embed=embed)

bot.run("BOT_TOKEN")