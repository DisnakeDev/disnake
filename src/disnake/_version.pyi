# SPDX-License-Identifier: MIT

from typing import Literal, NamedTuple

__version__: str

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int

version_info: VersionInfo
