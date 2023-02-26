# SPDX-License-Identifier: MIT

"""A simple example using custom a command context type."""

import os
import random

import disnake
from disnake.ext import commands


class MyContext(commands.Context):
    async def tick(self, value: bool):
        # reacts to the message with an emoji
        # depending on whether value is True or False
        # if its True, it'll add a green check mark
        # otherwise, it'll add a red cross mark
        emoji = "\N{WHITE HEAVY CHECK MARK}" if value else "\N{CROSS MARK}"

        try:
            # this will react to the command author's message
            await self.message.add_reaction(emoji)
        except disnake.HTTPException:
            # sometimes errors occur during this, for example
            # maybe you don't have permission to do that
            # we don't mind, so we can just ignore them
            pass


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=MyContext):
        # when you override this method, you pass your new Context
        # subclass to the super() method, which tells the bot to
        # use the new MyContext class
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")


bot = MyBot(command_prefix=commands.when_mentioned)


@bot.command()
async def guess(ctx: MyContext, number: int):
    """Guess a random number from 1 to 6."""
    value = random.randint(1, 6)
    # with your new helper function, you can add a
    # green check mark if the guess was correct,
    # or a red cross mark if it wasn't
    await ctx.tick(number == value)


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
