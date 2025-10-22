# SPDX-License-Identifier: MIT

from typing import TypedDict

from typing_extensions import NotRequired

from .snowflake import SnowflakeList
from .user import AvatarDecorationData, User


class BaseMember(TypedDict):
    nick: NotRequired[str | None]
    avatar: NotRequired[str | None]
    roles: SnowflakeList
    joined_at: str
    premium_since: NotRequired[str | None]
    deaf: bool
    mute: bool
    pending: NotRequired[bool]
    permissions: NotRequired[str]
    communication_disabled_until: NotRequired[str | None]
    flags: int
    avatar_decoration_data: NotRequired[AvatarDecorationData | None]


class Member(BaseMember, total=False):
    user: User


class MemberWithUser(BaseMember):
    user: User


class UserWithMember(User, total=False):
    member: BaseMember
