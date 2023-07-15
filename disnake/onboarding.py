# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, FrozenSet, Iterable, List, Optional, Union

from .emoji import Emoji, PartialEmoji
from .enums import OnboardingMode, OnboardingPromptType, try_enum
from .mixins import Hashable
from .object import Object

if TYPE_CHECKING:
    from typing_extensions import Self

    from .abc import Snowflake
    from .guild import Guild, GuildChannel
    from .types.emoji import Emoji as EmojiPayload
    from .types.onboarding import (
        Onboarding as OnboardingPayload,
        OnboardingPrompt as OnboardingPromptPayload,
        OnboardingPromptOption as OnboardingPromptOptionPayload,
    )

__all__ = (
    "Onboarding",
    "OnboardingPrompt",
    "OnboardingPromptOption",
)


class Onboarding:
    """Represents a guild onboarding object.

    .. versionadded:: 2.9

    Attributes
    ----------
    guild: :class:`Guild`
        The guild this onboarding is part of.
    prompts: List[:class:`OnboardingPrompt`]
        The prompts shown during onboarding and in community customization.
    enabled: :class:`bool`
        Whether onboarding is enabled.
    default_channel_ids: FrozenSet[:class:`int`]
        The IDs of the channels that will be shown to new members by default.
    mode: :class:`OnboardingMode`
        The onboarding mode, defining criteria for enabling onboarding.
    """

    __slots__ = ("guild", "prompts", "enabled", "default_channel_ids", "mode")

    def __init__(self, *, guild: Guild, data: OnboardingPayload) -> None:
        self.guild: Guild = guild
        self._from_data(data)

    def _from_data(self, data: OnboardingPayload) -> None:
        self.prompts: List[OnboardingPrompt] = [
            OnboardingPrompt._from_dict(data=prompt, guild=self.guild) for prompt in data["prompts"]
        ]
        self.enabled: bool = data["enabled"]
        self.default_channel_ids: FrozenSet[int] = (
            frozenset(map(int, exempt_channels))
            if (exempt_channels := data["default_channel_ids"])
            else frozenset()
        )
        self.mode: OnboardingMode = try_enum(OnboardingMode, data["mode"])

    def __repr__(self) -> str:
        return (
            f"<Onboarding guild={self.guild!r} prompts={self.prompts!r} enabled={self.enabled!r}>"
        )

    @property
    def default_channels(self) -> List[GuildChannel]:
        """List[:class:`abc.GuildChannel`]: The list of channels that will be shown to new members by default."""
        return list(filter(None, map(self.guild.get_channel, self.default_channel_ids)))


class OnboardingPrompt(Hashable):
    """Represents an onboarding prompt.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The onboarding prompt's ID. Note that if this onboarding prompt was manually constructed,
        this will be ``0``.
    title: :class:`str`
        The onboarding prompt's title.
    options: List[:class:`OnboardingPromptOption`]
        The onboarding prompt's options.
    type: :class:`OnboardingPromptType`
        The onboarding prompt's type.
    single_select: :class:`bool`
        Whether users are limited to selecting one option for the prompt.
    required: :class:`bool`
        Whether the prompt is required before a user completes the onboarding flow.
    in_onboarding: :class:`bool`
        Whether the prompt is present in the onboarding flow.
        If ``False``, the prompt will only appear in community customization.
    """

    __slots__ = ("id", "title", "options", "single_select", "required", "in_onboarding", "type")

    def __init__(
        self,
        *,
        title: str,
        options: List[OnboardingPromptOption],
        type: OnboardingPromptType,
        single_select: bool,
        required: bool,
        in_onboarding: bool,
    ) -> None:
        self.id: int = 0
        self.title: str = title
        self.options: List[OnboardingPromptOption] = options
        self.single_select: bool = single_select
        self.required: bool = required
        self.in_onboarding: bool = in_onboarding
        self.type: OnboardingPromptType = type

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            f"<OnboardingPrompt id={self.id!r} title={self.title!r} options={self.options!r}"
            f" single_select={self.single_select!r} required={self.required!r}"
            f" in_onboarding={self.in_onboarding!r} type={self.type!r}>"
        )

    @classmethod
    def _from_dict(cls, *, data: OnboardingPromptPayload, guild: Guild) -> Self:
        self = cls(
            title=data["title"],
            options=[
                OnboardingPromptOption._from_dict(data=option, guild=guild)
                for option in data["options"]
            ],
            single_select=data["single_select"],
            required=data["required"],
            in_onboarding=data["in_onboarding"],
            type=try_enum(OnboardingPromptType, data["type"]),
        )
        if "id" in data:
            self.id = int(data["id"])
        return self

    def to_dict(self) -> OnboardingPromptPayload:
        return {
            "id": self.id,
            "title": self.title,
            "options": [option.to_dict() for option in self.options],
            "single_select": self.single_select,
            "required": self.required,
            "in_onboarding": self.in_onboarding,
            "type": self.type.value,
        }


class OnboardingPromptOption(Hashable):
    """Represents an onboarding prompt option.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The onboarding prompt option's ID. Note that if this onboarding prompt option was manually constructed,
        this will be ``0``.
    title: :class:`str`
        The prompt option's title.
    description: Optional[:class:`str`]
        The prompt option's description.
    emoji: Optional[Union[:class:`PartialEmoji`, :class:`Emoji`, :class:`str`]]
        The prompt option's emoji.
    roles: Optional[FrozenSet[:class:`abc.Snowflake`]]
        The IDs of the roles that will be added to the user when they select this option.
    channels: Optional[FrozenSet[:class:`abc.Snowflake`]]
        The IDs of the channels that the user will see when they select this option.
    """

    __slots__ = ("id", "title", "description", "emoji", "guild", "roles", "channels")

    def __init__(
        self,
        *,
        title: str,
        description: Optional[str] = None,
        emoji: Optional[Union[str, PartialEmoji, Emoji]] = None,
        roles: Optional[Iterable[Snowflake]] = None,
        channels: Optional[Iterable[Snowflake]] = None,
    ) -> None:
        if roles is None and channels is None:
            raise TypeError("Either roles or channels must be provided.")

        self.id: int = 0
        self.title: str = title
        self.description: Optional[str] = description
        self.roles: FrozenSet[Snowflake] = frozenset(roles) if roles else frozenset()
        self.channels: FrozenSet[Snowflake] = frozenset(channels) if channels else frozenset()
        self.emoji: Optional[Union[Emoji, PartialEmoji, str]] = emoji

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            f"<OnboardingPromptOption id={self.id!r} title={self.title!r} "
            f"description={self.description!r} emoji={self.emoji!r}>"
        )

    @classmethod
    def _from_dict(cls, *, data: OnboardingPromptOptionPayload, guild: Guild) -> Self:
        if emoji_data := data.get("emoji"):
            emoji = guild._state.get_reaction_emoji(emoji_data)
        else:
            emoji = None

        self = cls(
            title=data["title"],
            description=data.get("description"),
            emoji=emoji,
            roles=[Object(id=role_id) for role_id in data["role_ids"]],
            channels=[Object(id=channel_id) for channel_id in data["channel_ids"]],
        )
        if "id" in data:
            self.id = int(data["id"])
        return self

    def to_dict(self) -> OnboardingPromptOptionPayload:
        emoji: EmojiPayload = {}  # type: ignore

        if isinstance(self.emoji, (Emoji, PartialEmoji)):
            emoji = self.emoji._to_partial().to_dict()
        elif isinstance(self.emoji, str):
            emoji["name"] = self.emoji

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "emoji": emoji,
            "role_ids": [role.id for role in self.roles],
            "channel_ids": [channel.id for channel in self.channels],
        }
