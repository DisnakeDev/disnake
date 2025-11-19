# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .snowflake import Snowflake
    from .team import Team
    from .user import User

# (also called "installation context", which seems more accurate)
ApplicationIntegrationType = Literal[0, 1]  # GUILD_INSTALL, USER_INSTALL
ApplicationEventWebhookStatus = Literal[0, 1, 2]  # disabled, enabled, disabled by Discord


class BaseAppInfo(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    description: str
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    summary: str
    verify_key: str
    hook: NotRequired[bool]
    max_participants: NotRequired[int]


class InstallParams(TypedDict):
    scopes: list[str]
    permissions: str


class ApplicationIntegrationTypeConfiguration(TypedDict, total=False):
    oauth2_install_params: InstallParams


class AppInfo(BaseAppInfo):
    rpc_origins: NotRequired[list[str]]
    bot_public: bool
    bot_require_code_grant: bool
    bot: NotRequired[User]
    owner: User
    team: NotRequired[Team]
    flags: NotRequired[int]
    guild_id: NotRequired[Snowflake]
    primary_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    tags: NotRequired[list[str]]
    install_params: NotRequired[InstallParams]
    custom_install_url: NotRequired[str]
    role_connections_verification_url: NotRequired[str]
    approximate_guild_count: NotRequired[int]
    approximate_user_install_count: NotRequired[int]
    approximate_user_authorization_count: NotRequired[int]
    redirect_uris: NotRequired[list[str]]
    interactions_endpoint_url: NotRequired[str | None]
    event_webhooks_url: NotRequired[str | None]
    event_webhooks_status: NotRequired[ApplicationEventWebhookStatus]
    event_webhooks_type: NotRequired[list[str]]
    # values in this dict generally shouldn't be null, but they can be empty dicts
    integration_types_config: NotRequired[dict[str, ApplicationIntegrationTypeConfiguration]]


class PartialAppInfo(BaseAppInfo, total=False):
    rpc_origins: list[str]
    cover_image: str
    flags: int


# see https://discord.com/developers/docs/topics/gateway-events#ready-ready-event-fields
class PartialGatewayAppInfo(TypedDict):
    id: Snowflake
    flags: int


class EditAppInfo(TypedDict, total=False):
    custom_install_url: str | None
    description: str
    role_connections_verification_url: str | None
    install_params: InstallParams | None
    integration_types_config: dict[str, ApplicationIntegrationTypeConfiguration]
    flags: int
    icon: str | None
    cover_image: str | None
    interactions_endpoint_url: str | None
    tags: list[str] | None
    event_webhooks_url: str | None
    event_webhooks_status: ApplicationEventWebhookStatus
    event_webhooks_types: list[str] | None
