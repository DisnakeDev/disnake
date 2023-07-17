# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .team import Team
from .user import User


class PartialAppInfo(TypedDict):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    cover_image: NotRequired[str]


class InstallParams(TypedDict):
    scopes: List[str]
    permissions: str


class AppInfo(PartialAppInfo):
    verify_key: str
    rpc_origins: NotRequired[List[str]]
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    bot_public: NotRequired[bool]
    bot_require_code_grant: NotRequired[bool]
    guild_id: NotRequired[Snowflake]
    primary_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    flags: NotRequired[int]
    tags: NotRequired[List[str]]
    install_params: NotRequired[InstallParams]
    custom_install_url: NotRequired[str]
    role_connections_verification_url: NotRequired[str]


class BotAppInfo(AppInfo):
    owner: User
    team: NotRequired[Team]


# see https://discord.com/developers/docs/topics/gateway-events#ready-ready-event-fields
class PartialGatewayAppInfo(TypedDict):
    id: Snowflake
    flags: int
