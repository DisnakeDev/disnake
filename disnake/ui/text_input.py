# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional, Tuple

from ..components import TextInput as TextInputComponent
from ..enums import ComponentType, TextInputStyle
from ..utils import MISSING
from .item import WrappedComponent

__all__ = ("TextInput",)


class TextInput(WrappedComponent):
    """Represents a UI text input.

    This can only be used in a :class:`~.ui.Modal`.

    .. versionadded:: 2.4

    Parameters
    ----------
    label: :class:`str`
        The label of the text input.
    custom_id: :class:`str`
        The ID of the text input that gets received during an interaction.
    style: :class:`.TextInputStyle`
        The style of the text input.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is entered.
    value: Optional[:class:`str`]
        The pre-filled value of the text input.
    required: :class:`bool`
        Whether the text input is required. Defaults to ``True``.
    min_length: Optional[:class:`int`]
        The minimum length of the text input.
    max_length: Optional[:class:`int`]
        The maximum length of the text input.
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
    # We have to set this to MISSING in order to overwrite the abstract property from WrappedComponent
    _underlying: TextInputComponent = MISSING

    def __init__(
        self,
        *,
        label: str,
        custom_id: str,
        style: TextInputStyle = TextInputStyle.short,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> None:
        self._underlying = TextInputComponent._raw_construct(
            type=ComponentType.text_input,
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
    def style(self) -> TextInputStyle:
        """:class:`.TextInputStyle`: The style of the text input."""
        return self._underlying.style

    @style.setter
    def style(self, value: TextInputStyle) -> None:
        self._underlying.style = value

    @property
    def label(self) -> str:
        """:class:`str`: The label of the text input."""
        return self._underlying.label  # type: ignore

    @label.setter
    def label(self, value: str) -> None:
        self._underlying.label = value

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the text input that gets received during an interaction."""
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
        """Optional[:class:`str`]: The pre-filled text of the text input."""
        return self._underlying.value

    @value.setter
    def value(self, value: Optional[str]) -> None:
        self._underlying.value = value

    @property
    def required(self) -> bool:
        """:class:`bool`: Whether the text input is required."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool) -> None:
        self._underlying.required = value

    @property
    def min_length(self) -> Optional[int]:
        """Optional[:class:`int`]: The minimum length of the text input."""
        return self._underlying.min_length

    @min_length.setter
    def min_length(self, value: Optional[int]) -> None:
        self._underlying.min_length = value

    @property
    def max_length(self) -> Optional[int]:
        """Optional[:class:`int`]: The maximum length of the text input."""
        return self._underlying.max_length

    @max_length.setter
    def max_length(self, value: Optional[int]) -> None:
        self._underlying.max_length = value
