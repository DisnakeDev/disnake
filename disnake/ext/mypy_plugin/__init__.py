# SPDX-License-Identifier: MIT


from mypy.plugin import Plugin


# FIXME: properly deprecate this in the future
class DisnakePlugin(Plugin):
    """Custom mypy plugin; no-op as of version 2.9."""


def plugin(version: str) -> type[Plugin]:
    return DisnakePlugin
