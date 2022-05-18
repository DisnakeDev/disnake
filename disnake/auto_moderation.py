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

from typing import TYPE_CHECKING, Any, List, Optional, Sequence

from .enums import (
    AutomodActionType,
    AutomodEventType,
    AutomodTriggerType,
    enum_if_int,
    try_enum,
    try_enum_to_int,
)
from .object import Object
from .utils import MISSING, _get_as_snowflake

if TYPE_CHECKING:
    from typing_extensions import Self

    from .abc import Snowflake
    from .guild import Guild, GuildChannel as GuildChannelType
    from .member import Member
    from .role import Role
    from .types.auto_moderation import (
        AutomodAction as AutomodActionPayload,
        AutomodActionMetadata,
        AutomodRule as AutomodRulePayload,
        EditAutomodRule as EditAutomodRulePayload,
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
    guild: :class:`Guild`
        The guild of the action, helpful for use with :func:`on_auto_moderation_action`.
    """

    __slots__ = ("type", "guild", "_metadata")

    def __init__(
        self, *, guild: Guild, type: AutomodActionType, channel: Optional[Snowflake] = None
    ):
        self.guild: Guild = guild
        self.type: AutomodActionType = enum_if_int(AutomodActionType, type)
        self._metadata: AutomodActionMetadata = {}

        if channel:
            self._metadata["channel_id"] = channel.id

    @property
    def channel_id(self) -> Optional[int]:
        """Optional[:class:`int`]: The target channel ID. See :attr:`~AutomodAction.channel` for more info."""
        return _get_as_snowflake(self._metadata, "channel_id")

    @property
    def channel(self) -> Optional[GuildChannelType]:
        """Optional[:class:`abc.GuildChannel`]: The channel to send an alert in when the rule is triggered,
        if :attr:`.type` is :attr:`AutomodActionType.send_alert`."""
        # TODO: return Object instead of None?
        return self.guild.get_channel(self.channel_id)  # type: ignore

    def __repr__(self) -> str:
        if self.type is AutomodActionType.log_to_channel:
            channel_repr = f" channel={self.channel!r}"
        else:
            channel_repr = ""
        return f"<AutomodAction type={self.type!r}{channel_repr}>"

    @classmethod
    def _from_dict(cls, data: AutomodActionPayload, guild: Guild) -> Self:
        meta = data.get("metadata", {})
        channel_id = _get_as_snowflake(meta, "channel_id")

        self = cls(
            guild=guild,
            type=try_enum(AutomodActionType, data["type"]),
            channel=Object(channel_id) if channel_id else None,
        )

        self._metadata = meta  # allow access to unimplemented fields

        return self

    def to_dict(self) -> AutomodActionPayload:
        return {
            "type": self.type.value,
            "metadata": self._metadata,
        }


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
            AutomodAction._from_dict(data=action, guild=guild)
            for action in data["actions"]
            if action
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
        # TODO: return Object instead of None?
        return list(filter(None, map(self.guild.get_role, self._exempt_role_ids)))

    @property
    def exempt_channels(self) -> List[GuildChannelType]:
        """List[:class:`abc.GuildChannel`]: The list of channels that are exempt from this rule."""
        return list(filter(None, map(self.guild.get_channel, self._exempt_channel_ids)))

    def __repr__(self) -> str:
        return (
            f"<AutomodRule id={self.id!r} name={self.name!r} enabled={self.enabled!r}"
            f" creator={self.creator!r} event_type={self.event_type!r} trigger_type={self.trigger_type!r}"
            f" actions={self.actions!r} exempt_roles={self._exempt_role_ids!r} exempt_channels={self._exempt_channel_ids!r}"
            f" trigger_metadata={self.trigger_metadata!r}>"
        )

    async def edit(
        self,
        *,
        name: str = MISSING,
        enabled: bool = MISSING,
        trigger_type: AutomodTriggerType = MISSING,
        actions: Sequence[AutomodAction] = MISSING,
        trigger_metadata: Any = MISSING,
        exempt_roles: Sequence[Snowflake] = MISSING,
        exempt_channels: Sequence[Snowflake] = MISSING,
        reason: Optional[str] = None,
    ) -> AutomodRule:
        """|coro|

        Edits the auto moderation rule.

        You must have :attr:`.Permissions.manage_guild` permission to do this.  # TODO

        All fields are optional.

        Parameters
        ----------
        name: :class:`str`
            The rule's new name.
        enabled: :class:`bool`
            Whether to enable the rule.
        trigger_type: :class:`AutomodTriggerType`
            The rule's new trigger type.
        actions: Sequence[:class:`AutomodAction`]
            The rule's new actions.
        trigger_metadata: Any
            unknown  # TODO
        exempt_roles: Sequence[:class:`abc.Snowflake`]
            The rule's new exempt roles.
        exempt_channels: Sequence[:class:`abc.Snowflake`]
            The rule's new exempt channels.
        reason: Optional[:class:`str`]
            The reason for editing the rule. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have proper permissions to edit the rule.
        NotFound
            The rule does not exist.
        HTTPException
            Editing the rule failed.

        Returns
        -------
        :class:`AutomodRule`
            The newly updated auto moderation rule.
        """

        payload: EditAutomodRulePayload = {}

        if name is not MISSING:
            payload["name"] = name
        if enabled is not MISSING:
            payload["enabled"] = enabled
        if trigger_type is not MISSING:
            payload["trigger_type"] = try_enum_to_int(trigger_type)
        if actions is not MISSING:
            payload["actions"] = [a.to_dict() for a in actions]
        if trigger_metadata is not MISSING:
            payload["trigger_metadata"] = trigger_metadata
        if exempt_roles is not MISSING:
            payload["exempt_roles"] = [e.id for e in exempt_roles]
        if exempt_channels is not MISSING:
            payload["exempt_channels"] = [e.id for e in exempt_channels]

        data = await self.guild._state.http.edit_auto_moderation_rule(
            self.guild.id, self.id, payload, reason=reason
        )
        return AutomodRule(data=data, guild=self.guild)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        """|coro|

        Deletes the auto moderation rule.

        You must have :attr:`.Permissions.manage_guild` permission to do this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this rule. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the rule.
        NotFound
            The rule does not exist.
        HTTPException
            Deleting the rule failed.
        """
        await self.guild._state.http.delete_auto_moderation_rule(
            self.guild.id, self.id, reason=reason
        )
