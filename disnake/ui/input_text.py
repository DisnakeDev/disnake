"""
The MIT License (MIT)

Copyright (c) 2021-present DisnakeDev

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from ..components import InputText as InputTextComponent
from ..enums import ComponentType, InputTextStyle
from .item import WrappedComponent

if TYPE_CHECKING:
    from ..types.components import InputText as InputTextPayload


__all__ = ("InputText",)


class InputText(WrappedComponent):
    """Represents a UI input text.

    This can only be used in :class:`~.ui.Modal`.

    .. versionadded:: 2.4

    Parameters
    ----------
    label: :class:`str`
        The label of the input text.
    custom_id: :class:`str`
        The ID of the input text that gets received during an interaction.
    style: :class:`.InputTextStyle`
        The style of the input text.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is entered.
    value: Optional[:class:`str`]
        The pre-filled value of the input text.
    required: :class:`bool`
        Whether the input text is required. Defaults to ``True``.
    min_length: :class:`int`
        The minimum length of the input text. Defaults to ``0``.
    max_length: Optional[:class:`int`]
        The maximum length of the input text.
    """

    __repr_attributes__: Tuple[str, ...] = (
        "style",
        "label",
        "custom_id",
        "placeholder",
        "value",
        "required",
        "min_length",
        "max_length",
    )

    def __init__(
        self,
        *,
        label: str,
        custom_id: str,
        style: InputTextStyle = InputTextStyle.short,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        required: bool = True,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ) -> None:
        self._underlying = InputTextComponent._raw_construct(
            type=ComponentType.input_text,
            style=style,
            label=label,
            custom_id=custom_id,
            placeholder=placeholder,
            value=value,
            required=required,
            min_length=min_length,
            max_length=max_length,
        )

    @property
    def width(self) -> int:
        return 5

    @property
    def type(self) -> ComponentType:
        """:class:`.ComponentType`: The type of the input text. This is always :attr:`.ComponentType.input_text`."""
        return self._underlying.type

    @property
    def style(self) -> InputTextStyle:
        """:class:`.InputTextStyle`: The style of the input text."""
        return self._underlying.style

    @style.setter
    def style(self, value: InputTextStyle) -> None:
        self._underlying.style = value

    @property
    def label(self) -> str:
        """:class:`str`: The label of the input text."""
        return self._underlying.label  # type: ignore

    @label.setter
    def label(self, value: str) -> None:
        self._underlying.label = value

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the input text that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        self._underlying.custom_id = value

    @property
    def placeholder(self) -> Optional[str]:
        """Optional[:class:`str`]: The placeholder text that is shown if nothing is entered."""
        return self._underlying.placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]) -> None:
        self._underlying.placeholder = value

    @property
    def value(self) -> Optional[str]:
        """Optional[:class:`str`]: The pre-filled text of the input text."""
        return self._underlying.value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self._underlying.value = value

    @property
    def required(self) -> bool:
        """:class:`bool`: Whether the input text is required."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool) -> None:
        self._underlying.required = value

    @property
    def min_length(self) -> int:
        """:class:`int`: The minimum length of the input text."""
        return self._underlying.min_length

    @min_length.setter
    def min_length(self, value: int) -> None:
        self._underlying.min_length = value

    @property
    def max_length(self) -> Optional[int]:
        """Optional[:class:`int`]: The maximum length of the input text."""
        return self._underlying.max_length

    @max_length.setter
    def max_length(self, value: Optional[int]) -> None:
        self._underlying.max_length = value

    def to_component_dict(self) -> InputTextPayload:
        return self._underlying.to_dict()
