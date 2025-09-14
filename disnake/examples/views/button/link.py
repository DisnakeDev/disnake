# SPDX-License-Identifier: MIT

"""An example using link buttons in views."""

# Note: this example mostly exists for completeness.
# There is no point in creating a view if there are no components that
# would send interactions, e.g. only link buttons.
# Instead, one could also skip the view entirely and just use:
# `ctx.send(..., components=[disnake.ui.Button(label="Click Here", url=url)])`

import os
from urllib.parse import quote_plus

import disnake
from disnake.ext import commands


# Define a simple View that gives us a google link button.
# We take in `query` as the query that the command author requested.
class Google(disnake.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # Quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = f"https://www.google.com/search?q={query}"

        # Link buttons cannot be made with the decorator, therefore we have to manually create one.
        # We add the url to the button, and add the button to the view.
        self.add_item(disnake.ui.Button(label="Click Here", url=url))


bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.command()
async def google(ctx: commands.Context, *, query: str):
    """Returns a google link for a query"""
    clean_query = await commands.clean_content().convert(ctx, query)
    await ctx.send(f"Google Result for: `{clean_query}`", view=Google(query))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
