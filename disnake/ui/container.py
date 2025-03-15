# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence, Tuple, Union

from ..colour import Colour
from ..components import Container as ContainerComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from .action_row import ActionRow, MessageUIComponent
    from .file import File
    from .media_gallery import MediaGallery
    from .section import Section
    from .separator import Separator
    from .text_display import TextDisplay

    ContainerChildUIComponent = Union[
        ActionRow[MessageUIComponent],
        Section,
        TextDisplay,
        MediaGallery,
        File,
        Separator,
    ]

__all__ = ("Container",)


class Container(UIComponent):
    """Represents a UI container.

    This is visually similar to :class:`Embed`\\s, and contains other components.

    .. versionadded:: 2.11

    Parameters
    ----------
    *components: Union[:class:`~ui.ActionRow`, :class:`~ui.Section`, :class:`~ui.TextDisplay`, :class:`~ui.MediaGallery`, :class:`~ui.FileComponent`, :class:`~ui.Separator`]
        The components in this container.
    accent_colour: Optional[:class:`Colour`]
        The accent colour of the container.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler. Defaults to ``False``.
    """

    __repr_attributes__: Tuple[str, ...] = (
        "components",
        "accent_colour",
        "spoiler",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: ContainerComponent = MISSING

    def __init__(
        self,
        *components: ContainerChildUIComponent,
        accent_colour: Optional[Colour] = None,
        spoiler: bool = False,
    ) -> None:
        # TODO: this also just doesn't work this way
        self._underlying = ContainerComponent._raw_construct(
            type=ComponentType.container,
            components=list(components),
            _accent_colour=accent_colour.value if accent_colour is not None else None,
            spoiler=spoiler,
        )

    @property
    def components(self) -> Sequence[ContainerChildUIComponent]:
        """Sequence[Union[:class:`~ui.ActionRow`, :class:`~ui.Section`, :class:`~ui.TextDisplay`, :class:`~ui.MediaGallery`, :class:`~ui.FileComponent`, :class:`~ui.Separator`]]: The components in this container."""
        # TODO: SequenceProxy?
        return self._underlying.components

    @components.setter
    def components(self, values: Sequence[ContainerChildUIComponent]) -> None:
        # don't be too restrictive for easier future compatibility
        for value in values:
            if not isinstance(value, UIComponent):
                raise TypeError("TODO")
        self._underlying.components = values

    # FIXME: add accent_color
    @property
    def accent_colour(self) -> Optional[Colour]:
        """Optional[:class:`Colour`]: The accent colour of the container."""
        return self._underlying.accent_colour

    @accent_colour.setter
    def accent_colour(self, value: Optional[Colour]) -> None:
        self._underlying._accent_colour = value.value if value is not None else None

    @property
    def spoiler(self) -> bool:
        """:class:`bool`: Whether the container is marked as a spoiler."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        self._underlying.spoiler = value
