# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Optional, TypedDict

from .snowflake import Snowflake
from .team import Team
from .user import User


class _PartialAppInfoOptional(TypedDict, total=False):
    cover_image: str


class PartialAppInfo(_PartialAppInfoOptional):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str


class InstallParams(TypedDict):
    scopes: List[str]
    permissions: str


class _AppInfoOptional(PartialAppInfo, total=False):
    rpc_origins: List[str]
    terms_of_service_url: str
    privacy_policy_url: str
    bot_public: bool
    bot_require_code_grant: bool
    guild_id: Snowflake
    primary_sku_id: Snowflake
    slug: str
    flags: int
    tags: List[str]
    install_params: InstallParams
    custom_install_url: str


class AppInfo(_AppInfoOptional):
    verify_key: str


class _BotAppInfoOptional(TypedDict, total=False):
    team: Team


class BotAppInfo(AppInfo, _BotAppInfoOptional):
    owner: User


class PartialGatewayAppInfo(TypedDict):
    id: Snowflake
    flags: int
