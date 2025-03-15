# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple, Union

from ..colour import Colour
from ..components import Container as ContainerComponent
from ..enums import ComponentType
from ..utils import SequenceProxy
from .item import UIComponent, ensure_ui_component

if TYPE_CHECKING:
    from .action_row import ActionRow, ActionRowMessageComponent
    from .file import File
    from .media_gallery import MediaGallery
    from .section import Section
    from .separator import Separator
    from .text_display import TextDisplay

    ContainerChildUIComponent = Union[
        ActionRow[ActionRowMessageComponent],
        Section,
        TextDisplay,
        MediaGallery,
        File,
        Separator,
    ]

__all__ = ("Container",)


class Container(UIComponent):
    """Represents a UI container.

    This is visually similar to :class:`.Embed`\\s, and contains other components.

    .. versionadded:: 2.11

    Parameters
    ----------
    *components: Union[:class:`~.ui.ActionRow`, :class:`~.ui.Section`, :class:`~.ui.TextDisplay`, :class:`~.ui.MediaGallery`, :class:`~.ui.File`, :class:`~.ui.Separator`]
        The components in this container.
    accent_colour: Optional[:class:`.Colour`]
        The accent colour of the container.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler. Defaults to ``False``.

    Attributes
    ----------
    accent_colour: Optional[:class:`.Colour`]
        The accent colour of the container.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler.
    """

    # unused, but technically required by base type
    __repr_attributes__: Tuple[str, ...] = (
        "components",
        "accent_colour",
        "spoiler",
    )

    # TODO: consider providing sequence operations (append, insert, remove, etc.)
    def __init__(
        self,
        *components: ContainerChildUIComponent,
        accent_colour: Optional[Colour] = None,
        spoiler: bool = False,
    ) -> None:
        self._components: List[ContainerChildUIComponent] = [
            # FIXME: typing broken until action rows become UIComponents
            ensure_ui_component(c, "components")
            for c in components
        ]
        # FIXME: add accent_color
        self.accent_colour: Optional[Colour] = accent_colour
        self.spoiler: bool = spoiler

    # TODO: consider moving runtime checks from constructor into property setters, also making these fields writable
    @property
    def components(self) -> Sequence[ContainerChildUIComponent]:
        """Sequence[Union[:class:`~.ui.ActionRow`, :class:`~.ui.Section`, :class:`~.ui.TextDisplay`, :class:`~.ui.MediaGallery`, :class:`~.ui.File`, :class:`~.ui.Separator`]]: A read-only copy of the components in this container."""
        return SequenceProxy(self._components)

    def __repr__(self) -> str:
        # implemented separately for now, due to SequenceProxy repr
        return f"<Container components={self._components!r} accent_colour={self.accent_colour!r} spoiler={self.spoiler!r}>"

    @property
    def _underlying(self) -> ContainerComponent:
        return ContainerComponent._raw_construct(
            type=ComponentType.container,
            components=[comp._underlying for comp in self._components],
            _accent_colour=self.accent_colour.value if self.accent_colour is not None else None,
            spoiler=self.spoiler,
        )
