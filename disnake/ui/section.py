# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, Sequence, Tuple, Union

from ..components import Section as SectionComponent
from ..enums import ComponentType
from ..utils import SequenceProxy
from .item import UIComponent, ensure_ui_component

if TYPE_CHECKING:
    from .button import Button
    from .text_display import TextDisplay
    from .thumbnail import Thumbnail

__all__ = ("Section",)


class Section(UIComponent):
    """Represents a UI section.

    .. versionadded:: 2.11

    Parameters
    ----------
    *components: :class:`~.ui.TextDisplay`
        The list of text items in this section.
    accessory: Union[:class:`~.ui.Thumbnail`, :class:`~.ui.Button`]
        The accessory component displayed next to the section text.
    """

    # unused, but technically required by base type
    __repr_attributes__: Tuple[str, ...] = (
        "components",
        "accessory",
    )

    # TODO: consider providing sequence operations (append, insert, remove, etc.)
    def __init__(
        self,
        *components: TextDisplay,
        accessory: Union[Thumbnail, Button],
    ) -> None:
        self._components: List[TextDisplay] = [
            ensure_ui_component(c, "components") for c in components
        ]
        self._accessory: Union[Thumbnail, Button] = ensure_ui_component(accessory, "accessory")

    # TODO: consider moving runtime checks from constructor into property setters, also making these fields writable
    @property
    def components(self) -> Sequence[TextDisplay]:
        """Sequence[:class:`~.ui.TextDisplay`]: A read-only copy of the text items in this section."""
        return SequenceProxy(self._components)

    @property
    def accessory(self) -> Union[Thumbnail, Button]:
        """Union[:class:`~.ui.Thumbnail`, :class:`~.ui.Button`]: The accessory component displayed next to the section text."""
        return self._accessory

    def __repr__(self) -> str:
        # implemented separately for now, due to SequenceProxy repr
        return f"<Section components={self._components!r} accessory={self._accessory!r}>"

    @property
    def _underlying(self) -> SectionComponent:
        return SectionComponent._raw_construct(
            type=ComponentType.section,
            components=[comp._underlying for comp in self._components],
            accessory=self._accessory._underlying,
        )
