from __future__ import annotations

__all__ = (
    "DiscordWarning",
    "ConfigWarning",
    "SyncWarning",
)


class DiscordWarning(Warning):
    """
    Base warning class for disnake
    """

    pass


class ConfigWarning(DiscordWarning):
    """
    Warning class related to configuration issues
    """

    pass


class SyncWarning(DiscordWarning):
    """
    Warning class for application command synchronization issues
    """

    pass
