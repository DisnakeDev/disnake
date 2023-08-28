# SPDX-License-Identifier: MIT

import disnake
from disnake.ext import commands


class UserCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.user_command(name="Avatar")
    async def avatar(self, inter: disnake.UserCommandInteraction, user: disnake.User) -> None:
        await inter.response.send_message(user.display_avatar.url, ephemeral=True)


def setup(bot) -> None:
    bot.add_cog(UserCommands(bot))
