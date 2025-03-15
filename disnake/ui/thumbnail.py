# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Optional, Tuple

from ..components import Thumbnail as ThumbnailComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

__all__ = ("Thumbnail",)


class Thumbnail(UIComponent):
    """Represents a UI thumbnail.

    This is only supported as the :attr:`~.ui.Section.accessory` of a section component.

    .. versionadded:: 2.11

    Parameters
    ----------
    media: Any
        n/a
    description: Optional[:class:`str`]
        The thumbnail's description ("alt text"), if any.
    spoiler: :class:`bool`
        Whether the thumbnail is marked as a spoiler. Defaults to ``False``.
    """

    __repr_attributes__: Tuple[str, ...] = (
        "media",
        "description",
        "spoiler",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: ThumbnailComponent = MISSING

    def __init__(
        self,
        *,
        media: Any,  # XXX: positional?
        description: Optional[str] = None,
        spoiler: bool = False,
    ) -> None:
        self._underlying = ThumbnailComponent._raw_construct(
            type=ComponentType.thumbnail,
            media=media,
            description=description,
            spoiler=spoiler,
        )

    @property
    def media(self) -> Any:
        """Any: n/a"""
        return self._underlying.media

    @media.setter
    def media(self, value: Any) -> None:
        self._underlying.media = value

    @property
    def description(self) -> Optional[str]:
        """Optional[:class:`str`]: The thumbnail's description ("alt text"), if any."""
        return self._underlying.description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._underlying.description = value

    @property
    def spoiler(self) -> bool:
        """:class:`bool`: Whether the thumbnail is marked as a spoiler."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        self._underlying.spoiler = value
