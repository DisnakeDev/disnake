# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, Optional, TypedDict

from .appinfo import PartialAppInfo
from .channel import InviteChannel
from .guild import InviteGuild
from .guild_scheduled_event import GuildScheduledEvent
from .user import PartialUser

InviteTargetType = Literal[1, 2]


class _InviteOptional(TypedDict, total=False):
    guild: InviteGuild
    inviter: PartialUser
    target_user: PartialUser
    target_type: InviteTargetType
    target_application: PartialAppInfo
    approximate_member_count: int
    approximate_presence_count: int
    guild_scheduled_event: GuildScheduledEvent


class _InviteMetadata(TypedDict, total=False):
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: str
    expires_at: Optional[str]


class VanityInvite(_InviteMetadata):
    code: Optional[str]


class IncompleteInvite(_InviteMetadata):
    code: str
    channel: InviteChannel


class Invite(IncompleteInvite, _InviteOptional):
    ...
