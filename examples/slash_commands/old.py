"""
An example of old-style options.
Not the most convenient syntax.
"""
import disnake
from disnake.ext import commands

bot = commands.Bot("!")


@bot.slash_command(
    name="slash_command",
    description="A Simple Slash Command",
    options=[
        disnake.Option("string", description="A string to send", required=True),
        disnake.Option(
            "channel", description="The destination channel", type=disnake.OptionType.channel
        ),
        disnake.Option(
            "number", description="The number of repetitions", type=disnake.OptionType.integer
        ),
    ],
)
async def command(inter, string, channel=None, number=1):
    channel = channel or inter.channel
    await inter.response.send_message(
        f"Sending {string} {number}x to {channel.mention}", ephemeral=True
    )
    await channel.send(string * number)
