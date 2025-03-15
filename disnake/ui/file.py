# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Tuple

from ..components import FileComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

__all__ = ("File",)


class File(UIComponent):
    """Represents a UI file component.

    .. versionadded:: 2.11

    Parameters
    ----------
    file: Any
        n/a
    spoiler: :class:`bool`
        Whether the file is marked as a spoiler. Defaults to ``False``.
    """

    __repr_attributes__: Tuple[str, ...] = (
        "file",
        "spoiler",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: FileComponent = MISSING

    def __init__(
        self,
        *,
        file: Any,  # XXX: positional?
        spoiler: bool = False,
    ) -> None:
        self._underlying = FileComponent._raw_construct(
            type=ComponentType.file,
            file=file,
            spoiler=spoiler,
        )

    @property
    def file(self) -> Any:
        """Any: n/a"""
        return self._underlying.file

    @file.setter
    def file(self, value: Any) -> None:
        self._underlying.file = value

    @property
    def spoiler(self) -> bool:
        """:class:`bool`: Whether the file is marked as a spoiler."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        self._underlying.spoiler = value
