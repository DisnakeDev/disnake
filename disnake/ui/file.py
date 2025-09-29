# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, ClassVar, Optional, Tuple

from ..components import FileComponent, UnfurledMediaItem, handle_media_item_input
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..components import LocalMediaItemInput

__all__ = ("File",)


class File(UIComponent):
    """Represents a UI file component.

    .. versionadded:: 2.11

    Parameters
    ----------
    file: Union[:class:`str`, :class:`.UnfurledMediaItem`]
        The file to display. This **only** supports attachment references (i.e.
        using the ``attachment://<filename>`` syntax), not arbitrary URLs.
    spoiler: :class:`bool`
        Whether the file is marked as a spoiler. Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
        "file",
        "spoiler",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: FileComponent = MISSING

    def __init__(
        self,
        file: LocalMediaItemInput,
        *,
        spoiler: bool = False,
        id: int = 0,
    ) -> None:
        file_media = handle_media_item_input(file)
        if not file_media.url.startswith("attachment://"):
            msg = "File component only supports `attachment://` references, not external media URLs"
            raise ValueError(msg)

        self._underlying = FileComponent._raw_construct(
            type=ComponentType.file,
            id=id,
            file=file_media,
            spoiler=spoiler,
            name=None,
            size=None,
        )

    @property
    def file(self) -> UnfurledMediaItem:
        """:class:`.UnfurledMediaItem`: The file to display."""
        return self._underlying.file

    @file.setter
    def file(self, value: LocalMediaItemInput) -> None:
        file_media = handle_media_item_input(value)
        if not file_media.url.startswith("attachment://"):
            msg = "File component only supports `attachment://` references, not external media URLs"
            raise ValueError(msg)
        self._underlying.file = file_media

    @property
    def spoiler(self) -> bool:
        """:class:`bool`: Whether the file is marked as a spoiler."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        self._underlying.spoiler = value

    @property
    def name(self) -> Optional[str]:
        """Optional[:class:`str`]: The name of the file.
        This is available in objects from the API, and ignored when sending.
        """
        return self._underlying.name

    @property
    def size(self) -> Optional[int]:
        """Optional[:class:`int`]: The size of the file.
        This is available in objects from the API, and ignored when sending.
        """
        return self._underlying.size

    @classmethod
    def from_component(cls, file: FileComponent) -> Self:
        media = file.file
        if not media.url.startswith("attachment://") and file.name:
            # turn cdn url into `attachment://` url, retain other fields
            media = copy.copy(media)
            media.url = f"attachment://{file.name}"

        self = cls(
            file=media,
            spoiler=file.spoiler,
            id=file.id,
        )
        # copy read-only fields
        self._underlying.name = file.name
        self._underlying.size = file.size
        return self
