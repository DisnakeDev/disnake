import random
from pprint import pformat
from typing import List

import disnake
from disnake.ext import commands


class Localizations(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command()
    async def localized_command(
        self,
        inter: disnake.AppCmdInter,
        auto: str,
        choice: str = commands.Param(
            choices=[
                # lookup keys for choices
                disnake.OptionChoice("a", "a", name_localizations="CHOICE_A"),
                disnake.OptionChoice("o", "o", name_localizations="CHOICE_O"),
                disnake.OptionChoice("u", "u", name_localizations="CHOICE_U"),
            ]
        ),
        other: str = commands.Param(
            # by lookup key
            name_localizations="OTHER_NAME",
            # specify localizations directly
            description_localizations={"en-GB": "insert bri'ish description here"},
        ),
    ) -> None:
        """
        {{ MY_LOC_CMD }} Does absolutely nothing

        Parameters
        ----------
        auto: Autocompletes with numbers from 1-5
        choice: Shows umlauts for german users {{CHOICE_PARAM}}
        other: Another value
        """
        await inter.response.send_message(f"```py\n{pformat(locals())}\n```")

    @localized_command.autocomplete("auto")
    async def autocomp(self, inter: disnake.AppCmdInter, value: str) -> List[disnake.OptionChoice]:
        # not really autocomplete, only used for showing autocomplete localization
        x = list(map(str, range(1, 6)))
        random.shuffle(x)
        return [disnake.OptionChoice(v, v, name_localizations=f"AUTOCOMP_{v}") for v in x]

    @commands.slash_command()
    async def localized_top_level(self, inter: disnake.AppCmdInter) -> None:
        pass

    @localized_top_level.sub_command_group()
    async def second(self, inter: disnake.AppCmdInter) -> None:
        pass

    @second.sub_command(
        name_localizations={"en-GB": "british_subcommand"},
        description_localizations="MY_SUBCMD_DESC",
    )
    async def third(
        self,
        inter: disnake.AppCmdInter,
        value: str = commands.Param(name="a_string", name_localizations="A_VERY_COOL_PARAM_NAME"),
    ) -> None:
        await inter.response.send_message(f"```py\n{pformat(locals())}\n```")

    # works for message/user commands as well
    @commands.message_command(
        name="Localized Reverse",
        name_localizations="MSG_REVERSE",
    )
    async def cmd_msg(self, inter: disnake.AppCmdInter, msg: disnake.Message) -> None:
        await inter.response.send_message(msg.content[::-1])


def setup(bot):
    bot.add_cog(Localizations(bot))
    print(f"> Extension {__name__} is ready\n")
