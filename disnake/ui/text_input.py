# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar, Optional

from ..components import TextInput as TextInputComponent
from ..enums import ComponentType, TextInputStyle
from ..utils import MISSING, deprecated
from .item import WrappedComponent

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("TextInput",)


class TextInput(WrappedComponent):
    """Represents a UI text input.

    This can only be used in a :class:`~.ui.Modal`.

    .. versionadded:: 2.4

    Parameters
    ----------
    label: :class:`str` | :data:`None`
        The label of the text input.

        .. deprecated:: 2.11
            This is deprecated in favor of :attr:`Label.text <.ui.Label.text>` and
            :attr:`.description <.ui.Label.description>`.

    custom_id: :class:`str`
        The ID of the text input that gets received during an interaction.
        If not given then one is generated for you.
    style: :class:`.TextInputStyle`
        The style of the text input.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is entered.
    value: :class:`str` | :data:`None`
        The pre-filled value of the text input.
    required: :class:`bool`
        Whether the text input is required. Defaults to ``True``.
    min_length: :class:`int` | :data:`None`
        The minimum length of the text input.
    max_length: :class:`int` | :data:`None`
        The maximum length of the text input.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.

        .. versionadded:: 2.11
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        "style",
        "custom_id",
        "placeholder",
        "value",
        "required",
        "min_length",
        "max_length",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: TextInputComponent = MISSING

    def __init__(
        self,
        *,
        label: Optional[str] = None,
        custom_id: str = MISSING,
        style: TextInputStyle = TextInputStyle.short,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        id: int = 0,
    ) -> None:
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = TextInputComponent._raw_construct(
            type=ComponentType.text_input,
            id=id,
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
    @deprecated('ui.Label("<text>", ui.TextInput(...))')
    def label(self) -> Optional[str]:
        """:class:`str`: The label of the text input.

        .. deprecated:: 2.11
            This is deprecated in favor of :class:`.ui.Label`.
        """
        return self._underlying.label

    @label.setter
    @deprecated('ui.Label("<text>", ui.TextInput(...))')
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
        """:class:`str` | :data:`None`: The placeholder text that is shown if nothing is entered."""
        return self._underlying.placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]) -> None:
        self._underlying.placeholder = value

    @property
    def value(self) -> Optional[str]:
        """:class:`str` | :data:`None`: The pre-filled text of the text input."""
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
        """:class:`int` | :data:`None`: The minimum length of the text input."""
        return self._underlying.min_length

    @min_length.setter
    def min_length(self, value: Optional[int]) -> None:
        self._underlying.min_length = value

    @property
    def max_length(self) -> Optional[int]:
        """:class:`int` | :data:`None`: The maximum length of the text input."""
        return self._underlying.max_length

    @max_length.setter
    def max_length(self, value: Optional[int]) -> None:
        self._underlying.max_length = value

    @classmethod
    def from_component(cls, text_input: TextInputComponent) -> Self:
        return cls(
            label=text_input.label or "",
            custom_id=text_input.custom_id,
            style=text_input.style,
            placeholder=text_input.placeholder,
            value=text_input.value,
            required=text_input.required,
            min_length=text_input.min_length,
            max_length=text_input.max_length,
            id=text_input.id,
        )
