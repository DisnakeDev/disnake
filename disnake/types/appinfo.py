# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .team import Team
from .user import User


class BaseAppInfo(TypedDict):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    summary: str
    verify_key: str
    hook: NotRequired[bool]
    max_participants: NotRequired[int]


class InstallParams(TypedDict):
    scopes: List[str]
    permissions: str


class AppInfo(BaseAppInfo):
    rpc_origins: List[str]
    bot_public: bool
    bot_require_code_grant: bool
    owner: User
    team: NotRequired[Team]
    guild_id: NotRequired[Snowflake]
    primary_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    tags: NotRequired[List[str]]
    install_params: NotRequired[InstallParams]
    custom_install_url: NotRequired[str]
    role_connections_verification_url: NotRequired[str]


class PartialAppInfo(BaseAppInfo, total=False):
    rpc_origins: List[str]
    cover_image: str
    flags: int


class PartialGatewayAppInfo(TypedDict):
    id: Snowflake
    flags: int
