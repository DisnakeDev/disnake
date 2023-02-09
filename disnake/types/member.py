# SPDX-License-Identifier: MIT

from typing import Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import SnowflakeList
from .user import User


class BaseMember(TypedDict):
    nick: NotRequired[Optional[str]]
    avatar: NotRequired[Optional[str]]
    roles: SnowflakeList
    joined_at: str
    premium_since: NotRequired[Optional[str]]
    deaf: bool
    mute: bool
    pending: NotRequired[bool]
    permissions: NotRequired[str]
    communication_disabled_until: NotRequired[Optional[str]]
    flags: int


class Member(BaseMember, total=False):
    user: User


class MemberWithUser(BaseMember):
    user: User


class UserWithMember(User, total=False):
    member: BaseMember
