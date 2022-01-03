import logging
import os
import traceback

import disnake
from disnake.ext import commands

from . import config


def fancy_traceback(exc: Exception) -> str:
    """May not fit the message content limit"""
    text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return f"```py\n{text[-4086:]}\n```"


logger = logging.getLogger(__name__)


class TestBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.Client.prefix,
            intents=disnake.Intents.all(),
            help_command=None,  # type: ignore
            sync_commands_debug=config.Client.sync_commands_debug,
            sync_permissions=config.Client.sync_permissions,
            test_guilds=config.Client.test_guilds,
            reload=config.Client.auto_reload,
        )

    def load_all_extensions(self, folder: str) -> None:
        py_path = f"test_bot.{folder}"
        folder = f"test_bot/{folder}"
        for name in os.listdir(folder):
            if name.endswith(".py") and os.path.isfile(f"{folder}/{name}"):
                self.load_extension(f"{py_path}.{name[:-3]}")

    async def on_ready(self):
        # fmt: off
        print(
            f"\n"
            f"The bot is ready.\n"
            f"User: {self.user}\n"
            f"ID: {self.user.id}\n"
        )
        # fmt: on

    def add_cog(self, cog, *, override: bool = False) -> None:
        logger.info(f"Loading cog {cog}.")
        return super().add_cog(cog, override=override)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        embed = disnake.Embed(
            title=f"Command `{ctx.command}` failed due to `{error}`",
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        await ctx.send(embed=embed)

    async def on_slash_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        embed = disnake.Embed(
            title=f"Slash command `{inter.data.name}` failed due to `{error}`",
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response._responded:
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)

    async def on_user_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        embed = disnake.Embed(
            title=f"User command `{inter.data.name}` failed due to `{error}`",
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response._responded:
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)

    async def on_message_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        embed = disnake.Embed(
            title=f"Message command `{inter.data.name}` failed due to `{error}`",
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response._responded:
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)


print(f"disnake: {disnake.__version__}\n")

if __name__ == "__main__":
    bot = TestBot()
    bot.load_all_extensions(config.Client.cogs_folder)
    bot.run(config.Client.token)
