# SPDX-License-Identifier: MIT

import typing as t
import warnings

from mypy.plugin import Plugin


class DisnakePlugin(Plugin):
    """Deprecated mypy plugin."""

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        super().__init__(*args, **kwargs)

        # show deprecation warning when run
        old_filters = warnings.filters[:]
        try:
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                "disnake.ext.mypy_plugin is deprecated and a no-op",
                category=DeprecationWarning,
                stacklevel=2,
            )
        finally:
            warnings.filters[:] = old_filters  # type: ignore


def plugin(version: str) -> t.Type[Plugin]:
    return DisnakePlugin
