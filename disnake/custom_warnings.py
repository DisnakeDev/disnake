# SPDX-License-Identifier: MIT

from __future__ import annotations

__all__ = (
    "DiscordWarning",
    "ConfigWarning",
    "SyncWarning",
    "LocalizationWarning",
)


class DiscordWarning(Warning):
    """
    Base warning class for disnake.

    .. versionadded:: 2.3
    """

    pass


class ConfigWarning(DiscordWarning):
    """
    Warning class related to configuration issues.

    .. versionadded:: 2.3
    """

    pass


class SyncWarning(DiscordWarning):
    """
    Warning class for application command synchronization issues.

    .. versionadded:: 2.3
    """

    pass


class LocalizationWarning(DiscordWarning):
    """
    Warning class for localization issues.

    .. versionadded:: 2.5
    """

    pass
