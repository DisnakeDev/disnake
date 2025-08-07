# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Tuple

from ..components import FileComponent, UnfurledMediaItem
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent, handle_media_item_input

if TYPE_CHECKING:
    from ._types import MediaItemInput

__all__ = ("File",)


class File(UIComponent):
    """Represents a UI file component.

    .. versionadded:: 2.11

    Parameters
    ----------
    file: Union[:class:`str`, :class:`.UnfurledMediaItem`]
        The file to display. This **only** supports attachment references (i.e.
        using the ``attachment://`` syntax), not arbitrary URLs.
    spoiler: :class:`bool`
        Whether the file is marked as a spoiler. Defaults to ``False``.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
        "file",
        "spoiler",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: FileComponent = MISSING

    def __init__(
        self,
        file: MediaItemInput,
        *,
        spoiler: bool = False,
    ) -> None:
        self._underlying = FileComponent._raw_construct(
            type=ComponentType.file,
            file=handle_media_item_input(file),
            spoiler=spoiler,
        )

    @property
    def file(self) -> UnfurledMediaItem:
        """:class:`.UnfurledMediaItem`: The file to display."""
        return self._underlying.file

    @file.setter
    def file(self, value: MediaItemInput) -> None:
        self._underlying.file = handle_media_item_input(value)

    @property
    def spoiler(self) -> bool:
        """:class:`bool`: Whether the file is marked as a spoiler."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        self._underlying.spoiler = value
