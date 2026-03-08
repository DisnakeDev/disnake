# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

from .appinfo import PartialAppInfo
from .channel import InviteChannel
from .guild import InviteGuild
from .guild_scheduled_event import GuildScheduledEvent
from .role import PartialRole
from .user import PartialUser

if TYPE_CHECKING:
    from datetime import datetime

InviteType = Literal[0, 1, 2]
InviteTargetType = Literal[1, 2]


class VanityInvite(TypedDict):
    code: str | None
    uses: NotRequired[int]


class _InviteMetadata(TypedDict, total=False):
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: str


class Invite(_InviteMetadata):
    code: str
    type: InviteType
    guild: NotRequired[InviteGuild]
    channel: InviteChannel | None
    inviter: NotRequired[PartialUser]
    target_type: NotRequired[InviteTargetType]
    target_user: NotRequired[PartialUser]
    target_application: NotRequired[PartialAppInfo]
    approximate_presence_count: NotRequired[int]
    approximate_member_count: NotRequired[int]
    expires_at: str | None
    guild_scheduled_event: NotRequired[GuildScheduledEvent]
    flags: NotRequired[int]
    roles: NotRequired[list[PartialRole]]


class TargetUsersJobBase(TypedDict):
    status: Literal[0, 1, 2, 3]
    total_users: int
    processed_users: int
    error_message: str | None


class TargetUsersJobPayload(TargetUsersJobBase):
    created_at: str
    completed_at: str | None


class TargetUserJob(TargetUsersJobBase):
    created_at: datetime
    completed_at: datetime | None
