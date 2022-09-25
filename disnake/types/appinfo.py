# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Optional, TypedDict

from .snowflake import Snowflake
from .team import Team
from .user import User


class BaseAppInfo(TypedDict):
    id: Snowflake
    name: str
    verify_key: str
    icon: Optional[str]
    summary: str
    description: str


class InstallParams(TypedDict):
    scopes: List[str]
    permissions: str


class _AppInfoOptional(TypedDict, total=False):
    team: Team
    guild_id: Snowflake
    primary_sku_id: Snowflake
    slug: str
    terms_of_service_url: str
    privacy_policy_url: str
    hook: bool
    max_participants: int
    tags: List[str]
    install_params: InstallParams
    custom_install_url: str


class AppInfo(BaseAppInfo, _AppInfoOptional):
    rpc_origins: List[str]
    owner: User
    bot_public: bool
    bot_require_code_grant: bool


class _PartialAppInfoOptional(TypedDict, total=False):
    rpc_origins: List[str]
    cover_image: str
    hook: bool
    terms_of_service_url: str
    privacy_policy_url: str
    max_participants: int
    flags: int


class PartialAppInfo(_PartialAppInfoOptional, BaseAppInfo):
    pass


class PartialGatewayAppInfo(TypedDict):
    id: Snowflake
    flags: int
