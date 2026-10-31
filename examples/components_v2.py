# SPDX-License-Identifier: MIT

"""An example showcasing v2/layout components."""

from __future__ import annotations

import asyncio
import datetime
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple

import disnake
from disnake import ui
from disnake.ext import commands

if TYPE_CHECKING:
    from disnake.ui._types import MessageComponents


bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def send_components(ctx: commands.Context) -> None:
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


async def fetch_websites() -> list[Website]:
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
    file_names = await asyncio.to_thread(lambda: list(Path("assets/").glob("*.png")))
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

    total_pages, last_page_size = divmod(len(data), TODO_PER_PAGE)
    if last_page_size != 0:
        total_pages += 1

    paginator_buttons_disabled = len(data) == TODO_PER_PAGE
    data = await fetch_user_todo_list(inter.author.id)
    await inter.send(
        components=build_todo_components(
            inter.author, data, 0, total_pages, last_page_size, paginator_buttons_disabled
        )
    )


def build_todo_components(
    author: disnake.abc.Snowflake,
    data: list[dict[str, Any]],
    current_page: int,
    total_pages: int,
    last_page_size: int,
    paginator_buttons_disabled: bool = False,
) -> MessageComponents:
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
                            custom_id=f"todo_options:{author.id}:{d['id']}",
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

    return [
        ui.Container(
            ui.TextDisplay(f"# `{author}`'s TODO list"),
            *pages[current_page],
        ),
        ui.ActionRow(
            ui.Button(
                emoji="⏪",
                custom_id=f"todo_f_back_btn:{author.id}:{current_page}:{total_pages}:{last_page_size}",
                # this button is disabled if all the buttons for the paginator are disabled or
                # if we are at the first page
                disabled=paginator_buttons_disabled or (current_page == 0),
            ),
            ui.Button(
                emoji="◀️",
                custom_id=f"todo_back_btn:{author.id}:{current_page}:{total_pages}:{last_page_size}",
                disabled=paginator_buttons_disabled,
            ),
            ui.Button(label=f"{current_page + 1}/{total_pages}", disabled=True),
            ui.Button(
                emoji="▶️",
                custom_id=f"todo_next_btn:{author.id}:{current_page}:{total_pages}:{last_page_size}",
                disabled=paginator_buttons_disabled,
            ),
            ui.Button(
                emoji="⏩",
                custom_id=f"todo_f_next_btn:{author.id}:{current_page}:{total_pages}:{last_page_size}",
                # this button is disabled if all the buttons for the paginator are disabled or
                # if we are at the last page
                disabled=paginator_buttons_disabled or (current_page == (total_pages - 1)),
            ),
        ),
    ]


@bot.listen(disnake.Event.message_interaction)
async def _(inter: disnake.MessageInteraction) -> None:
    # I suggest namespacing (prefixing) all components with the "UI name" they come from,
    # for easy interception and avoiding potential name clashes
    if not inter.data.custom_id.startswith("todo:"):
        return

    _, component_id, data = inter.data.custom_id.split(":", 2)
    invoker_id, current_page, total_pages, last_page_size = map(int, data.split(":"))

    if inter.author.id != invoker_id:
        await inter.response.send_message(
            "You can't interact with this component :(", ephemeral=True
        )
        return

    match component_id:
        case "todo_back_btn":
            current_page = (current_page - 1 + total_pages) % total_pages

        case "todo_f_back_btn":
            current_page = 0

        case "todo_next_btn":
            current_page = (current_page + 1) % total_pages

        case "todo_f_next_btn":
            current_page = total_pages - 1

        case "todo_options":
            await inter.send(
                "Implement this logic yourself! You should now understand how this works.",
                ephemeral=True,
            )
            return

        case _:
            # this could happen if you changed/removed a component's ID in code,
            # but a UI created with old code still exists somewhere
            raise Warning("/todo - unknown component: %s", component_id)

    todo_list = await fetch_user_todo_list(inter.author.id)
    components = build_todo_components(
        inter.author, todo_list, current_page, total_pages, last_page_size
    )

    # no need to isinstance() branch on interaction type, you always
    # .send_message in /command callbacks and .edit_message in on_message_interaction
    await inter.response.edit_message(components=components)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
