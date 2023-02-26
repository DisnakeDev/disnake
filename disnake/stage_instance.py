# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .enums import StagePrivacyLevel, try_enum
from .mixins import Hashable
from .utils import MISSING, _get_as_snowflake, cached_slot_property, warn_deprecated

__all__ = ("StageInstance",)

if TYPE_CHECKING:
    from .channel import StageChannel
    from .guild import Guild
    from .guild_scheduled_event import GuildScheduledEvent
    from .state import ConnectionState
    from .types.channel import StageInstance as StageInstancePayload


class StageInstance(Hashable):
    """Represents a stage instance of a stage channel in a guild.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two stage instances are equal.

        .. describe:: x != y

            Checks if two stage instances are not equal.

        .. describe:: hash(x)

            Returns the stage instance's hash.

    Attributes
    ----------
    id: :class:`int`
        The stage instance's ID.
    guild: :class:`Guild`
        The guild that the stage instance is running in.
    channel_id: :class:`int`
        The ID of the channel that the stage instance is running in.
    topic: :class:`str`
        The topic of the stage instance.
    privacy_level: :class:`StagePrivacyLevel`
        The privacy level of the stage instance.
    guild_scheduled_event_id: Optional[:class:`int`]
        The ID of the stage instance's associated scheduled event, if applicable.
        See also :attr:`.guild_scheduled_event`.
    """

    __slots__ = (
        "_state",
        "id",
        "guild",
        "channel_id",
        "topic",
        "privacy_level",
        "_discoverable_disabled",
        "guild_scheduled_event_id",
        "_cs_channel",
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: StageInstancePayload) -> None:
        self._state = state
        self.guild = guild
        self._update(data)

    def _update(self, data: StageInstancePayload) -> None:
        self.id: int = int(data["id"])
        self.channel_id: int = int(data["channel_id"])
        self.topic: str = data["topic"]
        self.privacy_level: StagePrivacyLevel = try_enum(StagePrivacyLevel, data["privacy_level"])
        self._discoverable_disabled: bool = data.get("discoverable_disabled", False)
        self.guild_scheduled_event_id: Optional[int] = _get_as_snowflake(
            data, "guild_scheduled_event_id"
        )

    def __repr__(self) -> str:
        return f"<StageInstance id={self.id} guild={self.guild!r} channel_id={self.channel_id} topic={self.topic!r}>"

    @cached_slot_property("_cs_channel")
    def channel(self) -> Optional[StageChannel]:
        """Optional[:class:`StageChannel`]: The channel that stage instance is running in."""
        # the returned channel will always be a StageChannel or None
        return self._state.get_channel(self.channel_id)  # type: ignore

    @property
    def discoverable_disabled(self) -> bool:
        """:class:`bool`: Whether discoverability for the stage instance is disabled.

        .. deprecated:: 2.5

            Stages can no longer be discoverable.
        """
        warn_deprecated(
            "StageInstance.discoverable_disabled is deprecated and will be removed in a future version",
            stacklevel=2,
        )
        return self._discoverable_disabled

    def is_public(self) -> bool:
        """Whether the stage instance is public.

        .. deprecated:: 2.5

            Stages can no longer be public.

        :return type: :class:`bool`
        """
        warn_deprecated(
            "StageInstance.is_public is deprecated and will be removed in a future version",
            stacklevel=2,
        )
        return self.privacy_level is StagePrivacyLevel.public

    @property
    def guild_scheduled_event(self) -> Optional[GuildScheduledEvent]:
        """Optional[:class:`GuildScheduledEvent`]: The stage instance's scheduled event.

        This is only set if this stage instance has an associated scheduled event,
        and requires that event to be cached
        (which requires the :attr:`~Intents.guild_scheduled_events` intent).
        """
        if self.guild_scheduled_event_id is None:
            return None
        return self.guild.get_scheduled_event(self.guild_scheduled_event_id)

    async def edit(
        self,
        *,
        topic: str = MISSING,
        privacy_level: StagePrivacyLevel = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """|coro|

        Edits the stage instance.

        You must have the :attr:`~Permissions.manage_channels` permission to
        use this.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` instead of ``InvalidArgument``.

        Parameters
        ----------
        topic: :class:`str`
            The stage instance's new topic.
        privacy_level: :class:`StagePrivacyLevel`
            The stage instance's new privacy level.
        reason: Optional[:class:`str`]
            The reason the stage instance was edited. Shows up on the audit log.

        Raises
        ------
        TypeError
            If the ``privacy_level`` parameter is not the proper type.
        Forbidden
            You do not have permissions to edit the stage instance.
        HTTPException
            Editing a stage instance failed.
        """
        payload = {}

        if topic is not MISSING:
            payload["topic"] = topic

        if privacy_level is not MISSING:
            if not isinstance(privacy_level, StagePrivacyLevel):
                raise TypeError("privacy_level field must be of type PrivacyLevel")
            if privacy_level is StagePrivacyLevel.public:
                warn_deprecated(
                    "Setting privacy_level to public is deprecated and will be removed in a future version.",
                    stacklevel=2,
                )

            payload["privacy_level"] = privacy_level.value

        if payload:
            await self._state.http.edit_stage_instance(self.channel_id, **payload, reason=reason)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        """|coro|

        Deletes the stage instance.

        You must have the :attr:`~Permissions.manage_channels` permission to
        use this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason the stage instance was deleted. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to delete the stage instance.
        HTTPException
            Deleting the stage instance failed.
        """
        await self._state.http.delete_stage_instance(self.channel_id, reason=reason)
