# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, List, Optional, Tuple, Union, cast

from ..colour import Colour
from ..components import Container as ContainerComponent
from ..enums import ComponentType
from ..utils import copy_doc
from .item import UIComponent, ensure_ui_component

if TYPE_CHECKING:
    from typing_extensions import Self

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
    children: List[Union[:class:`~.ui.ActionRow`, :class:`~.ui.Section`, :class:`~.ui.TextDisplay`, :class:`~.ui.MediaGallery`, :class:`~.ui.File`, :class:`~.ui.Separator`]]
        The list of child components in this container.
    accent_colour: Optional[:class:`.Colour`]
        The accent colour of the container.
        An alias exists under ``accent_color``.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
        "children",
        "accent_colour",
        "spoiler",
    )

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
        self.children: List[ContainerChildUIComponent] = [
            ensure_ui_component(c, "components") for c in components
        ]
        self._accent_colour: Optional[Colour] = accent_colour
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
    def accent_colour(self) -> Optional[Colour]:
        return self._accent_colour

    @accent_colour.setter
    def accent_colour(self, value: Optional[Union[int, Colour]]) -> None:
        if isinstance(value, int):
            self._accent_colour = Colour(value)
        elif value is None or isinstance(value, Colour):
            self._accent_colour = value
        else:
            msg = f"Expected Colour, int, or None but received {type(value).__name__} instead."
            raise TypeError(msg)

    accent_color = accent_colour

    @property
    def _underlying(self) -> ContainerComponent:
        return ContainerComponent._raw_construct(
            type=ComponentType.container,
            id=self._id,
            children=[comp._underlying for comp in self.children],
            accent_colour=self._accent_colour,
            spoiler=self.spoiler,
        )

    @classmethod
    def from_component(cls, container: ContainerComponent) -> Self:
        from .action_row import _to_ui_component

        return cls(
            *cast(
                "List[ContainerChildUIComponent]",
                [_to_ui_component(c) for c in container.children],
            ),
            accent_colour=container.accent_colour,
            spoiler=container.spoiler,
            id=container.id,
        )
