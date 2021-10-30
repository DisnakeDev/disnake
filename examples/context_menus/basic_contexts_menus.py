import disnake
from disnake.ext import commands


bot = commands.Bot(
    command_prefix="$",
    # Insert IDs of your test guilds below, if
    # you want the context menus to instantly appear.
    # Without test_guilds specified, your commands will
    # register globally in ~1 hour.
    test_guilds=[12345],
)


@bot.event
async def on_ready():
    print("Bot is ready")


# Here we create a user command. The function below the decorator
# should only have one requierd argument, which is
# an instance of ApplicationCommandInteraction.
@bot.user_command(name="Avatar")  # optional
async def avatar(inter: disnake.UserCommandInteraction):
    # inter.target is the user you clicked on
    emb = disnake.Embed(title=f"{inter.target}'s avatar")
    emb.set_image(url=inter.target.display_avatar.url)
    await inter.response.send_message(embed=emb)


# Here we create a message command. The function below the decorator
# should only have one requierd argument, which is
# an instance of ApplicationCommandInteraction.
@bot.message_command(name="Reverse")  # optional
async def reverse(inter: disnake.MessageCommandInteraction):
    # inter.target is the message you clicked on
    # Let's reverse it and send back
    await inter.response.send_message(inter.target.content[::-1])


bot.run("TOKEN")
