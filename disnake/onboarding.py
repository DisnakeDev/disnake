# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Union

from .emoji import Emoji, PartialEmoji, _EmojiTag
from .enums import OnboardingPromptType, try_enum
from .mixins import Hashable
from .object import Object

if TYPE_CHECKING:
    from typing_extensions import Self

    from .abc import Snowflake
    from .guild import Guild, GuildChannel
    from .state import ConnectionState
    from .types.onboarding import (
        Onboarding as OnboardingPayload,
        OnboardingPrompt as OnboardingPromptPayload,
        OnboardingPromptOption as OnboardingPromptOptionPayload,
        PartialOnboardingPrompt as PartialOnboardingPromptPayload,
        PartialOnboardingPromptOption as PartialOnboardingPromptOptionPayload,
    )

__all__ = (
    "Onboarding",
    "OnboardingPrompt",
    "OnboardingPromptOption",
)

# TODO: Audit log events


class Onboarding:  # NOTE: or GuildOnboarding?
    """Represents a guild onboarding.

    .. versionadded:: 2.9

    Attributes
    ----------
    guild: :class:`Guild`
        The guild this onboarding belongs to.
    prompts: List[:class:`OnboardingPrompt`]
        The prompts the onboarding has.
    enabled: bool
        Whether the onboarding is enabled.
    """

    __slots__ = (
        "guild",
        "prompts",
        "enabled",
        "_guild_id",
        "_default_channel_ids",
        "_state",
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: OnboardingPayload):
        self._state = state
        self.guild = guild
        self._from_data(data)

    def _from_data(self, data: OnboardingPayload):
        self.prompts = [
            OnboardingPrompt._from_dict(data=prompt, state=self._state)
            for prompt in data["prompts"]
        ]
        self.enabled = data["enabled"]
        self._guild_id = int(data["guild_id"])  # NOTE: is this required?
        self._default_channel_ids = list(map(int, data["default_channel_ids"]))

    def __repr__(self) -> str:
        return (
            f"<Onboarding guild_id={self.guild.id!r} prompts={self.prompts!r}"
            f" default_channel_ids={self._default_channel_ids!r} enabled={self.enabled!r}>"
        )

    @property
    def default_channels(self) -> List[GuildChannel]:
        """List[:class:`abc.GuildChannel`]: A list of channels that will display in Browse Channels."""
        return list(filter(None, map(self.guild._channels.get, self._default_channel_ids)))


class OnboardingPromptOption(Hashable):
    """Represents an onboarding prompt option.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The option's ID. Note that if this option was manually constructed,
        this will be ``0``.
    title: :class:`str`
        The option's title.
    description: :class:`str`
        The option's description.
    emoji: Optional[Union[:class:`str`, :class:`PartialEmoji`, :class:`Emoji`]]
        The option's emoji.
    roles: List[:class:`abc.Snowflake`]
        The roles that will be added to the user when they select this option.
    channels: List[:class:`abc.Snowflake`]
        The channels that the user will see when they select this option.
    """

    __slots__ = ("id", "title", "description", "emoji", "roles", "channels")

    def __init__(
        self,
        *,
        title: str,
        description: str,
        emoji: Union[str, PartialEmoji, Emoji],
        roles: Sequence[Snowflake],
        channels: Sequence[Snowflake],
    ):
        # NOTE: (a very very important note), the ID may sometimes be a UNIX timestamp since
        # Onboarding changes are saved locally until you send the API request (that's how it works in client)
        # so the API needs the timestamp to know what ID it needs to create, should we just add a note about it
        # or "try" to create the ID ourselves?
        # I'm not sure if this also happens for OnboardingPrompt
        self.id = 0
        self.title = title
        self.description = description
        self.roles = roles
        self.channels = channels

        self.emoji: Union[PartialEmoji, Emoji]
        if isinstance(emoji, str):
            self.emoji = PartialEmoji.from_str(emoji)
        elif isinstance(emoji, _EmojiTag):
            self.emoji = emoji
        else:
            raise TypeError("emoji must be a str, PartialEmoji, or Emoji instance")

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            f"<OnboardingPromptOption id={self.id!r} title={self.title!r} "
            f"description={self.description!r} emoji={self.emoji!r} "
            f"roles={self.roles!r} channels={self.channels!r}>"
        )

    def _to_dict(self) -> PartialOnboardingPromptOptionPayload:
        payload: PartialOnboardingPromptOptionPayload = {
            "title": self.title,
            "description": self.description,
            "emoji": self.emoji.to_dict(),
            "role_ids": [role.id for role in self.roles],
            "channel_ids": [channel.id for channel in self.channels],
        }

        if self.id:
            payload["id"] = self.id

        return payload

    @classmethod
    def _from_dict(cls, *, data: OnboardingPromptOptionPayload, state: ConnectionState) -> Self:
        emoji = PartialEmoji.from_dict(data["emoji"])

        self = cls(
            title=data["title"],
            description=data["description"],
            emoji=emoji,
            roles=[
                Object(id=role_id) for role_id in data["role_ids"]
            ],  # NOTE: should I get the Role here?
            channels=[
                Object(id=channel_id) for channel_id in data["channel_ids"]
            ],  # NOTE: should I get the channel here?
        )
        self.id = int(data["id"])
        return self


class OnboardingPrompt(Hashable):
    """Represents an onboarding prompt.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The onboarding prompt's ID. Note that if this prompt was manually constructed,
        this will be ``0``.
    title: :class:`str`
        The onboarding prompt's title.
    options: List[:class:`OnboardingPromptOption`]
        The onboarding prompt's options.
    single_select: :class:`bool`
        Whether only one option can be selected.
    required: :class:`bool`
        Whether one option must be selected.
    in_onboarding: :class:`bool`
        Whether this prompt is in the onboarding.
    type: :class:`OnboardingPromptType`
        The onboarding prompt's type.
    """

    __slots__ = ("id", "title", "options", "single_select", "required", "in_onboarding", "type")

    def __init__(
        self,
        *,
        title: str,
        options: List[OnboardingPromptOption],
        single_select: bool,
        required: bool,
        in_onboarding: bool,
        type: OnboardingPromptType,
    ):
        self.id = 0
        self.title = title
        self.options = options
        self.single_select = single_select
        self.required = required
        self.in_onboarding = in_onboarding
        self.type = type

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            f"<OnboardingPrompt id={self.id!r} title={self.title!r} options={self.options!r}"
            f" single_select={self.single_select!r} required={self.required!r}"
            f" in_onboarding={self.in_onboarding!r} type={self.type!r}>"
        )

    def _to_dict(self) -> PartialOnboardingPromptPayload:
        payload: PartialOnboardingPromptPayload = {
            "title": self.title,
            "options": [option._to_dict() for option in self.options],
            "single_select": self.single_select,
            "required": self.required,
            "in_onboarding": self.in_onboarding,
            "type": self.type.value,
        }

        if self.id:
            payload["id"] = self.id

        return payload

    @classmethod
    def _from_dict(cls, *, data: OnboardingPromptPayload, state: ConnectionState) -> Self:
        self = cls(
            title=data["title"],
            options=[
                OnboardingPromptOption._from_dict(data=option, state=state)
                for option in data["options"]
            ],
            single_select=data["single_select"],
            required=data["required"],
            in_onboarding=data["in_onboarding"],
            type=try_enum(OnboardingPromptType, data["type"]),
        )
        self.id = int(data["id"])
        return self
