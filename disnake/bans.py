# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, NamedTuple, Optional

__all__ = ("BanEntry",)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .user import User


class BanEntry(NamedTuple):
    reason: Optional[str]
    user: "User"


class BulkBanResult(NamedTuple):
    banned: List[Snowflake]
    failed: List[Snowflake]
