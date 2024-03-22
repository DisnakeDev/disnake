# SPDX-License-Identifier: MIT

from typing import List, Literal, NotRequired, Optional, TypedDict

from .emoji import PartialEmoji
from .snowflake import Snowflake, SnowflakeList

OnboardingPromptType = Literal[0, 1]
OnboardingMode = Literal[0, 1]


class OnboardingPromptOption(TypedDict):
    id: Snowflake
    title: str
    description: Optional[str]
    emoji: NotRequired[PartialEmoji]  # deprecated
    emoji_id: NotRequired[Snowflake]
    emoji_name: NotRequired[str]
    emoji_animated: NotRequired[bool]
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
    mode: OnboardingMode


class EditOnboarding(TypedDict, total=False):
    prompts: List[OnboardingPrompt]
    default_channel_ids: SnowflakeList
    enabled: bool
    mode: OnboardingMode
