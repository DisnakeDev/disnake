# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .snowflake import Snowflake

SubscriptionStatus = Literal[0, 1, 2]


class Subscription(TypedDict):
    id: Snowflake
    user_id: Snowflake
    sku_ids: list[Snowflake]
    entitlement_ids: list[Snowflake]
    renewal_sku_ids: list[Snowflake] | None
    current_period_start: str
    current_period_end: str
    status: SubscriptionStatus
    canceled_at: str | None
    # this is always missing unless queried with a private OAuth scope.
    country: NotRequired[str]
