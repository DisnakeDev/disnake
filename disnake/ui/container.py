# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional, Union, cast

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
    *components: :class:`~.ui.ActionRow` | :class:`~.ui.Section` | :class:`~.ui.TextDisplay` | :class:`~.ui.MediaGallery` | :class:`~.ui.File` | :class:`~.ui.Separator`
        The components in this container.
    accent_colour: :class:`.Colour` | :data:`None`
        The accent colour of the container.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler. Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.

    Attributes
    ----------
    children: :class:`list`\\[:class:`~.ui.ActionRow` | :class:`~.ui.Section` | :class:`~.ui.TextDisplay` | :class:`~.ui.MediaGallery` | :class:`~.ui.File` | :class:`~.ui.Separator`]
        The list of child components in this container.
    accent_colour: :class:`.Colour` | :data:`None`
        The accent colour of the container.
        An alias exists under ``accent_color``.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
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
        self.children: list[ContainerChildUIComponent] = [
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
                "list[ContainerChildUIComponent]",
                [_to_ui_component(c) for c in container.children],
            ),
            accent_colour=container.accent_colour,
            spoiler=container.spoiler,
            id=container.id,
        )

    def add_item(self, component: ContainerChildUIComponent) -> Self:
        """Adds a component to the container.

        This function returns the class instance to allow for fluent-style chaining.

        Parameters
        ----------
        component: :class:`~.ui.ActionRow` | :class:`~.ui.Section` | :class:`~.ui.TextDisplay` | :class:`~.ui.MediaGallery` | :class:`~.ui.File` | :class:`~.ui.Separator`
            The component to add to the container.

        Raises
        ------
        TypeError
            Raised if the component is not a valid UI component type.
        ValueError
            Raised if adding the component would exceed Discord's limits or the container is full.
        """
        total = 0
        for child in self.children:
            # If the child is a Section or Container, iterate its children
            if hasattr(child, "children") and isinstance(child.children, list):
                for b in child.children:
                    total += 1  # the child itself
                    # Check for accessory inside Section
                    if hasattr(b, "accessory") and b.accessory is not None:
                        total += 1
                    elif hasattr(child, "accessory") and child.accessory is not None:
                        total += 2  # double count as it's a child with an accessory
                    elif ensure_ui_component(b, "components"):
                        total += 1
                    else:
                        # Fallback for safey
                        total += 1
        if total >= 40:
            msg = f"Container cannot have more than 40 ContainerChildUIComponents. There were {total} ContainerChildUIComponents in {len(self.children)} components."
            raise ValueError(msg)

        self.children.append(ensure_ui_component(component, "components"))
        return self

    def remove_item(self, component: ContainerChildUIComponent) -> Self:
        """Removes a component from the container.

        This function returns the class instance to allow for fluent-style chaining.

        Parameters
        ----------
        component: :class:`~.ui.ActionRow` | :class:`~.ui.Section` | :class:`~.ui.TextDisplay` | :class:`~.ui.MediaGallery` | :class:`~.ui.File` | :class:`~.ui.Separator`
            The component to remove from the container.

        Raises
        ------
        ValueError
            Raised if the component is not found in the container.
        """
        try:
            self.children.remove(component)
        except ValueError:
            pass  # silently pass like in ui.View.remove_item
        return self

    def clear_items(self) -> Self:
        """Clears all components from the container.

        This function returns the class instance to allow for fluent-style chaining.
        """
        try:
            self.children.clear()
        except ValueError:
            pass  # silently pass like in ui.View.remove_item
        return self
