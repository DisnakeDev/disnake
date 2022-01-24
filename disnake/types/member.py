"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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

from typing import Optional, TypedDict

from .snowflake import SnowflakeList
from .user import User


class Nickname(TypedDict):
    nick: str


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
