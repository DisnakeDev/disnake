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
from typing import Dict, List, Optional, TypedDict

from .snowflake import Snowflake


class DiscoveryMetadata(TypedDict):
    guild_id: Snowflake
    primary_category_id: int
    keywords: List[str]
    emoji_discoverability_enabled: bool
    partner_actioned_timestamp: Optional[str]
    partner_application_timestamp: Optional[str]
    category_ids: List[int]


class DiscoveryCategory(TypedDict):
    id: int
    name: str
    is_primary: bool


class ValidateDiscoveryTerm(TypedDict):
    valid: bool


class _DiscoveryRequirementsNSFWPropertiesOptional(TypedDict, total=False):
    channels: List[Snowflake]
    channel_banned_keywords: Dict[Snowflake, List[str]]
    name: str
    name_banned_keywords: List[str]
    description: str
    description_banned_keywords: List[str]


class DiscoveryRequirementsNSFWProperties(_DiscoveryRequirementsNSFWPropertiesOptional):
    pass


class DiscoveryRequirementsHealthScore(TypedDict):
    avg_nonnew_communicators: Optional[str]
    avg_nonnew_participators: Optional[str]
    num_intentful_joiners: Optional[str]
    perc_ret_w1_intentful: Optional[float]


class _DiscoveryRequirementsOptional(TypedDict, total=False):
    guild_id: Snowflake
    safe_environment: bool
    healty: Optional[bool]
    health_score_pending: bool
    size: bool
    nsfw_properties: DiscoveryRequirementsNSFWProperties
    protected: bool
    valid_rules_channel: bool
    retention_healthy: Optional[bool]
    engagement_healthy: Optional[bool]
    age: bool
    minimum_age: int
    health_score: DiscoveryRequirementsHealthScore
    minimum_size: int
    grace_period_end_date: str


class DiscoveryRequirements(_DiscoveryRequirementsOptional):
    sufficient: Optional[bool]
    sufficient_without_grace_period: Optional[bool]
