# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, NamedTuple

__all__ = ("BanEntry",)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .user import User


class BanEntry(NamedTuple):
    reason: str | None
    user: User


class BulkBanResult(NamedTuple):
    banned: Sequence[Snowflake]
    failed: Sequence[Snowflake]
