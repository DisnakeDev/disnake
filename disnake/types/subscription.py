# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .snowflake import Snowflake

SubscriptionStatus = Literal[0, 1, 2]


class Subscription(TypedDict):
    id: Snowflake
    user_id: Snowflake
    sku_ids: List[Snowflake]
    entitlement_ids: List[Snowflake]
    renewal_sku_ids: Optional[List[Snowflake]]
    current_period_start: str
    current_period_end: str
    status: SubscriptionStatus
    canceled_at: Optional[str]
    # this is always missing unless queried with a private OAuth scope.
    country: NotRequired[str]
