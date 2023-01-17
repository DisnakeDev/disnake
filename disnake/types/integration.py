# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict, Union

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .user import User


class IntegrationApplication(TypedDict):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    summary: str
    bot: NotRequired[User]
    role_connections_verification_url: NotRequired[str]


class IntegrationAccount(TypedDict):
    id: str
    name: str


IntegrationExpireBehavior = Literal[0, 1]


class PartialIntegration(TypedDict):
    id: Snowflake
    name: str
    type: IntegrationType
    account: IntegrationAccount
    # undocumented, only shown in example - used for audit logs
    application_id: NotRequired[Snowflake]


IntegrationType = Literal["twitch", "youtube", "discord"]


class BaseIntegration(PartialIntegration):
    enabled: bool
    user: NotRequired[User]


class StreamIntegration(BaseIntegration):
    role_id: Optional[Snowflake]
    enable_emoticons: bool
    subscriber_count: int
    revoked: bool
    syncing: bool
    synced_at: str
    expire_behavior: IntegrationExpireBehavior
    expire_grace_period: int


class BotIntegration(BaseIntegration):
    application: IntegrationApplication
    scopes: List[str]


Integration = Union[BaseIntegration, StreamIntegration, BotIntegration]
