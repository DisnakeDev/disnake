# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from ..components import TextDisplay as TextDisplayComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("TextDisplay",)


class TextDisplay(UIComponent):
    """Represents a UI text display.

    .. versionadded:: 2.11

    Parameters
    ----------
    content: :class:`str`
        The text displayed by this component.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a message.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = ("content",)
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: TextDisplayComponent = MISSING

    def __init__(self, content: str, *, id: int = 0) -> None:
        self._underlying = TextDisplayComponent._raw_construct(
            type=ComponentType.text_display,
            id=id,
            content=str(content),
        )

    @property
    def content(self) -> str:
        """:class:`str`: The text displayed by this component."""
        return self._underlying.content

    @content.setter
    def content(self, value: str) -> None:
        self._underlying.content = str(value)

    @classmethod
    def from_component(cls, text_display: TextDisplayComponent) -> Self:
        return cls(
            content=text_display.content,
            id=text_display.id,
        )
