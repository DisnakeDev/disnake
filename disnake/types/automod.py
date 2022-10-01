# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, TypedDict, Union

from typing_extensions import NotRequired

from .snowflake import Snowflake, SnowflakeList

AutoModTriggerType = Literal[1, 2, 3, 4, 5]
AutoModEventType = Literal[1]
AutoModActionType = Literal[1, 2]
AutoModPresetType = Literal[1, 2, 3]


class AutoModBlockMessageActionMetadata(TypedDict):
    ...


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
    keyword_filter: List[str]
    presets: List[AutoModPresetType]
    allow_list: List[str]
    mention_total_limit: int


class AutoModRule(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    name: str
    creator_id: Snowflake
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    trigger_metadata: AutoModTriggerMetadata
    actions: List[AutoModAction]
    enabled: bool
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


class EditAutoModRule(TypedDict, total=False):
    name: str
    event_type: AutoModEventType
    trigger_metadata: AutoModTriggerMetadata
    actions: List[AutoModAction]
    enabled: bool
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


class CreateAutoModRule(TypedDict):
    name: str
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    trigger_metadata: NotRequired[AutoModTriggerMetadata]
    actions: List[AutoModAction]
    enabled: NotRequired[bool]
    exempt_roles: NotRequired[SnowflakeList]
    exempt_channels: NotRequired[SnowflakeList]
