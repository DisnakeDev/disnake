# SPDX-License-Identifier: MIT

from typing import TypeAlias

Snowflake: TypeAlias = str | int
SnowflakeList: TypeAlias = list[str] | list[int]  # keep separate for variance
