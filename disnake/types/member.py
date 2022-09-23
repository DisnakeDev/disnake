# SPDX-License-Identifier: MIT

from typing import Optional, TypedDict

from .snowflake import SnowflakeList
from .user import User


class _OptionalMember(TypedDict, total=False):
    avatar: Optional[str]
    nick: Optional[str]
    premium_since: str
    pending: bool
    permissions: str
    communication_disabled_until: Optional[str]


class BaseMember(_OptionalMember):
    roles: SnowflakeList
    joined_at: str
    deaf: bool
    mute: bool


class Member(BaseMember, total=False):
    user: User


class MemberWithUser(BaseMember):
    user: User


class UserWithMember(User, total=False):
    member: BaseMember
