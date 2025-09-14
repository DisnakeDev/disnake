# SPDX-License-Identifier: MIT

import typing as t

from mypy.plugin import Plugin


# FIXME: properly deprecate this in the future
class DisnakePlugin(Plugin):
    """Custom mypy plugin; no-op as of version 2.9."""


def plugin(version: str) -> t.Type[Plugin]:
    return DisnakePlugin
