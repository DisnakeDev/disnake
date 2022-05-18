"""
The MIT License (MIT)

Copyright (c) 2022-present Disnake Development

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

from typing import TYPE_CHECKING, Any, List, Optional

from .enums import AutomodActionType, AutomodEventType, AutomodTriggerType, try_enum
from .utils import _get_as_snowflake, cached_slot_property

if TYPE_CHECKING:
    from .guild import Guild, GuildChannel as GuildChannelType
    from .member import Member
    from .role import Role
    from .types.auto_moderation import (
        AutomodAction as AutomodActionPayload,
        AutomodRule as AutomodRulePayload,
    )

__all__ = ("AutomodAction", "AutomodRule")


class AutomodAction:
    """
    Represents an auto moderation action.

    .. versionadded:: 2.6

    Attributes
    ----------
    type: :class:`AutomodActionType`
        The action type.
    channel_id: Optional[:class:`int`]
        The target channel ID, if :attr:`.type` is :attr:`AutomodActionType.send_alert`.
    """

    __slots__ = ("type", "channel_id", "_guild", "_metadata", "_cs_channel")

    # TODO: create a `@classmethod _from_data` instead?
    def __init__(self, *, data: AutomodActionPayload, guild: Guild):
        self._guild: Guild = guild
        self.type: AutomodActionType = try_enum(AutomodActionType, data["type"])

        self._metadata = data.get("metadata", {})  # allow access to unimplemented fields
        self.channel_id: Optional[int] = _get_as_snowflake(self._metadata, "channel_id")

    @cached_slot_property("_cs_channel")
    def channel(self) -> Optional[GuildChannelType]:
        """Optional[:class:`abc.GuildChannel`]: The channel to send an alert in when the automod rule is triggered,
        if :attr:`.type` is :attr:`AutomodActionType.send_alert`."""
        return self._guild.get_channel(self.channel_id)  # type: ignore

    def __repr__(self) -> str:
        return f"<AutomodAction type={self.type!r} channel={self.channel!r}>"


class AutomodRule:
    """
    Represents an auto moderation rule.

    .. versionadded:: 2.6

    Attributes
    ----------
    id: :class:`int`
        The rule ID.
    name: :class:`str`
        The rule name.
    enabled: :class:`bool`
        Whether this rule is enabled.
    guild: :class:`Guild`
        The guild of the rule.
    creator_id: :class:`int`
        The rule creator's ID. See also :attr:`.creator`.
    event_type: :class:`AutomodEventType`
        The event type this rule is applied to.
    trigger_type: :class:`AutomodTriggerType`
        The type of trigger that determines whether this rule's actions should run for a specific event.
    actions: List[:class:`AutomodAction`]
        The list of actions that will execute if a matching event triggered this rule.
    trigger_metadata: Any
        unknown  # TODO
    """

    __slots__ = (
        "id",
        "name",
        "enabled",
        "guild",
        "creator_id",
        "event_type",
        "trigger_type",
        "actions",
        "trigger_metadata",
        "_exempt_role_ids",
        "_exempt_channel_ids",
    )

    # TODO: create a `@classmethod _from_data` instead?
    def __init__(self, *, data: AutomodRulePayload, guild: Guild):
        # note: `data["guild_id"]` also exists, but we don't have any use for it
        self.guild: Guild = guild

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.enabled: bool = data["enabled"]
        self.creator_id: int = int(data["creator_id"])
        self.event_type: AutomodEventType = try_enum(AutomodEventType, data["event_type"])
        self.trigger_type: AutomodTriggerType = try_enum(AutomodTriggerType, data["trigger_type"])
        self.actions: List[AutomodAction] = [
            AutomodAction(data=action, guild=guild) for action in data["actions"] if action
        ]
        self.trigger_metadata: Any = data["trigger_metadata"]
        self._exempt_role_ids: List[int] = list(map(int, data["exempt_roles"]))
        self._exempt_channel_ids: List[int] = list(map(int, data["exempt_channels"]))

    @property
    def creator(self) -> Optional[Member]:
        """Optional[:class:`Member`]: The guild member that created this rule.
        May be ``None`` if the member cannot be found. See also :attr:`.creator_id`.
        """
        return self.guild.get_member(self.creator_id)

    @property
    def exempt_roles(self) -> List[Role]:
        """List[:class:`Role`]: The list of roles that are exempt from this rule."""
        return list(filter(None, map(self.guild.get_role, self._exempt_role_ids)))

    @property
    def exempt_channels(self) -> List[GuildChannelType]:
        """List[:class:`abc.GuildChannel`]: The list of roles that are exempt from this rule."""
        return list(filter(None, map(self.guild.get_channel, self._exempt_channel_ids)))

    def __repr__(self) -> str:
        return (
            f"<AutomodRule id={self.id!r} name={self.name!r} enabled={self.enabled!r}"
            f" creator={self.creator!r} event_type={self.event_type!r} trigger_type={self.trigger_type!r}"
            f" actions={self.actions!r} exempt_roles={self._exempt_role_ids!r} exempt_channels={self._exempt_channel_ids!r}"
            f" trigger_metadata={self.trigger_metadata!r}>"
        )
