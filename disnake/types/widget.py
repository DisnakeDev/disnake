# SPDX-License-Identifier: MIT

from typing import List, Optional, TypedDict

from .snowflake import Snowflake
from .user import User


class WidgetChannel(TypedDict):
    id: Snowflake
    name: str
    position: int


class WidgetActivity(TypedDict):
    name: str


class WidgetMember(User, total=False):
    # `activity` is used starting api v8, `game` is used in older versions.
    # Since widgets are sometimes used with the unversioned URL, we support both
    # as long as v6 is still the default.
    activity: WidgetActivity
    game: WidgetActivity
    status: str
    avatar_url: str
    deaf: bool
    self_deaf: bool
    mute: bool
    self_mute: bool
    suppress: bool


class Widget(TypedDict):
    id: Snowflake
    name: str
    instant_invite: Optional[str]
    channels: List[WidgetChannel]
    members: List[WidgetMember]
    presence_count: int


class WidgetSettings(TypedDict):
    enabled: bool
    channel_id: Optional[Snowflake]
