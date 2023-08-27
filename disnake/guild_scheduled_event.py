# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, overload

from .asset import Asset
from .enums import (
    ChannelType,
    GuildScheduledEventEntityType,
    GuildScheduledEventPrivacyLevel,
    GuildScheduledEventStatus,
    try_enum,
)
from .mixins import Hashable
from .utils import (
    MISSING,
    _assetbytes_to_base64_data,
    _get_as_snowflake,
    cached_slot_property,
    isoformat_utc,
    parse_time,
    snowflake_time,
)

if TYPE_CHECKING:
    from .abc import GuildChannel, Snowflake
    from .asset import AssetBytes
    from .guild import Guild
    from .iterators import GuildScheduledEventUserIterator
    from .state import ConnectionState
    from .types.guild_scheduled_event import (
        GuildScheduledEvent as GuildScheduledEventPayload,
        GuildScheduledEventEntityMetadata as GuildScheduledEventEntityMetadataPayload,
    )
    from .user import User


__all__ = ("GuildScheduledEventMetadata", "GuildScheduledEvent")


class GuildScheduledEventMetadata:
    """Represents a guild scheduled event entity metadata.

    .. versionadded:: 2.3

    Attributes
    ----------
    location: Optional[:class:`str`]
        The location of the guild scheduled event. If :attr:`GuildScheduledEvent.entity_type` is
        :class:`GuildScheduledEventEntityType.external`, this value is not ``None``.
    """

    __slots__ = ("location",)

    def __init__(self, *, location: Optional[str] = None) -> None:
        self.location: Optional[str] = location

    def __repr__(self) -> str:
        return f"<GuildScheduledEventMetadata location={self.location!r}>"

    def to_dict(self) -> GuildScheduledEventEntityMetadataPayload:
        if self.location is not None:
            return {"location": self.location}
        return {}

    @classmethod
    def from_dict(
        cls, data: GuildScheduledEventEntityMetadataPayload
    ) -> GuildScheduledEventMetadata:
        return GuildScheduledEventMetadata(location=data.get("location"))


class GuildScheduledEvent(Hashable):
    """Represents a guild scheduled event.

    .. versionadded:: 2.3

    .. container:: operations

        .. describe:: x == y

            Checks if two guild scheduled events are equal.

        .. describe:: x != y

            Checks if two guild scheduled events are not equal.

        .. describe:: hash(x)

            Returns the guild scheduled event's hash.

    Attributes
    ----------
    id: :class:`int`
        The ID of the guild scheduled event.
    guild_id: :class:`int`
        The guild ID which the guild scheduled event belongs to.
    channel_id: Optional[:class:`int`]
        The channel ID in which the guild scheduled event will be hosted.
        This field is ``None`` if :attr:`entity_type` is :class:`GuildScheduledEventEntityType.external`.
    creator_id: Optional[:class:`int`]
        The ID of the user that created the guild scheduled event.
        This field is ``None`` for events created before October 25th, 2021.
    creator: Optional[:class:`User`]
        The user that created the guild scheduled event.
        This field is ``None`` for events created before October 25th, 2021.
    name: :class:`str`
        The name of the guild scheduled event (1-100 characters).
    description: :class:`str`
        The description of the guild scheduled event (1-1000 characters).
    scheduled_start_time: :class:`datetime.datetime`
        The time when the guild scheduled event will start.
    scheduled_end_time: Optional[:class:`datetime.datetime`]
        The time when the guild scheduled event will end, or ``None`` if the event does not have a scheduled time to end.
    privacy_level: :class:`GuildScheduledEventPrivacyLevel`
        The privacy level of the guild scheduled event.
    status: :class:`GuildScheduledEventStatus`
        The status of the guild scheduled event.
    entity_type: :class:`GuildScheduledEventEntityType`
        The type of the guild scheduled event.
    entity_id: Optional[:class:`int`]
        The ID of an entity associated with the guild scheduled event.
    entity_metadata: :class:`GuildScheduledEventMetadata`
        Additional metadata for the guild scheduled event.
    user_count: Optional[:class:`int`]
        The number of users subscribed to the guild scheduled event.
        If the guild scheduled event was fetched with ``with_user_count`` set to ``False``, this field is ``None``.
    """

    __slots__ = (
        "_state",
        "id",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "status",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "creator",
        "user_count",
        "_image",
        "_cs_guild",
        "_cs_channel",
    )

    def __init__(self, *, state: ConnectionState, data: GuildScheduledEventPayload) -> None:
        self._state: ConnectionState = state
        self._update(data)

    def _update(self, data: GuildScheduledEventPayload) -> None:
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.channel_id: Optional[int] = _get_as_snowflake(data, "channel_id")
        self.creator_id: Optional[int] = _get_as_snowflake(data, "creator_id")
        self.name: str = data["name"]
        self.description: Optional[str] = data.get("description")
        self.scheduled_start_time: datetime = parse_time(data["scheduled_start_time"])
        self.scheduled_end_time: Optional[datetime] = parse_time(data["scheduled_end_time"])
        self.privacy_level: GuildScheduledEventPrivacyLevel = try_enum(
            GuildScheduledEventPrivacyLevel, data["privacy_level"]
        )
        self.status: GuildScheduledEventStatus = try_enum(GuildScheduledEventStatus, data["status"])
        self.entity_type: GuildScheduledEventEntityType = try_enum(
            GuildScheduledEventEntityType, data["entity_type"]
        )
        self.entity_id: Optional[int] = _get_as_snowflake(data, "entity_id")

        metadata = data.get("entity_metadata")
        self.entity_metadata: Optional[GuildScheduledEventMetadata] = (
            None if metadata is None else GuildScheduledEventMetadata.from_dict(metadata)
        )

        creator_data = data.get("creator")
        self.creator: Optional[User]
        if creator_data is not None:
            self.creator = self._state.create_user(creator_data)
        else:
            self.creator = self._state.get_user(self.creator_id)

        self.user_count: Optional[int] = data.get("user_count")
        self._image: Optional[str] = data.get("image")

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("guild_id", self.guild_id),
            ("channel_id", self.channel_id),
            ("name", self.name),
            ("description", self.description),
            ("scheduled_start_time", self.scheduled_start_time),
            ("scheduled_end_time", self.scheduled_end_time),
            ("privacy_level", self.privacy_level),
            ("status", self.status),
            ("entity_type", self.entity_type),
            ("entity_metadata", self.entity_metadata),
            ("creator", self.creator),
        )
        inner = " ".join(f"{k!s}={v!r}" for k, v in attrs)
        return f"<{self.__class__.__name__} {inner}>"

    def __str__(self) -> str:
        return self.name

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: Returns the guild scheduled event's creation time in UTC.

        .. versionadded:: 2.6
        """
        return snowflake_time(self.id)

    @property
    def url(self) -> str:
        """:class:`str`: The guild scheduled event's URL.

        .. versionadded:: 2.6
        """
        return f"https://discord.com/events/{self.guild_id}/{self.id}"

    @cached_slot_property("_cs_guild")
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild which the guild scheduled event belongs to."""
        return self._state._get_guild(self.guild_id)

    @cached_slot_property("_cs_channel")
    def channel(self) -> Optional[GuildChannel]:
        """Optional[:class:`abc.GuildChannel`]: The channel in which the guild scheduled event will be hosted.

        This will be ``None`` if :attr:`entity_type` is :class:`GuildScheduledEventEntityType.external`.
        """
        if self.channel_id is None:
            return None
        guild = self.guild
        return None if guild is None else guild.get_channel(self.channel_id)

    @property
    def image(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: The cover image asset of the guild scheduled event, if available."""
        if self._image is None:
            return None
        return Asset._from_guild_scheduled_event_image(self._state, self.id, self._image)

    async def delete(self) -> None:
        """|coro|

        Deletes the guild scheduled event.

        You must have :attr:`.Permissions.manage_events` permission to do this.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the event.
        NotFound
            The event does not exist.
        HTTPException
            Deleting the event failed.
        """
        await self._state.http.delete_guild_scheduled_event(self.guild_id, self.id)

    # note: unlike `Guild.create_scheduled_event`, we don't remove `entity_type`-specific defaults
    # from parameters in the overloads here, as the entity_type might be the same as before,
    # in which case those parameters don't have to be passed

    # no entity_type specified
    @overload
    async def edit(
        self,
        *,
        name: str = ...,
        description: Optional[str] = ...,
        image: Optional[AssetBytes] = ...,
        channel: Optional[Snowflake] = ...,
        privacy_level: GuildScheduledEventPrivacyLevel = ...,
        scheduled_start_time: datetime = ...,
        scheduled_end_time: Optional[datetime] = ...,
        entity_metadata: Optional[GuildScheduledEventMetadata] = ...,
        status: GuildScheduledEventStatus = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        ...

    # new entity_type is `external`, no channel
    @overload
    async def edit(
        self,
        *,
        entity_type: Literal[GuildScheduledEventEntityType.external],
        channel: None = ...,
        name: str = ...,
        description: Optional[str] = ...,
        image: Optional[AssetBytes] = ...,
        privacy_level: GuildScheduledEventPrivacyLevel = ...,
        scheduled_start_time: datetime = ...,
        scheduled_end_time: datetime = ...,
        entity_metadata: GuildScheduledEventMetadata = ...,
        status: GuildScheduledEventStatus = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        ...

    # new entity_type is `voice` or `stage_instance`, no entity_metadata
    @overload
    async def edit(
        self,
        *,
        entity_type: Literal[
            GuildScheduledEventEntityType.voice,
            GuildScheduledEventEntityType.stage_instance,
        ],
        name: str = ...,
        description: Optional[str] = ...,
        image: Optional[AssetBytes] = ...,
        channel: Snowflake = ...,
        privacy_level: GuildScheduledEventPrivacyLevel = ...,
        scheduled_start_time: datetime = ...,
        scheduled_end_time: Optional[datetime] = ...,
        status: GuildScheduledEventStatus = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        ...

    # channel=None, no entity_type
    @overload
    async def edit(
        self,
        *,
        channel: None,
        name: str = ...,
        description: Optional[str] = ...,
        image: Optional[AssetBytes] = ...,
        privacy_level: GuildScheduledEventPrivacyLevel = ...,
        scheduled_start_time: datetime = ...,
        scheduled_end_time: datetime = ...,
        entity_metadata: GuildScheduledEventMetadata = ...,
        status: GuildScheduledEventStatus = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        ...

    # valid channel, no entity_type
    @overload
    async def edit(
        self,
        *,
        channel: Snowflake,
        name: str = ...,
        description: Optional[str] = ...,
        image: Optional[AssetBytes] = ...,
        privacy_level: GuildScheduledEventPrivacyLevel = ...,
        scheduled_start_time: datetime = ...,
        scheduled_end_time: Optional[datetime] = ...,
        status: GuildScheduledEventStatus = ...,
        reason: Optional[str] = ...,
    ) -> GuildScheduledEvent:
        ...

    async def edit(
        self,
        *,
        name: str = MISSING,
        description: Optional[str] = MISSING,
        image: Optional[AssetBytes] = MISSING,
        channel: Optional[Snowflake] = MISSING,
        privacy_level: GuildScheduledEventPrivacyLevel = MISSING,
        scheduled_start_time: datetime = MISSING,
        scheduled_end_time: Optional[datetime] = MISSING,
        entity_type: GuildScheduledEventEntityType = MISSING,
        entity_metadata: Optional[GuildScheduledEventMetadata] = MISSING,
        status: GuildScheduledEventStatus = MISSING,
        reason: Optional[str] = None,
    ) -> GuildScheduledEvent:
        """|coro|

        Edits the guild scheduled event.

        You must have :attr:`.Permissions.manage_events` permission to do this.

        .. versionchanged:: 2.6
            Updates must follow requirements of :func:`Guild.create_scheduled_event`

        .. versionchanged:: 2.6
            Now raises :exc:`TypeError` instead of :exc:`ValueError` for
            invalid parameter types.

        .. versionchanged:: 2.6
            Removed ``channel_id`` parameter in favor of ``channel``.

        .. versionchanged:: 2.6
            Naive datetime parameters are now assumed to be in the local
            timezone instead of UTC.

        Parameters
        ----------
        name: :class:`str`
            The name of the guild scheduled event.
        description: Optional[:class:`str`]
            The description of the guild scheduled event.
        image: Optional[|resource_type|]
            The cover image of the guild scheduled event. Set to ``None`` to remove the image.

            .. versionadded:: 2.4

            .. versionchanged:: 2.5
                Now accepts various resource types in addition to :class:`bytes`.

        channel: Optional[:class:`.abc.Snowflake`]
            The channel in which the guild scheduled event will be hosted.
            Set to ``None`` if changing ``entity_type`` to :class:`GuildScheduledEventEntityType.external`.

            .. versionadded:: 2.6

        privacy_level: :class:`GuildScheduledEventPrivacyLevel`
            The privacy level of the guild scheduled event.
        scheduled_start_time: :class:`datetime.datetime`
            The time to schedule the guild scheduled event.
            If the datetime is naive, it is assumed to be local time.
        scheduled_end_time: Optional[:class:`datetime.datetime`]
            The time when the guild scheduled event is scheduled to end.
            If the datetime is naive, it is assumed to be local time.
        entity_type: :class:`GuildScheduledEventEntityType`
            The entity type of the guild scheduled event.
        entity_metadata: Optional[:class:`GuildScheduledEventMetadata`]
            The entity metadata of the guild scheduled event.
        status: :class:`GuildScheduledEventStatus`
            The status of the guild scheduled event.

            See also :func:`start`, :func:`end`, and :func:`cancel`.
        reason: Optional[:class:`str`]
            The reason for editing the guild scheduled event. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have proper permissions to edit the event.
        NotFound
            The event does not exist or the ``image`` asset couldn't be found.
        HTTPException
            Editing the event failed.
        TypeError
            The ``image`` asset is a lottie sticker (see :func:`Sticker.read`),
            one of ``entity_type``, ``privacy_level``, ``entity_metadata`` or ``status``
            is not of the correct type, or the provided channel's type is neither :class:`ChannelType.voice` nor
            :class:`ChannelType.stage_voice`.

        Returns
        -------
        :class:`GuildScheduledEvent`
            The newly updated guild scheduled event instance.
        """
        fields: Dict[str, Any] = {}

        if entity_type is MISSING:
            if channel is None:
                entity_type = GuildScheduledEventEntityType.external
            elif channel is not MISSING and isinstance(
                channel_type := getattr(channel, "type", None), ChannelType
            ):
                if channel_type is ChannelType.voice:
                    entity_type = GuildScheduledEventEntityType.voice
                elif channel_type is ChannelType.stage_voice:
                    entity_type = GuildScheduledEventEntityType.stage_instance
                else:
                    raise TypeError("channel type must be either 'voice' or 'stage_voice'")

        if privacy_level is not MISSING:
            if not isinstance(privacy_level, GuildScheduledEventPrivacyLevel):
                raise TypeError(
                    "privacy_level must be an instance of GuildScheduledEventPrivacyLevel"
                )

            fields["privacy_level"] = privacy_level.value

        if entity_type is not MISSING:
            if not isinstance(entity_type, GuildScheduledEventEntityType):
                raise TypeError("entity_type must be an instance of GuildScheduledEventEntityType")

            fields["entity_type"] = entity_type.value

        if entity_metadata is not MISSING:
            if entity_metadata is None:
                fields["entity_metadata"] = None

            elif isinstance(entity_metadata, GuildScheduledEventMetadata):
                fields["entity_metadata"] = entity_metadata.to_dict()

            else:
                raise TypeError(
                    "entity_metadata must be an instance of GuildScheduledEventMetadata"
                )

        if status is not MISSING:
            if not isinstance(status, GuildScheduledEventStatus):
                raise TypeError("status must be an instance of GuildScheduledEventStatus")

            fields["status"] = status.value

        if name is not MISSING:
            fields["name"] = name

        if description is not MISSING:
            fields["description"] = description

        if image is not MISSING:
            fields["image"] = await _assetbytes_to_base64_data(image)

        if channel is not MISSING:
            fields["channel_id"] = channel.id if channel is not None else None
        elif entity_type is GuildScheduledEventEntityType.external:
            # special case, as the API wants `channel_id=null` if type is being changed to `external`
            fields["channel_id"] = None

        if scheduled_start_time is not MISSING:
            fields["scheduled_start_time"] = isoformat_utc(scheduled_start_time)

        if scheduled_end_time is not MISSING:
            fields["scheduled_end_time"] = isoformat_utc(scheduled_end_time)

        data = await self._state.http.edit_guild_scheduled_event(
            guild_id=self.guild_id, event_id=self.id, reason=reason, **fields
        )
        return GuildScheduledEvent(state=self._state, data=data)

    async def start(self, *, reason: Optional[str] = None) -> GuildScheduledEvent:
        """|coro|

        Starts the guild scheduled event.

        Changes the event status to :attr:`~GuildScheduledEventStatus.active`.

        You must have :attr:`.Permissions.manage_events` permission to do this.

        .. versionadded:: 2.7

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for starting the guild scheduled event. Shows up on the audit log.

        Raises
        ------
        ValueError
            The event has already started or ended, or was cancelled.
        Forbidden
            You do not have permissions to start the event.
        HTTPException
            Starting the event failed.

        Returns
        -------
        :class:`GuildScheduledEvent`
            The started guild scheduled event instance.
        """
        if self.status is not GuildScheduledEventStatus.scheduled:
            raise ValueError("This event is not scheduled")
        return await self._edit_status(GuildScheduledEventStatus.active, reason=reason)

    async def end(self, *, reason: Optional[str] = None) -> GuildScheduledEvent:
        """|coro|

        Ends the guild scheduled event.

        Changes the event status to :attr:`~GuildScheduledEventStatus.completed`.

        You must have :attr:`.Permissions.manage_events` permission to do this.

        .. versionadded:: 2.7

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for ending the guild scheduled event. Shows up on the audit log.

        Raises
        ------
        ValueError
            The event has not started yet, has already ended, or was cancelled.
        Forbidden
            You do not have permissions to end the event.
        HTTPException
            Ending the event failed.

        Returns
        -------
        :class:`GuildScheduledEvent`
            The ended guild scheduled event instance.
        """
        if self.status is not GuildScheduledEventStatus.active:
            raise ValueError("This event is not active")
        return await self._edit_status(GuildScheduledEventStatus.completed, reason=reason)

    async def cancel(self, *, reason: Optional[str] = None) -> GuildScheduledEvent:
        """|coro|

        Cancels the guild scheduled event.

        Changes the event status to :attr:`~GuildScheduledEventStatus.cancelled`.

        You must have :attr:`.Permissions.manage_events` permission to do this.

        .. versionadded:: 2.7

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for cancelling the guild scheduled event. Shows up on the audit log.

        Raises
        ------
        ValueError
            The event has already started or ended, or was already cancelled.
        Forbidden
            You do not have permissions to cancel the event.
        HTTPException
            Cancelling the event failed.

        Returns
        -------
        :class:`GuildScheduledEvent`
            The cancelled guild scheduled event instance.
        """
        if self.status is not GuildScheduledEventStatus.scheduled:
            raise ValueError("This event is not scheduled")
        return await self._edit_status(GuildScheduledEventStatus.cancelled, reason=reason)

    # shortcut for editing just the event status, bypasses other edit logic
    async def _edit_status(
        self, status: GuildScheduledEventStatus, *, reason: Optional[str]
    ) -> GuildScheduledEvent:
        data = await self._state.http.edit_guild_scheduled_event(
            guild_id=self.guild_id,
            event_id=self.id,
            reason=reason,
            status=status.value,
        )
        return GuildScheduledEvent(state=self._state, data=data)

    def fetch_users(
        self,
        *,
        limit: Optional[int] = None,
        with_members: bool = True,
        before: Optional[Snowflake] = None,
        after: Optional[Snowflake] = None,
    ) -> GuildScheduledEventUserIterator:
        """|coro|

        Returns an :class:`AsyncIterator` of users subscribed to the guild scheduled event.

        If ``before`` is specified, users are returned in reverse order,
        i.e. starting with the highest ID.

        .. versionchanged:: 2.5
            Now returns an :class:`AsyncIterator` instead of a list of the first 100 users.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of users to retrieve.
        with_members: :class:`bool`
            Whether to include some users as members. Defaults to ``True``.
        before: Optional[:class:`abc.Snowflake`]
            Retrieve users before this object.
        after: Optional[:class:`abc.Snowflake`]
            Retrieve users after this object.

        Raises
        ------
        Forbidden
            You do not have proper permissions to fetch the users.
        NotFound
            The event does not exist.
        HTTPException
            Retrieving the users failed.

        Yields
        ------
        Union[:class:`User`, :class:`Member`]
            The member (if retrievable) or user subscribed to the guild scheduled event.

        Examples
        --------
        Usage ::

            async for user in event.fetch_users(limit=500):
                print(user.name)

        Flattening into a list ::

            users = await event.fetch_users(limit=250).flatten()
        """
        from .iterators import GuildScheduledEventUserIterator  # cyclic import

        return GuildScheduledEventUserIterator(
            self,
            limit=limit,
            with_members=with_members,
            before=before,
            after=after,
        )
