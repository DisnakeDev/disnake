"""
The MIT License (MIT)

Copyright (c) 2022-present Disnake Development

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

from typing import List, Literal, Optional, TypedDict

from .snowflake import Snowflake, SnowflakeList

AutomodTriggerType = Literal[1, 2, 3, 4]
AutomodEventType = Literal[1]
AutomodActionType = Literal[1, 2]
# TODO: will likely change
AutomodListType = Literal["PROFANITY", "SEXUAL_CONTENT", "SLURS"]


# TODO: undocumented
class AutomodActionMetadata(TypedDict, total=False):
    channel_id: Snowflake


class AutomodAction(TypedDict):
    type: AutomodActionType
    metadata: AutomodActionMetadata


class AutomodTriggerMetadata(TypedDict, total=False):
    keyword_filter: List[str]
    keyword_lists: List[AutomodListType]


class AutomodRule(TypedDict):
    id: Snowflake
    name: str
    enabled: bool
    guild_id: Snowflake
    creator_id: Snowflake
    event_type: AutomodEventType
    trigger_type: AutomodTriggerType
    actions: List[AutomodAction]
    trigger_metadata: AutomodTriggerMetadata
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


class EditAutomodRule(TypedDict, total=False):
    name: str
    enabled: bool
    trigger_type: AutomodTriggerType
    actions: List[AutomodAction]
    trigger_metadata: Any
    exempt_roles: SnowflakeList
    exempt_channels: SnowflakeList


# TODO
class CreateAutomodRule(EditAutomodRule, total=False):
    event_type: AutomodEventType


# TODO: gateway event, move once full state typings are added
class AutomodActionExecutionEvent(TypedDict):
    guild_id: Snowflake
    action: AutomodAction
    rule_id: Snowflake
    rule_trigger_type: AutomodTriggerType
    channel_id: Optional[Snowflake]
    message_id: Optional[Snowflake]
    alert_system_message_id: Optional[Snowflake]
    content: str
    matched_keyword: Optional[str]
    matched_content: Optional[str]
