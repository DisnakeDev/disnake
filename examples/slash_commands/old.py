"""
An example of old-style options.
Not the most convenient syntax.
"""
from typing import Optional, Union

import disnake
from disnake import TextChannel, Thread, ApplicationCommandInteraction
from disnake.ext import commands


bot = commands.Bot("!")


@bot.slash_command(
    name="slash_command",
    description="A Simple Slash Command",
    options=[
        disnake.Option("string", description="A string to send", required=True),
        disnake.Option("channel", description="The destination channel", type=disnake.OptionType.channel),
        disnake.Option("number", description="The number of repetitions", type=disnake.OptionType.integer),
    ]
)
async def command(
    inter: ApplicationCommandInteraction,
    string: str,
    channel: Optional[Union[TextChannel, Thread]] = None,
    number: int = 1
) -> None:
    channel = channel if channel is not None else inter.channel
    await inter.response.send_message(f"Sending {string} {number}x to {channel.mention}", ephemeral=True)
    await channel.send(string * number)
