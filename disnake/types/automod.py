"""
The MIT License (MIT)

Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import List, Literal, TypedDict, Union

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


class _AutoModActionOptional(TypedDict, total=False):
    metadata: AutoModActionMetadata


class AutoModAction(_AutoModActionOptional):
    type: AutoModActionType


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


class _CreateAutoModRuleOptional(TypedDict, total=False):
    trigger_metadata: AutoModTriggerMetadata
    enabled: bool
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


class CreateAutoModRule(_CreateAutoModRuleOptional):
    name: str
    event_type: AutoModEventType
    trigger_type: AutoModTriggerType
    actions: List[AutoModAction]
