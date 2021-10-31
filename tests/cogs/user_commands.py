import disnake
from disnake.ext import commands


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.user_command(name="Avatar")
    async def avatar(self, inter: disnake.UserCommandInteraction):
        await inter.response.send_message(
            inter.target.display_avatar.url,
            ephemeral=True
        )


def setup(bot):
    bot.add_cog(UserCommands(bot))
    print(f"> Extension {__name__} is ready\n")
