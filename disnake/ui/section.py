# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, List, Tuple, Union, cast

from ..components import Section as SectionComponent
from ..enums import ComponentType
from ..utils import copy_doc
from .item import UIComponent, ensure_ui_component
from .text_display import TextDisplay

if TYPE_CHECKING:
    from typing_extensions import Self

    from .button import Button
    from .thumbnail import Thumbnail

__all__ = ("Section",)


class Section(UIComponent):
    """Represents a UI section.

    This allows displaying an accessory (thumbnail or button) next to a block of text.

    .. versionadded:: 2.11

    Parameters
    ----------
    *components: Union[:class:`str`, :class:`~.ui.TextDisplay`]
        The text items in this section (up to 3).
    accessory: Union[:class:`~.ui.Thumbnail`, :class:`~.ui.Button`]
        The accessory component displayed next to the section text.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.

    Attributes
    ----------
    children: List[:class:`~.ui.TextDisplay`]
        The list of text items in this section.
    accessory: Union[:class:`~.ui.Thumbnail`, :class:`~.ui.Button`]
        The accessory component displayed next to the section text.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = (
        "children",
        "accessory",
    )

    def __init__(
        self,
        *components: Union[str, TextDisplay],
        accessory: Union[Thumbnail, Button[Any]],
        id: int = 0,
    ) -> None:
        self._id: int = id
        # this list can be modified without any runtime checks later on,
        # just assume the user knows what they're doing at that point
        self.children: List[TextDisplay] = [
            TextDisplay(c) if isinstance(c, str) else ensure_ui_component(c, "components")
            for c in components
        ]
        self.accessory: Union[Thumbnail, Button[Any]] = ensure_ui_component(accessory, "accessory")

    # these are reimplemented here to store the value in a separate attribute,
    # since `Section` lazily constructs `_underlying`, unlike most components
    @property
    @copy_doc(UIComponent.id)
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def _underlying(self) -> SectionComponent:
        return SectionComponent._raw_construct(
            type=ComponentType.section,
            id=self._id,
            children=[comp._underlying for comp in self.children],
            accessory=self.accessory._underlying,
        )

    @classmethod
    def from_component(cls, section: SectionComponent) -> Self:
        from .action_row import _to_ui_component

        return cls(
            *cast(
                "List[TextDisplay]",
                [_to_ui_component(c) for c in section.children],
            ),
            accessory=cast("Union[Thumbnail, Button[Any]]", _to_ui_component(section.accessory)),
            id=section.id,
        )
