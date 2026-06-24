# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict

from .snowflake import Snowflake


class WelcomeScreen(TypedDict):
    description: str | None
    welcome_channels: list[WelcomeScreenChannel]


class WelcomeScreenChannel(TypedDict):
    channel_id: Snowflake
    description: str
    emoji_id: Snowflake | None
    emoji_name: str | None
