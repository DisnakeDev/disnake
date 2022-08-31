import disnake
from disnake.ext import commands


class MessageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.message_command(name="Reverse")
    async def reverse(self, inter: disnake.MessageCommandInteraction):
        await inter.response.send_message(inter.target.content[::-1])


def setup(bot):
    bot.add_cog(MessageCommands(bot))
