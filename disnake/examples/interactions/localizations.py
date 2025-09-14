# SPDX-License-Identifier: MIT

"""An example on how to set up localized application commands."""

import os
from typing import Any

import disnake
from disnake import Localized, OptionChoice
from disnake.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned)


# For more details, see https://docs.disnake.dev/en/stable/ext/commands/slash_commands.html#localizations

# For this example to work, you need to create a file `locale/de.json` containing the following:
"""
{
    "HIGHSCORE_COMMAND_NAME": "rekord",
    "HIGHSCORE_COMMAND_DESCRIPTION": "Zeigt die Rekordpunktzahl des Users innerhalb des gewählten Zeitraums.",
    "HIGHSCORE_USER_NAME": "user",
    "HIGHSCORE_USER_DESCRIPTION": "Der User, dessen Punktzahl gezeigt werden soll.",
    "HIGHSCORE_GAME_NAME": "spiel",
    "HIGHSCORE_GAME_DESCRIPTION": "Spiel, für das Punktzahlen gefiltert werden.",
    "HIGHSCORE_RANGE_NAME": "zeitraum",
    "HIGHSCORE_RANGE_DESCRIPTION": "Der Zeitraum zur Berechnung der Rekordpunktzahl.",

    "CHOICE_DAY": "Letzter Tag",
    "CHOICE_WEEK": "Letzte Woche",
    "CHOICE_MONTH": "Letzter Monat",

    "GAME_TIC-TAC-TOE": "Tic-Tac-Toe",
    "GAME_CHESS": "Schach",
    "GAME_RISK": "Risiko"
}
"""


# localizations need to be loaded before the commands are defined
bot.i18n.load(f"{os.path.dirname(__file__)}/locale/")


@bot.slash_command()
async def highscore(
    inter: disnake.CommandInteraction,
    user: disnake.User,
    game: str,
    interval: str = commands.Param(
        choices=[
            OptionChoice(Localized("Last Day", key="CHOICE_DAY"), "day"),
            OptionChoice(Localized("Last Week", key="CHOICE_WEEK"), "week"),
            OptionChoice(Localized("Last Month", key="CHOICE_MONTH"), "month"),
        ]
    ),
):
    """Shows the highscore of the selected user within the specified interval.
    {{ HIGHSCORE_COMMAND }}

    Parameters
    ----------
    user: The user to show data for. {{ HIGHSCORE_USER }}
    game: Which game to check scores in. {{ HIGHSCORE_GAME }}
    interval: The time interval to use. {{ HIGHSCORE_RANGE }}
    """
    db: Any = ...  # a placeholder for an actual database connection
    data = await db.highscores.find(user=user.id, game=game).filter(interval).max()
    await inter.send(f"max: {data}")


@highscore.autocomplete("game")
async def game_autocomp(inter: disnake.CommandInteraction, string: str):
    # this clearly isn't great autocompletion as it autocompletes based on the English name,
    # but for the purposes of this example it'll do
    games = ("Tic-tac-toe", "Chess", "Risk")
    return [
        Localized(game, key=f"GAME_{game.upper()}")
        for game in games
        if string.lower() in game.lower()
    ]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
