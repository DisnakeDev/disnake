# SPDX-License-Identifier: MIT

from unittest import mock

import pytest

from disnake import (
    Guild,
    Object,
    Onboarding,
    OnboardingPrompt,
    OnboardingPromptOption,
    OnboardingPromptType,
    PartialEmoji,
)
from disnake.types import onboarding as onboarding_types

onboarding_prompt_option_payload: onboarding_types.OnboardingPromptOption = {
    "id": "0",
    "title": "test",
    "description": "test",
    "emoji": {"id": "123", "name": "", "animated": False},
    "role_ids": ["456", "789"],
    "channel_ids": ["123", "456"],
}


@pytest.fixture
def onboarding_prompt_option() -> OnboardingPromptOption:
    return OnboardingPromptOption(
        title="test",
        description="test",
        emoji=PartialEmoji(name="", id=123, animated=False),
        roles=[Object(id="456"), Object(id="789")],
        channels=[Object(id="123"), Object(id="456")],
        guild=mock.Mock(Guild, id=123),
    )


@pytest.fixture
def onboarding_prompt() -> OnboardingPrompt:
    onboarding_prompt_payload: onboarding_types.OnboardingPrompt = {
        "id": 0,
        "title": "test",
        "options": [],
        "single_select": True,
        "required": True,
        "in_onboarding": True,
        "type": OnboardingPromptType.multiple_choice.value,
    }

    return OnboardingPrompt(data=onboarding_prompt_payload, guild=mock.Mock(Guild, id=123))


@pytest.fixture
def onboarding() -> Onboarding:
    onboarding_payload: onboarding_types.Onboarding = {
        "guild_id": "123",
        "prompts": [],
        "default_channel_ids": ["456", "789"],
        "enabled": True,
    }

    return Onboarding(
        guild=mock.Mock(Guild, id=123),
        data=onboarding_payload,
    )


class TestOnboarding:
    def test_onboarding(self, onboarding: Onboarding) -> None:
        assert onboarding.guild.id == 123
        assert onboarding.prompts == []
        assert onboarding._default_channel_ids == [456, 789]
        assert onboarding.enabled is True


class TestOnboardingPrompt:
    def test_onboarding_prompt(self, onboarding_prompt: OnboardingPrompt) -> None:
        assert onboarding_prompt.title == "test"
        assert onboarding_prompt.options == []
        assert onboarding_prompt.single_select is True
        assert onboarding_prompt.required is True
        assert onboarding_prompt.in_onboarding is True
        assert onboarding_prompt.type == OnboardingPromptType.multiple_choice

    def test_onboarding_prompt_str(self, onboarding_prompt: OnboardingPrompt) -> None:
        assert str(onboarding_prompt) == "test"


class TestOnboardingPromptOption:
    def test_onboarding_prompt_option(
        self, onboarding_prompt_option: OnboardingPromptOption
    ) -> None:
        assert onboarding_prompt_option.title == "test"
        assert onboarding_prompt_option.description == "test"
        assert onboarding_prompt_option.emoji == PartialEmoji(name="", id=123, animated=False)
        assert onboarding_prompt_option.roles == [Object(id="456"), Object(id="789")]
        assert onboarding_prompt_option.channels == [Object(id="123"), Object(id="456")]

    def test_onboarding_prompt_option_str(
        self, onboarding_prompt_option: OnboardingPromptOption
    ) -> None:
        assert str(onboarding_prompt_option) == "test"
