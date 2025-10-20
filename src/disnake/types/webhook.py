# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .channel import PartialChannel
from .snowflake import Snowflake
from .user import User


class SourceGuild(TypedDict):
    id: int
    name: str
    icon: str


WebhookType = Literal[1, 2, 3]


class FollowerWebhook(TypedDict):
    channel_id: Snowflake
    webhook_id: Snowflake
    source_channel: NotRequired[PartialChannel]
    source_guild: NotRequired[SourceGuild]


class PartialWebhook(TypedDict):
    id: Snowflake
    type: WebhookType
    guild_id: NotRequired[Optional[Snowflake]]
    user: NotRequired[User]
    token: NotRequired[str]


# note: `total=False` to support `Webhook.partial`
class Webhook(PartialWebhook, total=False):
    name: Optional[str]
    avatar: Optional[str]
    channel_id: Snowflake
    application_id: Optional[Snowflake]
