# The MIT License (MIT)

# Copyright (c) 2021-present DisnakeDev

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from .enums import (
    GuildScheduledEventEntityType,
    GuildScheduledEventStatus,
    StagePrivacyLevel,
    try_enum,
)
from .user import User
from .mixins import Hashable
from .utils import cached_slot_property, parse_time, _get_as_snowflake

if TYPE_CHECKING:
    from .abc import GuildChannel
    from .guild import Guild
    from .state import ConnectionState


__all__ = ("GuildEventEntityMetadata", "GuildScheduledEvent")


class GuildEventEntityMetadata:
    """
    Represents guild event entity metadata.

    .. versionadded:: 2.3

    Attributes
    ----------
    speaker_ids: List[:class:`int`]
        The speakers of the stage channel.
    location: Optional[:class:`str`]
        Location of the event
    """

    __slots__ = ("speaker_ids", "location")

    def __init__(self, *, data: Dict[str, Any]):
        self.speaker_ids: List[int] = list(map(int, data.get("speaker_ids", [])))
        self.location: Optional[str] = data.get("location")


class GuildScheduledEvent(Hashable):
    """
    Represents guild scheduled events.

    .. versionadded:: 2.3

    .. container:: operations

        .. describe:: x == y

            Checks if two scheduled events are equal.

        .. describe:: x != y

            Checks if two scheduled events are not equal.

        .. describe:: hash(x)

            Returns the scheduled event's hash.

    Attributes
    ----------
    id: :class:`int`
        The id of the event.
    guild_id: :class:`int`
        The guild id of the event.
    channel_id: Optional[:class:`int`]
        The channel id of the event.
    creator_id: Optional[:class:`int`]
        The id of the user that created the event.
    name: :class:`str`
        The name of the event.
    description: :class:`str`
        The description of the event.
    image: Optional[:class:`str`]
        The image of the event.
    scheduled_start_time: :class:`datetime`
        The time the event will start.
    scheduled_end_time: Optional[:class:`datetime`]
        The time the event will end, or ``None`` if the event does not have a scheduled time to end.
    privacy_level: :class:`StagePrivacyLevel`
        Event privacy level.
    status: :class:`GuildScheduledEventStatus`
        The scheduled status of the event.
    entity_type: :class:`GuildScheduledEventEntityType`
        The scheduled entity type of the event.
    entity_id: Optional[:class:`int`]
        Entity id.
    entity_metadata: :class:`GuildEventEntityMetadata`
        Metadata for the event.
    sku_ids: List[:class:`int`]
        Sku ids.
    creator: Optional[:class:`User`]
        The creator of the event.
    skus: Optional[List[:class:`dict`]]
        A list of skus.
    user_count: Optional[:class:`int`]
        Users subscribed to the event.
    """

    __slots__ = (
        "_state",
        "id",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "image",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "status",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "sku_ids",
        "creator",
        "skus",
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
        self.image: Optional[str] = data["image"]
        self.scheduled_start_time: datetime = parse_time(  # type: ignore
            data["scheduled_start_time"]
        )
        self.scheduled_end_time: Optional[datetime] = parse_time(data["scheduled_end_time"])
        self.privacy_level: StagePrivacyLevel = try_enum(StagePrivacyLevel, data["privacy_level"])
        self.status: GuildScheduledEventStatus = try_enum(GuildScheduledEventStatus, data["status"])
        self.entity_type: GuildScheduledEventEntityType = try_enum(
            GuildScheduledEventEntityType, data["entity_type"]
        )
        self.entity_id: Optional[int] = _get_as_snowflake(data, "entity_id")

        entity_metadata = data["entity_metadata"]
        self.entity_metadata: Optional[GuildEventEntityMetadata] = (
            None if entity_metadata is None else GuildEventEntityMetadata(data=entity_metadata)
        )
        self.sku_ids: List[int] = list(map(int, data["sku_ids"]))

        creator_data = data.get("creator")
        self.creator: Optional[User] = (
            None if creator_data is None else User(state=self._state, data=creator_data)
        )
        self.skus: Optional[list] = data.get("skus")  # TODO: what is this
        self.user_count: Optional[int] = data.get("user_count")

    @cached_slot_property("_cs_guild")
    def guild(self) -> Optional[Guild]:
        """:class:`Guild` The guild of the event."""
        return self._state._get_guild(self.guild_id)

    @cached_slot_property("_cs_channel")
    def channel(self) -> Optional[GuildChannel]:  # TODO: better type hints?
        """:class:`GuildChannel` The channel of the event."""
        if self.channel_id is None:
            return None
        guild = self.guild
        return None if guild is None else guild.get_channel(self.channel_id)

    async def delete(self):
        """
        Delete this scheduled guild event.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the event.
        NotFound
            The event does not exist.
        HTTPException
            Deleting the event failed.
        """
        await self._state.http.delete_guild_scheduled_event(self.id)

    async def edit(
        self,
        *,
        channel_id: int = None,
        name: str = None,
        privacy_level: StagePrivacyLevel = None,
        scheduled_start_time: datetime = None,
        description: str = None,
        entity_type: GuildScheduledEventEntityType = None,
    ):
        """
        Edit this scheduled guild event.

        Parameters
        ----------
        channel_id: :class:`int`
            The channel id of the event.
        name: :class:`str`
            The name of the event.
        privacy_level: :class:`StagePrivacyLevel`
            The privacy level of the event.
        scheduled_start_time: :class:`datetime`
            The time to schedule the event.
        description: :class:`str`
            The description of the event.
        entity_type: :class:`GuildScheduledEventEntityType`
            The scheduled entity type of the event.

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

        privacy_level_value = None if privacy_level is None else privacy_level.value
        entity_type_value = None if entity_type is None else entity_type.value
        start_time_iso8601 = (
            None if scheduled_start_time is None else scheduled_start_time.isoformat()
        )

        return await self._state.http.edit_guild_scheduled_event(
            event_id=self.id,
            channel_id=channel_id,
            name=name,
            privacy_level=privacy_level_value,
            scheduled_start_time=start_time_iso8601,
            description=description,
            entity_type=entity_type_value,
        )
