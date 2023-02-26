# SPDX-License-Identifier: MIT

"""An example showcasing the two ways of adding autocompletion to slash command options."""

import os
from typing import List

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "Rust", "Lisp", "Elixir"]


# One way of adding autocompletion is through `Param` and the `autocomplete` parameter.

# Autocomplete only works with `str`, `int`, and `float` options,
# and the callback you provide must return a name->value dict,
# a list of names, or a list of `SelectOption`s,
# with up to 25 elements.


async def autocomplete_langs(inter, string: str) -> List[str]:
    string = string.lower()
    return [lang for lang in LANGUAGES if string in lang.lower()]


@bot.slash_command()
async def languages_1(
    inter: disnake.CommandInteraction,
    language: str = commands.Param(autocomplete=autocomplete_langs),
):
    ...


# Instead of using Param, you can also create autocomplete options
# with the `@<cmd>.autocomplete(<name>)` decorator, whose only argument
# is the option you want to enable autocomplete for.
# This is particularly useful in cogs, if you need access to `self` in
# your autocomplete callback.


@bot.slash_command()
async def languages_2(inter: disnake.CommandInteraction, language: str):
    ...


@languages_2.autocomplete("language")
async def language_autocomp(inter: disnake.CommandInteraction, string: str):
    string = string.lower()
    return [lang for lang in LANGUAGES if string in lang.lower()]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
