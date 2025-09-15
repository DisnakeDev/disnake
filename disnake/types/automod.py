# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

from .snowflake import Snowflake, SnowflakeList

AutoModTriggerType = Literal[1, 3, 4, 5]
AutoModEventType = Literal[1]
AutoModActionType = Literal[1, 2, 3]
AutoModPresetType = Literal[1, 2, 3]


class AutoModBlockMessageActionMetadata(TypedDict):
    custom_message: NotRequired[str]


class AutoModSendAlertActionMetadata(TypedDict):
    channel_id: Snowflake


class AutoModTimeoutActionMetadata(TypedDict):
    duration_seconds: int


AutoModActionMetadata = Union[
    AutoModBlockMessageActionMetadata,
    AutoModSendAlertActionMetadata,
    AutoModTimeoutActionMetadata,
]


class AutoModAction(TypedDict):
    type: AutoModActionType
    metadata: NotRequired[AutoModActionMetadata]


class AutoModTriggerMetadata(TypedDict, total=False):
    keyword_filter: list[str]
    regex_patterns: list[str]
    presets: list[AutoModPresetType]
    allow_list: list[str]
    mention_total_limit: int
    mention_raid_protection_enabled: bool


class AutoModRule(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    name: str
    creator_id: Snowflake
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    trigger_metadata: AutoModTriggerMetadata
    actions: list[AutoModAction]
    enabled: bool
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


class EditAutoModRule(TypedDict, total=False):
    name: str
    event_type: AutoModEventType
    trigger_metadata: AutoModTriggerMetadata
    actions: list[AutoModAction]
    enabled: bool
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


class CreateAutoModRule(TypedDict):
    name: str
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    trigger_metadata: NotRequired[AutoModTriggerMetadata]
    actions: list[AutoModAction]
    enabled: NotRequired[bool]
    exempt_roles: NotRequired[SnowflakeList]
    exempt_channels: NotRequired[SnowflakeList]
