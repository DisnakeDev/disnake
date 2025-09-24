# SPDX-License-Identifier: MIT

"""An example showcasing v2/layout components."""

import os
from pathlib import Path
from typing import Any, List, NamedTuple

import disnake
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


class Website(NamedTuple):
    name: str
    domain: str
    web_url: str
    image_url: str


async def fetch_websites() -> List[Website]:
    return [
        Website(
            name="Disnake Dev",
            domain="disnake.dev",
            web_url="https://disnake.dev/",
            image_url="https://disnake.dev/assets/disnake-logo.png",
        ),
        Website(
            name="Disnake Docs",
            domain="docs.disnake.dev",
            web_url="https://docs.disnake.dev/en/stable/index.html",
            image_url="https://disnake.dev/assets/disnake-logo.png",
        ),
        Website(
            name="Disnake Guide",
            domain="guide.disnake.dev",
            web_url="https://guide.disnake.dev/",
            image_url="https://disnake.dev/assets/disnake-logo.png",
        ),
    ]


@bot.slash_command()
async def cool_message(inter: disnake.ApplicationCommandInteraction) -> None:
    # mock a fetch of the websites
    websites: list[Website] = await fetch_websites()
    web_components = [
        ui.Section(
            ui.TextDisplay("### " + website.name),
            ui.TextDisplay(f"[`{website.domain}`]({website.web_url})"),
            accessory=ui.Thumbnail(
                media=website.image_url, description=f"{website.name}'s thumbnail"
            ),
        )
        for website in websites
    ]

    await inter.response.send_message(
        components=[
            ui.Container(
                ui.TextDisplay(f"# Websites found ({len(websites)})"),
                *web_components,
                accent_colour=disnake.Color.blue(),
            )
        ]
    )


@bot.slash_command()
async def buttons_with_actions(inter: disnake.ApplicationCommandInteraction) -> None:
    await inter.response.send_message(components=[ui.Container(ui.TextDisplay)])


@bot.slash_command()
async def media_gallery(inter: disnake.ApplicationCommandInteraction) -> None:
    file_names = list(Path("assets/").glob("*.png"))
    media = [
        disnake.MediaGalleryItem(media=f"attachment://{file_path.name}", description=file_path.name)
        for file_path in file_names
    ]
    files = [disnake.File(file_path, filename=file_path.name) for file_path in file_names]
    await inter.response.send_message(
        components=[
            ui.Container(
                ui.TextDisplay("## Image Gallery"),
                ui.TextDisplay("A list of images present locally in the `assets` folder."),
                ui.MediaGallery(*media),
            )
        ],
        files=files,
    )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
