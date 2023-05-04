# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import List, Literal, Optional, TypedDict, Union

from typing_extensions import NotRequired

from .automod import (
    AutoModAction,
    AutoModEventType,
    AutoModRule,
    AutoModTriggerMetadata,
    AutoModTriggerType,
)
from .channel import ChannelType, PermissionOverwrite, VideoQualityMode
from .guild import (
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    MFALevel,
    VerificationLevel,
)
from .guild_scheduled_event import GuildScheduledEvent
from .integration import IntegrationExpireBehavior, PartialIntegration
from .interactions import ApplicationCommand, ApplicationCommandPermissions
from .role import Role
from .snowflake import Snowflake
from .threads import Thread
from .user import User
from .webhook import Webhook

AuditLogEvent = Literal[
    1,
    10,
    11,
    12,
    13,
    14,
    15,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    30,
    31,
    32,
    40,
    41,
    42,
    50,
    51,
    52,
    60,
    61,
    62,
    72,
    73,
    74,
    75,
    80,
    81,
    82,
    83,
    84,
    85,
    90,
    91,
    92,
    100,
    101,
    102,
    110,
    111,
    112,
    121,
    140,
    141,
    142,
    143,
]


class _AuditLogChange_Str(TypedDict):
    key: Literal[
        "name",
        "description",
        "preferred_locale",
        "vanity_url_code",
        "topic",
        "code",
        "allow",
        "deny",
        "permissions",
        "tags",
    ]
    new_value: str
    old_value: str


class _AuditLogChange_AssetHash(TypedDict):
    key: Literal[
        "icon_hash",
        "splash_hash",
        "discovery_splash_hash",
        "banner_hash",
        "avatar_hash",
        "asset",
    ]
    new_value: str
    old_value: str


class _AuditLogChange_Snowflake(TypedDict):
    key: Literal[
        "id",
        "owner_id",
        "afk_channel_id",
        "rules_channel_id",
        "public_updates_channel_id",
        "widget_channel_id",
        "system_channel_id",
        "application_id",
        "channel_id",
        "inviter_id",
        "guild_id",
    ]
    new_value: Snowflake
    old_value: Snowflake


class _AuditLogChange_Bool(TypedDict):
    key: Literal[
        "widget_enabled",
        "nsfw",
        "hoist",
        "mentionable",
        "temporary",
        "deaf",
        "mute",
        "nick",
        "enabled_emoticons",
        "region",
        "rtc_region",
        "available",
        "archived",
        "locked",
        "premium_progress_bar_enabled",
        "enabled",
    ]
    new_value: bool
    old_value: bool


class _AuditLogChange_Int(TypedDict):
    key: Literal[
        "afk_timeout",
        "prune_delete_days",
        "position",
        "bitrate",
        "rate_limit_per_user",
        "color",
        "max_uses",
        "max_age",
        "user_limit",
        "auto_archive_duration",
        "default_auto_archive_duration",
    ]
    new_value: int
    old_value: int


class _AuditLogChange_ListSnowflake(TypedDict):
    key: Literal["exempt_roles", "exempt_channels"]
    new_value: List[Snowflake]
    old_value: List[Snowflake]


class _AuditLogChange_ListRole(TypedDict):
    key: Literal["$add", "$remove"]
    new_value: List[Role]
    old_value: List[Role]


class _AuditLogChange_MFALevel(TypedDict):
    key: Literal["mfa_level"]
    new_value: MFALevel
    old_value: MFALevel


class _AuditLogChange_VerificationLevel(TypedDict):
    key: Literal["verification_level"]
    new_value: VerificationLevel
    old_value: VerificationLevel


class _AuditLogChange_ExplicitContentFilter(TypedDict):
    key: Literal["explicit_content_filter"]
    new_value: ExplicitContentFilterLevel
    old_value: ExplicitContentFilterLevel


class _AuditLogChange_DefaultMessageNotificationLevel(TypedDict):
    key: Literal["default_message_notifications"]
    new_value: DefaultMessageNotificationLevel
    old_value: DefaultMessageNotificationLevel


class _AuditLogChange_ChannelType(TypedDict):
    key: Literal["type"]
    new_value: ChannelType
    old_value: ChannelType


class _AuditLogChange_IntegrationExpireBehaviour(TypedDict):
    key: Literal["expire_behavior"]
    new_value: IntegrationExpireBehavior
    old_value: IntegrationExpireBehavior


class _AuditLogChange_VideoQualityMode(TypedDict):
    key: Literal["video_quality_mode"]
    new_value: VideoQualityMode
    old_value: VideoQualityMode


class _AuditLogChange_Overwrites(TypedDict):
    key: Literal["permission_overwrites"]
    new_value: List[PermissionOverwrite]
    old_value: List[PermissionOverwrite]


class _AuditLogChange_Datetime(TypedDict):
    key: Literal["communication_disabled_until"]
    new_value: datetime.datetime
    old_value: datetime.datetime


class _AuditLogChange_ApplicationCommandPermissions(TypedDict):
    key: str
    new_value: ApplicationCommandPermissions
    old_value: ApplicationCommandPermissions


class _AuditLogChange_AutoModTriggerType(TypedDict):
    key: Literal["trigger_type"]
    new_value: AutoModTriggerType
    old_value: AutoModTriggerType


class _AuditLogChange_AutoModEventType(TypedDict):
    key: Literal["event_type"]
    new_value: AutoModEventType
    old_value: AutoModEventType


class _AuditLogChange_AutoModActions(TypedDict):
    key: Literal["actions"]
    new_value: List[AutoModAction]
    old_value: List[AutoModAction]


class _AuditLogChange_AutoModTriggerMetadata(TypedDict):
    key: Literal["trigger_metadata"]
    new_value: AutoModTriggerMetadata
    old_value: AutoModTriggerMetadata


AuditLogChange = Union[
    _AuditLogChange_Str,
    _AuditLogChange_AssetHash,
    _AuditLogChange_Snowflake,
    _AuditLogChange_Int,
    _AuditLogChange_Bool,
    _AuditLogChange_ListSnowflake,
    _AuditLogChange_ListRole,
    _AuditLogChange_MFALevel,
    _AuditLogChange_VerificationLevel,
    _AuditLogChange_ExplicitContentFilter,
    _AuditLogChange_DefaultMessageNotificationLevel,
    _AuditLogChange_ChannelType,
    _AuditLogChange_IntegrationExpireBehaviour,
    _AuditLogChange_VideoQualityMode,
    _AuditLogChange_Overwrites,
    _AuditLogChange_Datetime,
    _AuditLogChange_ApplicationCommandPermissions,
    _AuditLogChange_AutoModTriggerType,
    _AuditLogChange_AutoModEventType,
    _AuditLogChange_AutoModActions,
    _AuditLogChange_AutoModTriggerMetadata,
]


class AuditEntryInfo(TypedDict):
    delete_member_days: str
    members_removed: str
    channel_id: Optional[Snowflake]
    message_id: Snowflake
    count: str
    id: Snowflake
    type: Literal["0", "1"]
    role_name: str
    application_id: Snowflake
    auto_moderation_rule_name: str
    auto_moderation_rule_trigger_type: str


class AuditLogEntry(TypedDict):
    target_id: Optional[str]
    changes: NotRequired[List[AuditLogChange]]
    user_id: Optional[Snowflake]
    id: Snowflake
    action_type: AuditLogEvent
    options: NotRequired[AuditEntryInfo]
    reason: NotRequired[str]


class AuditLog(TypedDict):
    audit_log_entries: List[AuditLogEntry]
    application_commands: List[ApplicationCommand]
    auto_moderation_rules: List[AutoModRule]
    guild_scheduled_events: List[GuildScheduledEvent]
    integrations: List[PartialIntegration]
    threads: List[Thread]
    users: List[User]
    webhooks: List[Webhook]
