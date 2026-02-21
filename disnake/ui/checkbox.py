# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from ..components import Checkbox as CheckboxComponent
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("Checkbox",)


class Checkbox(UIComponent):
    r"""Represents a UI checkbox.

    For a group of multiple checkboxes, see :class:`.ui.CheckboxGroup`.

    .. versionadded:: |vnext|

    Parameters
    ----------
    custom_id: :class:`str`
        The ID of the checkbox that gets received during an interaction.
        If not given then one is generated for you.
    default: :class:`bool`
        Whether this checkbox is selected by default.
        Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = ("default",)
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: CheckboxComponent = MISSING

    def __init__(
        self,
        *,
        custom_id: str = MISSING,
        default: bool = False,
        id: int = 0,
    ) -> None:
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = CheckboxComponent._raw_construct(
            type=ComponentType.checkbox,
            id=id,
            custom_id=custom_id,
            default=default,
        )

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the checkbox that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        self._underlying.custom_id = value

    @property
    def default(self) -> bool:
        """:class:`bool`: Whether this checkbox is selected by default."""
        return self._underlying.default

    @default.setter
    def default(self, value: bool) -> None:
        self._underlying.default = bool(value)

    @classmethod
    def from_component(cls, component: CheckboxComponent) -> Self:
        return cls(
            custom_id=component.custom_id,
            default=component.default,
            id=component.id,
        )
