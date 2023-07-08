# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
import sys
from enum import Enum
from pathlib import Path
from typing import NamedTuple, NoReturn

TARGET_FILE = Path("disnake/__init__.py")
INIT = TARGET_FILE.read_text("utf-8")

version_re = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+)?)?")


class ReleaseLevel(Enum):
    alpha = "a"
    beta = "b"
    candidate = "rc"
    final = ""


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: ReleaseLevel
    serial: int

    @classmethod
    def from_str(cls, s: str) -> VersionInfo:
        match = version_re.fullmatch(s)
        if not match:
            raise ValueError(f"invalid version: '{s}'")

        major, minor, micro, releaselevel, serial = match.groups()
        return VersionInfo(
            int(major),
            int(minor),
            int(micro),
            ReleaseLevel(releaselevel or ""),
            int(serial or 0),
        )

    def __str__(self) -> str:
        s = f"{self.major}.{self.minor}.{self.micro}"
        if self.releaselevel is not ReleaseLevel.final:
            s += self.releaselevel.value
            if self.serial:
                s += str(self.serial)
        return s

    def to_versioninfo(self) -> str:
        return (
            f"VersionInfo(major={self.major}, minor={self.minor}, micro={self.micro}, "
            f'releaselevel="{self.releaselevel.name}", serial={self.serial})'
        )


def get_current_version() -> VersionInfo:
    match = re.search(r"^__version__\b.*\"(.+?)\"$", INIT, re.MULTILINE)
    assert match, "could not find current version in __init__.py"
    return VersionInfo.from_str(match[1])


def replace_line(text: str, regex: str, repl: str) -> str:
    lines = []
    found = False

    for line in text.split("\n"):
        if re.search(regex, line):
            found = True
            line = repl
        lines.append(line)

    assert found, f"failed to find `{regex}` in file"
    return "\n".join(lines)


def fail(msg: str) -> NoReturn:
    print("error:", msg, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) > 2:
        fail(f"Usage: {sys.argv[0]} [<version>|dev]")

    current_version = get_current_version()

    # if no version is given, just print current version
    if len(sys.argv) == 1:
        print(str(current_version))
        return

    # else, update to specified version
    new_version_str = sys.argv[1]

    if new_version_str == "dev":
        if current_version.releaselevel is not ReleaseLevel.final:
            fail("Current version must be final to bump to dev version")
        new_version = VersionInfo(
            major=current_version.major,
            minor=current_version.minor + 1,
            micro=0,
            releaselevel=ReleaseLevel.alpha,
            serial=0,
        )
    else:
        new_version = VersionInfo.from_str(new_version_str)

    text = INIT
    text = replace_line(text, r"^__version__\b", f'__version__ = "{str(new_version)}"')
    text = replace_line(
        text, r"^version_info\b", f"version_info: VersionInfo = {new_version.to_versioninfo()}"
    )

    if text != INIT:
        TARGET_FILE.write_text(text, "utf-8")

    print(f"Updated version to {str(new_version)}")


main()
