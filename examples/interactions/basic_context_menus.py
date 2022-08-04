import os

import disnake
from disnake.ext import commands

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
)


@bot.event
async def on_ready():
    print("Bot is ready")


# Here we create a user command. The function below the decorator
# should only have one requierd argument, which is
# an instance of ApplicationCommandInteraction.
@bot.user_command(name="Avatar")  # optional
async def avatar(inter: disnake.ApplicationCommandInteraction, user: disnake.User):
    emb = disnake.Embed(title=f"{user}'s avatar")
    emb.set_image(url=user.display_avatar.url)
    await inter.response.send_message(embed=emb)


# Here we create a message command. The function below the decorator
# should only have one required argument, which is
# an instance of ApplicationCommandInteraction.
@bot.message_command(name="Reverse")  # optional
async def reverse(inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
    # Let's reverse it and send back
    await inter.response.send_message(message.content[::-1])


bot.run(os.getenv("BOT_TOKEN"))
