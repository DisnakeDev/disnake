# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Sequence, Tuple

from ..components import MediaGallery as MediaGalleryComponent, MediaGalleryItem
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

__all__ = ("MediaGallery",)


class MediaGallery(UIComponent):
    """Represents a UI media gallery.

    .. versionadded:: 2.11

    Parameters
    ----------
    *items: :class:`.MediaGalleryItem`
        The list of images in this gallery.
    """

    __repr_attributes__: Tuple[str, ...] = ("items",)
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: MediaGalleryComponent = MISSING

    # FIXME: MediaGalleryItem currently isn't user-instantiable
    def __init__(self, *items: MediaGalleryItem) -> None:
        self._underlying = MediaGalleryComponent._raw_construct(
            type=ComponentType.media_gallery,
            items=list(items),
        )

    @property
    def items(self) -> List[MediaGalleryItem]:
        """List[:class:`.MediaGalleryItem`]: The images in this gallery."""
        return self._underlying.items

    @items.setter
    def items(self, values: Sequence[MediaGalleryItem]) -> None:
        self._underlying.items = list(values)
