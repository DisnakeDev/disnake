# SPDX-License-Identifier: MIT

import asyncio
import logging
import os
import sys
import traceback

import disnake
from disnake.ext import commands

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from .config import Config

logger = logging.getLogger(__name__)

if not Config.test_guilds:
    logger.warning("No test guilds configured. Using global commands.")


def fancy_traceback(exc: Exception) -> str:
    """May not fit the message content limit"""
    text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return f"```py\n{text[-4086:]}\n```"


class TestBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=Config.prefix,
            intents=disnake.Intents.all(),
            help_command=None,
            command_sync_flags=commands.CommandSyncFlags.all(),
            strict_localization=Config.strict_localization,
            test_guilds=Config.test_guilds,
            reload=Config.auto_reload,
            enable_gateway_error_handler=Config.enable_gateway_error_handler,
        )

        self.i18n.load("test_bot/locale")

    async def on_ready(self) -> None:
        # fmt: off
        print(
            f"\n"
            f"The bot is ready.\n"
            f"User: {self.user}\n"
            f"ID: {self.user.id}\n"
        )
        # fmt: on

    def add_cog(self, cog: commands.Cog, *, override: bool = False) -> None:
        logger.info("Loading cog %s", cog.qualified_name)
        return super().add_cog(cog, override=override)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        msg = f"Command `{ctx.command}` failed due to `{error}`"
        logger.error(msg, exc_info=True)

        embed = disnake.Embed(
            title=msg,
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        await ctx.send(embed=embed)

    async def on_slash_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        msg = f"Slash command `{inter.data.name}` failed due to `{error}`"
        logger.error(msg, exc_info=True)

        embed = disnake.Embed(
            title=msg,
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response.is_done():
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)

    async def on_user_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        msg = f"User command `{inter.data.name}` failed due to `{error}`"
        logger.error(msg, exc_info=True)
        embed = disnake.Embed(
            title=msg,
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response.is_done():
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)

    async def on_message_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: commands.CommandError,
    ) -> None:
        msg = f"Message command `{inter.data.name}` failed due to `{error}`"
        logger.error(msg, exc_info=True)
        embed = disnake.Embed(
            title=msg,
            description=fancy_traceback(error),
            color=disnake.Color.red(),
        )
        if inter.response.is_done():
            send = inter.channel.send
        else:
            send = inter.response.send_message
        await send(embed=embed)


print(f"disnake: {disnake.__version__}\n")

if __name__ == "__main__":
    bot = TestBot()
    bot.load_extensions(os.path.join(__package__, Config.cogs_folder))
    bot.run(Config.token)
