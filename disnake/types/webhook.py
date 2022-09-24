# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, Optional, TypedDict

from .channel import PartialChannel
from .snowflake import Snowflake
from .user import User


class SourceGuild(TypedDict):
    id: int
    name: str
    icon: str


class _WebhookOptional(TypedDict, total=False):
    guild_id: Snowflake
    user: User
    token: str


WebhookType = Literal[1, 2, 3]


class _FollowerWebhookOptional(TypedDict, total=False):
    source_channel: PartialChannel
    source_guild: SourceGuild


class FollowerWebhook(_FollowerWebhookOptional):
    channel_id: Snowflake
    webhook_id: Snowflake


class PartialWebhook(_WebhookOptional):
    id: Snowflake
    type: WebhookType


# note: `total=False` to support `Webhook.partial`
class _FullWebhook(TypedDict, total=False):
    name: Optional[str]
    avatar: Optional[str]
    channel_id: Snowflake
    application_id: Optional[Snowflake]


class Webhook(PartialWebhook, _FullWebhook):
    ...
