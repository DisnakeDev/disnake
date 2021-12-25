"""
The MIT License (MIT)

Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .enums import (
    GuildScheduledEventEntityType,
    GuildScheduledEventPrivacyLevel,
    GuildScheduledEventStatus,
    try_enum,
)
from .member import Member
from .mixins import Hashable
from .user import User
from .utils import MISSING, _get_as_snowflake, cached_slot_property, parse_time

if TYPE_CHECKING:
    from .abc import GuildChannel
    from .guild import Guild
    from .state import ConnectionState


__all__ = ("GuildScheduledEventMetadata", "GuildScheduledEvent")


class GuildScheduledEventMetadata:
    """
    Represents guild scheduled event entity metadata.

    .. versionadded:: 2.3

    Attributes
    ----------
    location: Optional[:class:`str`]
        The location of the guild scheduled event. If :attr:`GuildScheduledEvent.entity_type` is
        :class:`GuildScheduledEventEntityType.external`, this value is not ``None``.
    """

    __slots__ = ("location",)

    def __init__(self, *, location: str = None):
        self.location: Optional[str] = location

    def __repr__(self) -> str:
        return f"<GuildScheduledEventMetadata location={self.location!r}>"

    def to_dict(self) -> Dict[str, Any]:
        return {"location": self.location}

    @classmethod
    def from_dict(cls, data):
        return GuildScheduledEventMetadata(location=data.get("location"))


class GuildScheduledEvent(Hashable):
    """
    Represents guild scheduled event.

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
        This field is ``None`` if :attr:`entity_type` is :class:`GuildScheduledEventEntityType.external`
    creator_id: Optional[:class:`int`]
        The ID of the user that created the guild scheduled event.
        This field is ``None`` for events created before October 25th, 2021.
    name: :class:`str`
        The name of the guild scheduled event (1-100 characters).
    description: :class:`str`
        The description of the guild scheduled event (1-1000 characters).
    scheduled_start_time: :class:`datetime.datetime`
        The time when the guild scheduled event will start
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
    creator: Optional[:class:`User`]
        The user that created the guild scheduled event.
        This field is ``None`` for events created before October 25th, 2021.
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
        "_cs_guild",
        "_cs_channel",
    )

    def __init__(self, *, state: ConnectionState, data: Dict[str, Any]):
        self._state: ConnectionState = state
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.channel_id: Optional[int] = _get_as_snowflake(data, "channel_id")
        self.creator_id: Optional[int] = _get_as_snowflake(data, "creator_id")
        self.name: str = data["name"]
        self.description: Optional[str] = data.get("description")
        self.scheduled_start_time: datetime = parse_time(  # type: ignore
            data["scheduled_start_time"]
        )
        self.scheduled_end_time: Optional[datetime] = parse_time(data["scheduled_end_time"])
        self.privacy_level: GuildScheduledEventPrivacyLevel = try_enum(
            GuildScheduledEventPrivacyLevel, data["privacy_level"]
        )
        self.status: GuildScheduledEventStatus = try_enum(GuildScheduledEventStatus, data["status"])
        self.entity_type: GuildScheduledEventEntityType = try_enum(
            GuildScheduledEventEntityType, data["entity_type"]
        )
        self.entity_id: Optional[int] = _get_as_snowflake(data, "entity_id")

        metadata = data["entity_metadata"]
        self.entity_metadata: Optional[GuildScheduledEventMetadata] = (
            None if metadata is None else GuildScheduledEventMetadata.from_dict(metadata)
        )

        creator_data = data.get("creator")
        self.creator: Optional[User]
        if creator_data is not None:
            self.creator = User(state=self._state, data=creator_data)
        elif self.creator_id is not None:
            self.creator = self._state.get_user(self.creator_id)
        else:
            self.creator = None

        self.user_count: Optional[int] = data.get("user_count")

    def __repr__(self) -> str:
        return (
            "<GuildScheduledEvent "
            + " ".join(
                f"{attr}={getattr(self, attr)!r}"
                for attr in self.__slots__
                if not attr.startswith("_")
            )
            + ">"
        )

    def __str__(self) -> str:
        return self.name

    @cached_slot_property("_cs_guild")
    def guild(self) -> Optional[Guild]:
        """The guild which the guild scheduled event belongs to.

        :return type: Optional[:class:`Guild`]
        """
        return self._state._get_guild(self.guild_id)

    @cached_slot_property("_cs_channel")
    def channel(self) -> Optional[GuildChannel]:
        """The channel in which the guild scheduled event will be hosted.

        :return type: Optional[:class:`abc.GuildChannel`]
        """
        if self.channel_id is None:
            return None
        guild = self.guild
        return None if guild is None else guild.get_channel(self.channel_id)

    async def delete(self):
        """|coro|

        Deletes the guild scheduled event.

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

    async def edit(
        self,
        *,
        name: str = MISSING,
        description: str = MISSING,
        channel_id: Optional[int] = MISSING,
        privacy_level: GuildScheduledEventPrivacyLevel = MISSING,
        scheduled_start_time: datetime = MISSING,
        scheduled_end_time: datetime = MISSING,
        entity_type: GuildScheduledEventEntityType = MISSING,
        entity_metadata: GuildScheduledEventMetadata = MISSING,
        status: GuildScheduledEventStatus = MISSING,
        reason: Optional[str] = None,
    ):
        """|coro|

        Edits the guild scheduled event.

        If updating ``entity_type`` to :class:`GuildScheduledEventEntityType.external`:

        - ``channel_id`` should be set to ``None`` or ignored
        - ``entity_metadata`` with a location field must be provided
        - ``scheduled_end_time`` must be provided

        Parameters
        ----------
        name: :class:`str`
            The name of the guild scheduled event.
        description: :class:`str`
            The description of the guild scheduled event.
        channel_id: Optional[:class:`int`]
            The channel ID in which the guild scheduled event will be hosted.
            Set to ``None`` if changing ``entity_type`` to :class:`GuildScheduledEventEntityType.external`.
        privacy_level: :class:`GuildScheduledEventPrivacyLevel`
            The privacy level of the guild scheduled event.
        scheduled_start_time: :class:`datetime.datetime`
            The time to schedule the guild scheduled event.
        scheduled_end_time: :class:`datetime.datetime`
            The time when the guild scheduled event is scheduled to end.
        entity_type: :class:`GuildScheduledEventEntityType`
            The entity type of the guild scheduled event.
        entity_metadata: :class:`GuildScheduledEventMetadata`
            The entity metadata of the guild scheduled event.
        status: :class:`GuildScheduledEventStatus`
            The status of the guild scheduled event.
        reason: Optional[:class:`str`]
            The reason for editing the guild scheduled event. Shows up on the audit log.

        Returns
        -------
        :class:`GuildScheduledEvent`
            The updated guild scheduled event instance.

        Raises
        ------
        Forbidden
            You do not have proper permissions to edit the event.
        NotFound
            The event does not exist.
        HTTPException
            Editing the event failed.
        """

        fields: Dict[str, Any] = {}
        is_external = entity_type is GuildScheduledEventEntityType.external
        error_for_external_entity = (
            "if entity_type is GuildScheduledEventEntityType.external, {} must be {}"
        )

        if privacy_level is not MISSING:
            if not isinstance(privacy_level, GuildScheduledEventPrivacyLevel):
                raise ValueError(
                    "privacy_level must be an instance of GuildScheduledEventPrivacyLevel"
                )

            fields["privacy_level"] = privacy_level.value

        if entity_type is not MISSING:
            if not isinstance(entity_type, GuildScheduledEventEntityType):
                raise ValueError("entity_type must be an instance of GuildScheduledEventEntityType")

            fields["entity_type"] = entity_type.value

        if not entity_metadata and is_external:
            raise ValueError(error_for_external_entity.format("entity_metadata", "provided"))

        if entity_metadata is not MISSING:
            if entity_metadata is None:
                fields["entity_metadata"] = None

            elif isinstance(entity_metadata, GuildScheduledEventMetadata):
                fields["entity_metadata"] = entity_metadata.to_dict()

            else:
                raise ValueError(
                    "entity_metadata must be an instance of GuildScheduledEventMetadata"
                )

        if status is not MISSING:
            if not isinstance(status, GuildScheduledEventStatus):
                raise ValueError("status must be an instance of GuildScheduledEventStatus")

            fields["status"] = status.value

        if name is not MISSING:
            fields["name"] = name

        if description is not MISSING:
            fields["description"] = description

        if channel_id is not MISSING:
            if channel_id is not None and is_external:
                raise ValueError(error_for_external_entity.format("channel_id", "None or MISSING"))
            fields["channel_id"] = channel_id
        elif channel_id is None and is_external:
            fields["channel_id"] = None

        if scheduled_start_time is not MISSING:
            fields["scheduled_start_time"] = scheduled_start_time.isoformat()

        if scheduled_end_time is not MISSING:
            fields["scheduled_end_time"] = scheduled_end_time.isoformat()
        elif is_external:
            raise ValueError(error_for_external_entity.format("scheduled_end_time", "provided"))

        data = await self._state.http.edit_guild_scheduled_event(
            guild_id=self.guild_id, event_id=self.id, reason=reason, **fields
        )
        return GuildScheduledEvent(state=self._state, data=data)

    async def fetch_users(
        self,
        *,
        limit: int = None,
        with_members: bool = True,
        before_id: int = None,
        after_id: int = None,
    ) -> List[Union[Member, User]]:
        """|coro|

        Retrieves a list of users subscribed to the guild scheduled event.

        Parameters
        ----------
        limit: :class:`int`
            The number of users to retrieve.
        with_members: :class:`bool`
            Whether to include some users as members. Defaults to ``True``.
        before_id: :class:`int`
            Consider only users before given user ID.
        after_id: :class:`int`
            Consider only users after given user ID.

        Returns
        -------
        List[Union[:class:`Member`, :class:`User`]]
            A list of users subscribed to the guild scheduled event.

        Raises
        ------
        Forbidden
            You do not have proper permissions to fetch the users.
        NotFound
            The event does not exist.
        HTTPException
            The request failed.
        """

        raw_users = await self._state.http.get_guild_scheduled_event_users(
            guild_id=self.guild_id,
            event_id=self.id,
            limit=limit,
            with_member=with_members,
            before=before_id,
            after=after_id,
        )
        users = []

        for data in raw_users:
            member_data = data.get("member")
            if member_data is not None and self.guild is not None:
                user = Member(data=member_data, guild=self.guild, state=self._state)
            else:
                user = User(data=data["user"], state=self._state)
            users.append(user)

        return users
