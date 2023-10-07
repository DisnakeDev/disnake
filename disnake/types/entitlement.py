# SPDX-License-Identifier: MIT

from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake

EntitlementType = Literal[8]


class Entitlement(TypedDict):
    id: Snowflake
    sku_id: Snowflake
    user_id: NotRequired[Snowflake]
    guild_id: NotRequired[Snowflake]
    application_id: Snowflake
    type: EntitlementType
    deleted: bool
    starts_at: NotRequired[str]
    ends_at: NotRequired[str]
