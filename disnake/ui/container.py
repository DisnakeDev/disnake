# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, List, Optional, Tuple, Union

from ..colour import Colour
from ..components import Container as ContainerComponent
from ..enums import ComponentType
from ..utils import copy_doc
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
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.

    Attributes
    ----------
    components: List[Union[:class:`~.ui.ActionRow`, :class:`~.ui.Section`, :class:`~.ui.TextDisplay`, :class:`~.ui.MediaGallery`, :class:`~.ui.File`, :class:`~.ui.Separator`]]
        The list of components in this container.
    accent_colour: Optional[:class:`.Colour`]
        The accent colour of the container.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
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
        id: int = 0,
    ) -> None:
        self._id: int = id
        # this list can be modified without any runtime checks later on,
        # just assume the user knows what they're doing at that point
        self.components: List[ContainerChildUIComponent] = [
            ensure_ui_component(c, "components") for c in components
        ]
        # FIXME: add accent_color
        self.accent_colour: Optional[Colour] = accent_colour
        self.spoiler: bool = spoiler

    # these are reimplemented here to store the value in a separate attribute,
    # since `Container` lazily constructs `_underlying`, unlike most components
    @property
    @copy_doc(UIComponent.id)
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def _underlying(self) -> ContainerComponent:
        return ContainerComponent._raw_construct(
            type=ComponentType.container,
            id=self._id,
            components=[comp._underlying for comp in self.components],
            _accent_colour=self.accent_colour.value if self.accent_colour is not None else None,
            spoiler=self.spoiler,
        )
