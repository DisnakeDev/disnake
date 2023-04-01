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
    from .role import Role
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
        The IDs of the channels that will automatically be shown to new members.
    """

    __slots__ = (
        "guild",
        "prompts",
        "enabled",
        "default_channel_ids",
    )

    def __init__(self, *, guild: Guild, data: OnboardingPayload):
        self.guild = guild
        self._from_data(data)

    def _from_data(self, data: OnboardingPayload):
        self.prompts = [
            OnboardingPrompt._from_dict(data=prompt, guild=self.guild) for prompt in data["prompts"]
        ]
        self.enabled = data["enabled"]
        self.default_channel_ids = (
            frozenset(map(int, exempt_channels))
            if (exempt_channels := data["default_channel_ids"])
            else frozenset()
        )

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
        The onboarding prompt's ID.
    type: :class:`OnboardingPromptType`
        The onboarding prompt's type.
    options: List[:class:`OnboardingPromptOption`]
        The onboarding prompt's options.
    title: :class:`str`
        The onboarding prompt's title.
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
        self.id = int(data["id"])
        return self


class OnboardingPromptOption(Hashable):
    """Represents an onboarding prompt option.

    .. versionadded:: 2.9

    Attributes
    ----------
    id: :class:`int`
        The prompt option's ID.
    emoji: Optional[Union[:class:`PartialEmoji`, :class:`Emoji`]]
        The prompt option's emoji.
    title: :class:`str`
        The prompt option's title.
    description: :class:`str`
        The prompt option's description.
    roles_ids: FrozenSet[:class:`int`]
        The IDs of the roles that will be added to the user when they select this option.
    channels_ids: FrozenSet[:class:`int`]
        The IDs of the channels that will be shown to the user when they select this option.
    """

    __slots__ = ("id", "title", "description", "emoji", "guild", "roles_ids", "channels_ids")

    def __init__(
        self,
        *,
        title: str,
        description: str,
        emoji: Optional[Union[str, PartialEmoji, Emoji]],
        roles: Sequence[Snowflake],
        channels: Sequence[Snowflake],
        guild: Guild,
    ):
        # NOTE: The ID may sometimes be a UNIX timestamp since
        # Onboarding changes are saved locally until you send the API request (that's how it works in client)
        # so the API needs the timestamp to know what ID it needs to create, should we just add a note about it
        # or "try" to create the ID ourselves?
        # I'm not sure if this also happens for OnboardingPrompt
        self.id = 0
        self.title = title
        self.description = description
        self.guild = guild
        self.roles_ids = (
            frozenset(map(int, roles_ids))
            if (roles_ids := [role.id for role in roles])
            else frozenset()
        )
        self.channels_ids = (
            frozenset(map(int, channels_ids))
            if (channels_ids := [channel.id for channel in channels])
            else frozenset()
        )

        self.emoji: Optional[Union[PartialEmoji, Emoji]] = None
        if emoji is None:
            self.emoji = None
        elif isinstance(emoji, str):
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
            description=data.get("description") or "",
            emoji=emoji,
            roles=[Object(id=role_id) for role_id in data["role_ids"]],
            channels=[Object(id=channel_id) for channel_id in data["channel_ids"]],
            guild=guild,
        )
        self.id = int(data["id"])
        return self

    @property
    def roles(self) -> List[Role]:
        """List[:class:`Role`]: A list of roles that will be added to the user when they select this option."""
        return list(filter(None, map(self.guild.get_role, self.roles_ids)))

    @property
    def channels(self) -> List[GuildChannel]:
        """List[:class:`abc.GuildChannel`]: A list of channels that the user will see when they select this option."""
        return list(filter(None, map(self.guild.get_channel, self.channels_ids)))
