# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Union

from .emoji import Emoji, PartialEmoji, _EmojiTag
from .mixins import Hashable
from .object import Object
from .utils import _get_as_snowflake

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

# NOTE: From the information I got, onboarding will be read-only for bots.

# TODO: Audit log events
# TODO: Gateway events? (it currently doesn't have any)
# TODO: Guild methods
# TODO: Member flags
# TODO: Verify/Unverify member method
# TODO: Add documentation
# TODO: Check if any http methods need permissions
# Manage Guild and Manage Roles are required to edit onboarding.


class Onboarding:  # NOTE: or GuildOnboarding?
    """Represents a guild onboarding.

    .. versionadded:: 2.8

    TO BE DONE...

    Attributes
    ----------
    guild: :class:`Guild`
        The guild this onboarding belongs to.
    prompts: List[:class:`OnboardingPrompt`]
        The prompts the onboarding has.
    """

    __slots__ = (
        "guild",
        "prompts",
        "_guild_id",
        "_enable_default_channels",
        "_enable_onboarding_prompts",
        "_default_channel_ids",
        "_responses",
        "_state",
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: OnboardingPayload):
        self._state = state
        self.guild = guild
        self._from_data(data)

    def _from_data(self, data: OnboardingPayload):
        # Is this even required if there are no gateway events?

        # NOTE: I'm not sure if these are always available.
        self.prompts = [
            OnboardingPrompt._from_dict(data=prompt, state=self._state)
            for prompt in data["prompts"]
        ]
        self._guild_id = int(data["guild_id"])  # NOTE: is this required?
        self._enable_onboarding_prompts = data["enable_onboarding_prompts"]
        self._enable_default_channels = data["enable_default_channels"]
        self._default_channel_ids = list(map(int, data["default_channel_ids"]))
        self._responses = data["responses"]  # NOTE: client only?

    def __repr__(self) -> str:
        return (
            f"<Onboarding guild_id={self.guild.id!r} prompts={self.prompts!r}"
            f" enable_onboarding_prompts={self._enable_onboarding_prompts!r} enable_default_channels={self._enable_default_channels!r}"
            f" default_channel_ids={self._default_channel_ids!r}>"
        )

    @property
    def onboarding_prompts_enabled(self) -> bool:
        """:class:`bool`: Whether onboarding prompts are enabled."""
        # TODO: Add more info about this
        return self._enable_onboarding_prompts

    @property
    def default_channels_enabled(self) -> bool:
        """:class:`bool`: Whether default channels are enabled."""
        # TODO: Add more info about this
        return self._enable_default_channels

    @property
    def default_channels(self) -> List[GuildChannel]:
        """List[:class:`abc.GuildChannel`]: A list of channels that will display in Browse Channels."""
        return list(filter(None, map(self.guild._channels.get, self._default_channel_ids)))

    async def edit(
        self,
        prompts: List[OnboardingPrompt],
        onboarding_prompts_enabled: bool,
        default_channels_enabled: bool,
        default_channel_ids: List[int],
    ) -> Self:
        # See the first note of this file. I'll keep this here just in case it's supported by bots.
        """|coro|

        Edits the onboarding.

        Parameters
        ----------
        prompts: List[:class:`OnboardingPrompt`]
            The new onboarding prompts.
        onboarding_prompts_enabled: :class:`bool`
            Whether onboarding prompts are enabled.
        default_channels_enabled: :class:`bool`
            Whether default channels are enabled.
        default_channel_ids: List[:class:`int`]
            The new default channel IDs.

        Raises
        ------
        Forbidden
            You do not have permissions to edit the onboarding.
        HTTPException
            Editing the onboarding failed.

        Returns
        -------
        :class:`Onboarding`
            The newly edited onboarding.
        """
        data = await self._state.http.edit_guild_onboarding(
            self.guild.id,
            prompts=[prompt._to_dict() for prompt in prompts],
            enable_onboarding_prompts=onboarding_prompts_enabled,
            enable_default_channels=default_channels_enabled,
            default_channel_ids=default_channel_ids,
        )
        return Onboarding(state=self._state, guild=self.guild, data=data)


class OnboardingPromptOption(Hashable):
    """Represents an onboarding prompt option.

    .. versionadded:: 2.8

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
        emoji: Optional[Union[str, PartialEmoji, Emoji]],
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

        self.emoji: Optional[
            Union[str, PartialEmoji, Emoji]
        ] = None  # NOTE: not sure if this is nullable
        if emoji is None:
            self.emoji = None
        elif isinstance(emoji, str):
            self.emoji = PartialEmoji.from_str(emoji)
        elif isinstance(emoji, _EmojiTag):
            self.emoji = emoji
        else:
            raise TypeError("emoji must be None, a str, PartialEmoji, or Emoji instance")

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            f"<OnboardingPromptOption id={self.id!r} title={self.title!r} "
            f"description={self.description!r} emoji={self.emoji!r} "
            f"roles={self.roles!r} channels={self.channels!r}>"
        )

    def _to_dict(self) -> PartialOnboardingPromptOptionPayload:
        emoji_name, emoji_id = PartialEmoji._emoji_to_name_id(self.emoji)
        payload: PartialOnboardingPromptOptionPayload = {
            "title": self.title,
            "description": self.description,
            "emoji_name": emoji_name,
            "emoji_id": emoji_id,
            "role_ids": [role.id for role in self.roles],
            "channel_ids": [channel.id for channel in self.channels],
        }

        if self.id:
            payload["id"] = self.id

        return payload

    @classmethod
    def _from_dict(cls, *, data: OnboardingPromptOptionPayload, state: ConnectionState) -> Self:
        emoji_id = _get_as_snowflake(data, "emoji_id")
        emoji_name = data.get("emoji_name")
        emoji = PartialEmoji._emoji_from_name_id(emoji_name, emoji_id, state=state)

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

    # TODO: with_changes


class OnboardingPrompt(Hashable):
    """Represents an onboarding prompt.

    .. versionadded:: 2.8

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
    """

    __slots__ = ("id", "title", "options", "single_select", "required", "in_onboarding")

    def __init__(
        self,
        *,
        title: str,
        options: List[OnboardingPromptOption],
        single_select: bool,
        required: bool,
        in_onboarding: bool,
    ):
        self.id = 0
        self.title = title
        self.options = options
        self.single_select = single_select
        self.required = required
        self.in_onboarding = in_onboarding

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return (
            f"<OnboardingPrompt id={self.id!r} title={self.title!r} options={self.options!r}"
            f" single_select={self.single_select!r} required={self.required!r}"
            f" in_onboarding={self.in_onboarding!r}>"
        )

    def _to_dict(self) -> PartialOnboardingPromptPayload:
        payload: PartialOnboardingPromptPayload = {
            "title": self.title,
            "options": [option._to_dict() for option in self.options],
            "single_select": self.single_select,
            "required": self.required,
            "in_onboarding": self.in_onboarding,
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
        )
        self.id = int(data["id"])
        return self

    # TODO: with_changes
