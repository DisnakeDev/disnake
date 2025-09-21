# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict

from .emoji import Emoji
from .snowflake import Snowflake, SnowflakeList

OnboardingPromptType = Literal[0, 1]


class OnboardingPromptOption(TypedDict):
    id: Snowflake
    title: str
    description: Optional[str]
    emoji: Emoji
    role_ids: SnowflakeList
    channel_ids: SnowflakeList


class OnboardingPrompt(TypedDict):
    id: Snowflake
    title: str
    options: List[OnboardingPromptOption]
    single_select: bool
    required: bool
    in_onboarding: bool
    type: OnboardingPromptType


class Onboarding(TypedDict):
    guild_id: Snowflake
    prompts: List[OnboardingPrompt]
    default_channel_ids: SnowflakeList
    enabled: bool
