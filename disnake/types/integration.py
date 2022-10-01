# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict, Union

from .snowflake import Snowflake
from .user import User


class _IntegrationApplicationOptional(TypedDict, total=False):
    bot: User


class IntegrationApplication(_IntegrationApplicationOptional):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    summary: str


class IntegrationAccount(TypedDict):
    id: str
    name: str


IntegrationExpireBehavior = Literal[0, 1]


class _PartialIntegrationOptional(TypedDict, total=False):
    application_id: Snowflake  # undocumented, only shown in example - used for audit logs


class PartialIntegration(_PartialIntegrationOptional):
    id: Snowflake
    name: str
    type: IntegrationType
    account: IntegrationAccount


IntegrationType = Literal["twitch", "youtube", "discord"]


class BaseIntegration(PartialIntegration):
    enabled: bool
    syncing: bool
    synced_at: str
    user: User
    expire_behavior: IntegrationExpireBehavior
    expire_grace_period: int


class StreamIntegration(BaseIntegration):
    role_id: Optional[Snowflake]
    enable_emoticons: bool
    subscriber_count: int
    revoked: bool


class BotIntegration(BaseIntegration):
    application: IntegrationApplication
    scopes: List[str]


Integration = Union[BaseIntegration, StreamIntegration, BotIntegration]
