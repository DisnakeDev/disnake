# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional, Tuple

from ..components import Thumbnail as ThumbnailComponent, UnfurledMediaItem
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent, handle_media_item_input

if TYPE_CHECKING:
    from ._types import MediaItemInput

__all__ = ("Thumbnail",)


class Thumbnail(UIComponent):
    """Represents a UI thumbnail.

    This is only supported as the :attr:`~.ui.Section.accessory` of a section component.

    .. versionadded:: 2.11

    Parameters
    ----------
    media: Union[:class:`str`, :class:`.AssetMixin`, :class:`.Attachment`, :class:`.UnfurledMediaItem`]
        The media item to display. Can be an arbitrary URL or attachment
        reference (``attachment://<filename>``).
    description: Optional[:class:`str`]
        The thumbnail's description ("alt text"), if any.
    spoiler: :class:`bool`
        Whether the thumbnail is marked as a spoiler. Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
        "media",
        "description",
        "spoiler",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: ThumbnailComponent = MISSING

    def __init__(
        self,
        media: MediaItemInput,
        description: Optional[str] = None,
        *,
        spoiler: bool = False,
        id: int = 0,
    ) -> None:
        self._underlying = ThumbnailComponent._raw_construct(
            type=ComponentType.thumbnail,
            id=id,
            media=handle_media_item_input(media),
            description=description,
            spoiler=spoiler,
        )

    @property
    def media(self) -> UnfurledMediaItem:
        """:class:`.UnfurledMediaItem`: The media item to display."""
        return self._underlying.media

    @media.setter
    def media(self, value: MediaItemInput) -> None:
        self._underlying.media = handle_media_item_input(value)

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
