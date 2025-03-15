# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Tuple, Union

from ..components import Section as SectionComponent
from ..enums import ComponentType
from ..utils import MISSING
from .button import Button
from .item import UIComponent

if TYPE_CHECKING:
    from .text_display import TextDisplay
    from .thumbnail import Thumbnail

__all__ = ("Section",)


class Section(UIComponent):
    """Represents a UI section.

    .. versionadded:: 2.11

    Parameters
    ----------
    *components: :class:`~ui.TextDisplay`
        The list of text items in this section.
    accessory: Union[:class:`~ui.Thumbnail`, :class:`~ui.Button`]
        The accessory component displayed next to the section text.
    """

    __repr_attributes__: Tuple[str, ...] = (
        "components",
        "accessory",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: SectionComponent = MISSING

    def __init__(
        self,
        *components: TextDisplay,
        accessory: Union[Thumbnail, Button],
    ) -> None:
        # TODO: this just doesn't work this way
        self._underlying = SectionComponent._raw_construct(
            type=ComponentType.section,
            components=list(components),
            accessory=accessory,
        )

    @property
    def components(self) -> Sequence[TextDisplay]:
        """Sequence[:class:`~ui.TextDisplay`]: The text items in this section."""
        # TODO: SequenceProxy?
        return self._underlying.components

    @components.setter
    def components(self, values: Sequence[TextDisplay]) -> None:
        # don't be too restrictive for easier future compatibility
        for value in values:
            if not isinstance(value, UIComponent):
                raise TypeError("TODO")
        self._underlying.components = values

    @property
    def accessory(self) -> Union[Thumbnail, Button]:
        """Union[:class:`~ui.Thumbnail`, :class:`~ui.Button`]: The accessory component displayed next to the section text."""
        return self._underlying.accessory

    @accessory.setter
    def accessory(self, value: Union[Thumbnail, Button]) -> None:
        # don't be too restrictive for easier future compatibility
        if not isinstance(value, UIComponent):
            raise TypeError("TODO")
        self._underlying.accessory = value
