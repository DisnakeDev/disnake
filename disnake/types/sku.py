# SPDX-License-Identifier: MIT

from typing import Literal, TypedDict

from .snowflake import Snowflake

SKUType = Literal[2, 3, 5, 6]


class SKU(TypedDict):
    id: Snowflake
    type: SKUType
    application_id: Snowflake
    name: str
    slug: str
    flags: int
    # there are more fields, but they aren't documented and mostly uninteresting
