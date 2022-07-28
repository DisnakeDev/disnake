import os
from typing import List

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)

# You may even add autocompletion for your commands.
# This requires the type to be a string and for you to not use enumeration.
# Your autocompleter may return either a dict of names to values or a list of names
# but the amount of options cannot be more than 20.

LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "Rust", "Lisp", "Elixir"]


async def autocomplete_langs(inter, string: str) -> List[str]:
    return [lang for lang in LANGUAGES if string.lower() in lang.lower()]


@bot.slash_command()
async def autocomplete(
    inter: disnake.CommandInteraction,
    language: str = commands.Param(autocomplete=autocomplete_langs),
):
    ...


# In case you don't want to use Param or need to use self in a cog you may
# create autocomplete options with the decorator @slash_command.autocomplete()
@bot.slash_command()
async def languages(inter: disnake.CommandInteraction, language: str):
    ...


@languages.autocomplete("language")
async def language_autocomp(inter: disnake.CommandInteraction, string: str):
    string = string.lower()
    return [lang for lang in LANGUAGES if string in lang.lower()]


bot.run(os.getenv("BOT_TOKEN"))
