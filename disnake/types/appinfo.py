# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Dict, List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .team import Team
from .user import User

# (also called "installation context", which seems more accurate)
ApplicationIntegrationType = Literal[0, 1]  # GUILD_INSTALL, USER_INSTALL


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


class ApplicationIntegrationTypeConfiguration(TypedDict, total=False):
    oauth2_install_params: InstallParams


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
    approximate_guild_count: NotRequired[int]
    approximate_user_install_count: NotRequired[int]
    # values in this dict generally shouldn't be null, but they can be empty dicts
    integration_types_config: NotRequired[Dict[str, ApplicationIntegrationTypeConfiguration]]


class PartialAppInfo(BaseAppInfo, total=False):
    rpc_origins: List[str]
    cover_image: str
    flags: int


# see https://discord.com/developers/docs/topics/gateway-events#ready-ready-event-fields
class PartialGatewayAppInfo(TypedDict):
    id: Snowflake
    flags: int
