# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from .emoji import Emoji
    from .snowflake import Snowflake, SnowflakeList

OnboardingPromptType = Literal[0, 1]


class OnboardingPromptOption(TypedDict):
    id: Snowflake
    title: str
    description: str | None
    emoji: Emoji
    role_ids: SnowflakeList
    channel_ids: SnowflakeList


class OnboardingPrompt(TypedDict):
    id: Snowflake
    title: str
    options: list[OnboardingPromptOption]
    single_select: bool
    required: bool
    in_onboarding: bool
    type: OnboardingPromptType


class Onboarding(TypedDict):
    guild_id: Snowflake
    prompts: list[OnboardingPrompt]
    default_channel_ids: SnowflakeList
    enabled: bool
