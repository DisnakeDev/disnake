# SPDX-License-Identifier: MIT

"""An example showcasing v2/layout components."""

from __future__ import annotations

import datetime
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


# Now let's make a simple command with static components
# just to show some info
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


# Let's make an example about media gallery and sending local files
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


# mimic a DB call from a database
async def fetch_user_todo_list(user_id: int) -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "title": "Study for the exam",
            "description": ":'(",
            "status": "Not Done",
            "deadline": datetime.datetime(year=2025, month=12, day=2, tzinfo=datetime.timezone.utc),
        },
        {
            "id": 2,
            "title": "Finish other PRs",
            "description": "",
            "status": "Not Done",
            "deadline": datetime.datetime(year=2025, month=12, day=2, tzinfo=datetime.timezone.utc),
        },
        {
            "id": 3,
            "title": "Make homemade pizza",
            "description": "",
            "status": "Not Done",
            "deadline": datetime.datetime(year=2025, month=12, day=2, tzinfo=datetime.timezone.utc),
        },
        {
            "id": 4,
            "title": "Read the new book",
            "description": "",
            "status": "Not Done",
            "deadline": datetime.datetime(year=2025, month=12, day=2, tzinfo=datetime.timezone.utc),
        },
        {
            "id": 5,
            "title": "Look for Christmas gift",
            "description": "",
            "status": "Not Done",
            "deadline": datetime.datetime(year=2025, month=12, day=2, tzinfo=datetime.timezone.utc),
        },
        {
            "id": 6,
            "title": "Study for final exams",
            "description": "Pain",
            "status": "Not Done",
            "deadline": datetime.datetime(year=2026, month=1, day=2, tzinfo=datetime.timezone.utc),
        },
    ]


# Now let's make a more complex example that uses buttons
@bot.slash_command()
async def todo_list(inter: disnake.ApplicationCommandInteraction) -> None:
    TODO_PER_PAGE = 5
    data = await fetch_user_todo_list(inter.author.id)

    last_page_size = len(data) % TODO_PER_PAGE
    total_pages = len(data) // TODO_PER_PAGE
    if last_page_size != 0:
        total_pages += 1

    paginator_buttons_disabled = len(data) == TODO_PER_PAGE
    await send_page(inter, 0, total_pages, last_page_size, paginator_buttons_disabled)


async def interaction_check(
    inter: disnake.MessageInteraction, invoker_id: int, user_id: int
) -> None:
    if int(invoker_id) != user_id:
        await inter.send("You can't interact with this component :(", ephemeral=True)


async def send_page(
    inter: disnake.ApplicationCommandInteraction | disnake.MessageInteraction,
    current_page: int,
    total_pages: int,
    last_page_size: int,
    paginator_buttons_disabled: bool = False,
) -> None:
    # ideally you cache this somehow instead of making one DB call for every button click
    data = await fetch_user_todo_list(inter.author.id)
    pages = []
    base = 0

    if data:
        # we split our data nicely into pages
        # ideally you don't do this for every button click, you just do it the first time
        # then cache it and reuse
        for _ in range(total_pages):
            page = []
            for j in range(base, base + 5):
                if j >= len(data):
                    break

                d = data[j]
                page.append(
                    ui.Section(
                        ui.TextDisplay(f"## {d['title']}"),
                        ui.TextDisplay(
                            f"{d['description']}\n**{d['status']}**  •  {disnake.utils.format_dt(d['deadline'])}"
                        ),
                        # just some empty chars, don't mind them
                        accessory=ui.Button(
                            label="⋮‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎Options",  # noqa: PLE2502
                            custom_id=f"todo_options:{inter.author.id}:{d['id']}",
                        ),
                    )
                )

                # we don't put separators after the last element of
                # a page and, in the last page, after the last element (of a non fully filled page)
                if ((j + 1) % 5 != 0) and j != len(data) - 1:
                    page.append(ui.Separator(spacing=disnake.SeparatorSpacing.large))
            base += 5
            pages.append(page)
    else:
        pages.append(ui.TextDisplay("__No TODOs yet :(__"))

    components = [
        ui.Container(
            ui.TextDisplay(f"# `{inter.author}`'s TODO list"),
            *pages[current_page],
        ),
        ui.ActionRow(
            ui.Button(
                emoji="⏪",
                custom_id=f"todo_f_back_btn:{inter.author.id}:{current_page}:{total_pages}:{last_page_size}",
                # this button is disabled if all the buttons for the paginator are disabled or
                # if we are at the first page
                disabled=paginator_buttons_disabled or (current_page == 0),
            ),
            ui.Button(
                emoji="◀️",
                custom_id=f"todo_back_btn:{inter.author.id}:{current_page}:{total_pages}:{last_page_size}",
                disabled=paginator_buttons_disabled,
            ),
            ui.Button(label=f"{current_page + 1}/{total_pages}", disabled=True),
            ui.Button(
                emoji="▶️",
                custom_id=f"todo_next_btn:{inter.author.id}:{current_page}:{total_pages}:{last_page_size}",
                disabled=paginator_buttons_disabled,
            ),
            ui.Button(
                emoji="⏩",
                custom_id=f"todo_f_next_btn:{inter.author.id}:{current_page}:{total_pages}:{last_page_size}",
                # this button is disabled if all the buttons for the paginator are disabled or
                # if we are at the last page
                disabled=paginator_buttons_disabled or (current_page == (total_pages - 1)),
            ),
        ),
    ]

    if isinstance(inter, disnake.ApplicationCommandInteraction):
        # this means that we are sending the first page
        return await inter.send(components=components)
    await inter.response.edit_message(components=components)


@bot.listen(disnake.Event.button_click)
async def back_btn(inter: disnake.MessageInteraction) -> None:
    if not inter.component.custom_id:
        return

    # remember that this is a normal listener and will get called
    # for every global button click so we ignore every other component
    # except for the one we really care (todo_back_btn)
    if not inter.component.custom_id.startswith("todo_back_btn"):
        return

    # we get our data from the button custom id that we built previously
    invoker_id, current_page, total_pages, last_page_size = map(
        int, inter.component.custom_id.split(":")[1:]
    )
    await interaction_check(inter, invoker_id, inter.author.id)

    # we implement a pac-man like effect, if you are at the first page
    # it will bring you at the last page
    if current_page == 0:
        current_page = total_pages - 1
    else:
        current_page -= 1

    await send_page(inter, current_page, total_pages, last_page_size)


@bot.listen(disnake.Event.button_click)
async def fast_back_btn(inter: disnake.MessageInteraction) -> None:
    if not inter.component.custom_id:
        return

    if not inter.component.custom_id.startswith("todo_f_back_btn"):
        return

    # remember that this is a normal listener and will get called
    # for every global button click so we ignore every other component
    # except for the one we really care (todo_next_btn)
    invoker_id, current_page, total_pages, last_page_size = map(
        int, inter.component.custom_id.split(":")[1:]
    )
    await interaction_check(inter, invoker_id, inter.author.id)

    # bring the user to the first page
    current_page = 0
    await send_page(inter, current_page, total_pages, last_page_size)


@bot.listen(disnake.Event.button_click)
async def next_btn(inter: disnake.MessageInteraction) -> None:
    if not inter.component.custom_id:
        return

    if not inter.component.custom_id.startswith("todo_next_btn"):
        return

    # remember that this is a normal listener and will get called
    # for every global button click so we ignore every other component
    # except for the one we really care (todo_next_btn)
    invoker_id, current_page, total_pages, last_page_size = map(
        int, inter.component.custom_id.split(":")[1:]
    )
    await interaction_check(inter, invoker_id, inter.author.id)

    # we implement a pac-man like effect, if you are at the last page
    # it will bring you at the first page
    if current_page == (total_pages - 1):
        current_page = 0
    else:
        current_page += 1

    await send_page(inter, current_page, total_pages, last_page_size)


@bot.listen(disnake.Event.button_click)
async def fast_next_btn(inter: disnake.MessageInteraction) -> None:
    if not inter.component.custom_id:
        return

    if not inter.component.custom_id.startswith("todo_f_next_btn"):
        return

    # remember that this is a normal listener and will get called
    # for every global button click so we ignore every other component
    # except for the one we really care (todo_next_btn)
    invoker_id, current_page, total_pages, last_page_size = map(
        int, inter.component.custom_id.split(":")[1:]
    )
    await interaction_check(inter, invoker_id, inter.author.id)

    # bring the user to the last page
    current_page = total_pages - 1
    await send_page(inter, current_page, total_pages, last_page_size)


@bot.listen(disnake.Event.button_click)
async def options_btn(inter: disnake.MessageInteraction) -> None:
    if not inter.component.custom_id:
        return

    if not inter.component.custom_id.startswith("todo_options"):
        return

    invoker_id, _ = map(int, inter.component.custom_id.split(":")[1:])
    await interaction_check(inter, invoker_id, inter.author.id)
    await inter.send(
        "Implement this logic yourself! You should now understand how this works.", ephemeral=True
    )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
