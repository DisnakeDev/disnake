# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import ClassVar, Tuple

from ..components import TextDisplay as TextDisplayComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

__all__ = ("TextDisplay",)


# XXX: `TextDisplay` vs just `Text`
class TextDisplay(UIComponent):
    """Represents a UI text display.

    .. versionadded:: 2.11

    Parameters
    ----------
    content: :class:`str`
        The text displayed by this component.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If left unset (i.e. the default ``0``) when sending a component, the API will assign
        sequential identifiers to the components in the message.
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = ("content",)
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: TextDisplayComponent = MISSING

    def __init__(self, content: str, *, id: int = 0) -> None:
        self._underlying = TextDisplayComponent._raw_construct(
            type=ComponentType.text_display,
            id=id,
            content=content,
        )

    @property
    def content(self) -> str:
        """:class:`str`: The text displayed by this component."""
        return self._underlying.content

    @content.setter
    def content(self, value: str) -> None:
        # TODO: consider str cast?
        self._underlying.content = value
