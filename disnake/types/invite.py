# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, Optional, TypedDict

from typing_extensions import NotRequired

from disnake.types.appinfo import PartialAppInfo
from disnake.types.channel import InviteChannel
from disnake.types.guild import InviteGuild
from disnake.types.guild_scheduled_event import GuildScheduledEvent
from disnake.types.user import PartialUser

InviteTargetType = Literal[1, 2]


class VanityInvite(TypedDict):
    code: Optional[str]
    uses: NotRequired[int]


class _InviteMetadata(TypedDict, total=False):
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: str


class Invite(_InviteMetadata):
    code: str
    guild: NotRequired[InviteGuild]
    channel: InviteChannel
    inviter: NotRequired[PartialUser]
    target_type: NotRequired[InviteTargetType]
    target_user: NotRequired[PartialUser]
    target_application: NotRequired[PartialAppInfo]
    approximate_presence_count: NotRequired[int]
    approximate_member_count: NotRequired[int]
    expires_at: NotRequired[Optional[str]]
    guild_scheduled_event: NotRequired[GuildScheduledEvent]
