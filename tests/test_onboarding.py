# SPDX-License-Identifier: MIT

from unittest import mock

import pytest

from disnake import (
    APIOnboardingPrompt,
    APIOnboardingPromptOption,
    Guild,
    Object,
    Onboarding,
    OnboardingPrompt,
    OnboardingPromptOption,
    OnboardingPromptType,
)
from disnake.types import onboarding as onboarding_types


@pytest.fixture
def onboarding_prompt_option() -> OnboardingPromptOption:
    return OnboardingPromptOption(
        title="title",
        description="description",
        emoji="🗿",
        roles=[Object(id=123)],
        channels=[Object(id=456)],
    )


@pytest.fixture
def api_onboarding_prompt_option() -> APIOnboardingPromptOption:
    return APIOnboardingPromptOption(
        guild=mock.Mock(Guild, id=123),
        data=onboarding_types.OnboardingPromptOption(
            id="0",
            title="title",
            description="description",
            emoji={"name": "🗿", "id": "", "animated": False},
            role_ids=["123", "456"],
            channel_ids=["789", "159"],
        ),
    )


@pytest.fixture
def onboarding_prompt() -> OnboardingPrompt:
    return OnboardingPrompt(
        title="title",
        options=[
            OnboardingPromptOption(
                title="title",
                description="description",
                emoji="🗿",
                roles=[Object(id=123)],
                channels=[Object(id=456)],
            )
        ],
        type=OnboardingPromptType.multiple_choice,
        single_select=True,
        required=True,
        in_onboarding=True,
    )


@pytest.fixture
def api_onboarding_prompt() -> APIOnboardingPrompt:
    return APIOnboardingPrompt(
        guild=mock.Mock(Guild, id=123),
        data=onboarding_types.OnboardingPrompt(
            id="0",
            title="title",
            options=[],
            single_select=True,
            required=True,
            in_onboarding=True,
            type=OnboardingPromptType.multiple_choice.value,
        ),
    )


@pytest.fixture
def onboarding() -> Onboarding:
    onboarding_payload: onboarding_types.Onboarding = {
        "guild_id": "123",
        "prompts": [],
        "default_channel_ids": ["456", "789"],
        "enabled": True,
        "mode": 0,
    }

    return Onboarding(
        guild=mock.Mock(Guild, id=123),
        data=onboarding_payload,
    )


class TestOnboarding:
    def test_onboarding(self, onboarding: Onboarding) -> None:
        assert onboarding.guild.id == 123
        assert onboarding.prompts == []
        assert onboarding.default_channel_ids == frozenset([456, 789])
        assert onboarding.enabled is True


class TestOnboardingPrompt:
    def test_onboarding_prompt(
        self, onboarding_prompt: OnboardingPrompt, onboarding_prompt_option: OnboardingPromptOption
    ) -> None:
        assert onboarding_prompt.id == 0
        assert onboarding_prompt.title == "title"
        assert onboarding_prompt.options == [onboarding_prompt_option]
        assert onboarding_prompt.type == OnboardingPromptType.multiple_choice
        assert onboarding_prompt.single_select is True
        assert onboarding_prompt.required is True
        assert onboarding_prompt.in_onboarding is True

    def test_onboarding_prompt_str(self, onboarding_prompt: OnboardingPrompt) -> None:
        assert str(onboarding_prompt) == "title"


class TestAPIOnboardingPrompt:
    def test_api_onboarding_prompt(self, api_onboarding_prompt: APIOnboardingPrompt) -> None:
        assert api_onboarding_prompt.title == "title"
        assert api_onboarding_prompt.options == []
        assert api_onboarding_prompt.single_select is True
        assert api_onboarding_prompt.required is True
        assert api_onboarding_prompt.in_onboarding is True
        assert api_onboarding_prompt.type == OnboardingPromptType.multiple_choice

    def test_onboarding_prompt_str(self, api_onboarding_prompt: APIOnboardingPrompt) -> None:
        assert str(api_onboarding_prompt) == "title"


class TestOnboardingPromptOption:
    def test_onboarding_prompt_option(
        self, onboarding_prompt_option: OnboardingPromptOption
    ) -> None:
        assert onboarding_prompt_option.title == "title"
        assert onboarding_prompt_option.description == "description"
        assert onboarding_prompt_option.emoji == "🗿"
        assert onboarding_prompt_option.role_ids == frozenset([123])
        assert onboarding_prompt_option.channel_ids == frozenset([456])

    def test_onboarding_prompt_option_str(
        self, api_onboarding_prompt_option: APIOnboardingPromptOption
    ) -> None:
        assert str(api_onboarding_prompt_option) == "title"


class TestAPIOnboardingPromptOption:
    def test_api_onboarding_prompt_option(
        self, api_onboarding_prompt_option: APIOnboardingPromptOption
    ) -> None:
        assert api_onboarding_prompt_option.title == "title"
        assert api_onboarding_prompt_option.description == "description"
        assert api_onboarding_prompt_option.role_ids == frozenset([123, 456])
        assert api_onboarding_prompt_option.channel_ids == frozenset([789, 159])

    def test_api_onboarding_prompt_option_str(
        self, api_onboarding_prompt_option: APIOnboardingPromptOption
    ) -> None:
        assert str(api_onboarding_prompt_option) == "title"
