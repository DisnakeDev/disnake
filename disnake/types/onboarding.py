# SPDX-License-Identifier: MIT

from typing import List, Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake, SnowflakeList

# NOTE: PartialOnboardingXX is very redundant, TBD


class OnboardingPromptOption(TypedDict):
    id: Snowflake
    title: str
    description: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    role_ids: SnowflakeList
    channel_ids: SnowflakeList


class PartialOnboardingPromptOption(TypedDict):
    id: NotRequired[Snowflake]
    title: str
    description: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    role_ids: SnowflakeList
    channel_ids: SnowflakeList


class OnboardingPrompt(TypedDict):
    id: Snowflake
    title: str
    options: List[OnboardingPromptOption]
    single_select: bool
    required: bool
    in_onboarding: bool
    type: int


class PartialOnboardingPrompt(TypedDict):
    id: NotRequired[Snowflake]
    title: str
    options: List[PartialOnboardingPromptOption]
    single_select: bool
    required: bool
    in_onboarding: bool
    type: int


class Onboarding(TypedDict):
    guild_id: Snowflake
    prompts: List[OnboardingPrompt]
    enable_onboarding_prompts: bool
    enable_default_channels: bool
    default_channel_ids: SnowflakeList
    # NOTE: client only?
    responses: SnowflakeList
    enabled: bool


class EditOnboarding(TypedDict):
    prompts: List[PartialOnboardingPrompt]
    enable_onboarding_prompts: bool
    enable_default_channels: bool
    default_channel_ids: SnowflakeList
