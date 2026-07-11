# SPDX-License-Identifier: MIT

"""An example showcasing v2/layout components."""

import os
from typing import Any

from disnake import ui
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def send_components(ctx: commands.Context):
    media_data: Any = ...  # placeholder for actual data

    await ctx.send(
        components=[
            ui.TextDisplay("@user's current activity:"),
            ui.Container(
                ui.Section(
                    f"Listening to {media_data.title}",
                    accessory=ui.Thumbnail(media_data.album_cover.url),
                ),
                ui.ActionRow(ui.Button(label="Open in Browser", url=media_data.link)),
            ),
        ]
    )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
