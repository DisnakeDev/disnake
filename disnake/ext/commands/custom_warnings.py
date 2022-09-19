# SPDX-License-Identifier: MIT

from disnake import DiscordWarning

__all__ = ("MessageContentPrefixWarning",)


class MessageContentPrefixWarning(DiscordWarning):
    """
    Warning for invalid prefixes without message content.
    """

    pass
