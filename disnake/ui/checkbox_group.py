# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from ..components import CheckboxGroup as CheckboxGroupComponent, GroupOption
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("CheckboxGroup",)


class CheckboxGroup(UIComponent):
    r"""Represents a UI checkbox group.

    For single checkboxes, see :class:`.ui.Checkbox`.

    .. versionadded:: |vnext|

    Parameters
    ----------
    custom_id: :class:`str`
        The ID of the checkbox group that gets received during an interaction.
        If not given then one is generated for you.
    options: :class:`list`\[:class:`.GroupOption`]
        A list of options that can be selected in this group (1-10).
    min_values: :class:`int`
        The minimum number of options that must be selected in this group.
        Defaults to 1 and must be between 0 and 10.
    max_values: :class:`int`
        The maximum number of options that must be selected in this group.
        Defaults to the total number of options and must be between 1 and 10.
        TODO: revisit max_values default, this is set at instantiation which may be confusing
    required: :class:`bool`
        Whether the checkbox group is required.
        Defaults to ``True``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        "options",
        "min_values",
        "max_values",
        "required",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: CheckboxGroupComponent = MISSING

    def __init__(
        self,
        # TODO: allow list or dict, similar to StringSelect
        options: list[GroupOption],
        *,
        custom_id: str = MISSING,
        min_values: int = 1,
        max_values: int = MISSING,
        required: bool = True,
        id: int = 0,
    ) -> None:
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = CheckboxGroupComponent._raw_construct(
            type=ComponentType.checkbox_group,
            id=id,
            custom_id=custom_id,
            options=options,
            min_values=min_values,
            max_values=max_values if max_values is not MISSING else len(options),
            required=required,
        )

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the checkbox group that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        self._underlying.custom_id = value

    @property
    def options(self) -> list[GroupOption]:
        r""":class:`list`\[:class:`disnake.GroupOption`]: A list of options that can be selected in this checkbox group."""
        return self._underlying.options

    @options.setter
    def options(self, value: list[GroupOption]) -> None:
        if not isinstance(value, list):
            msg = "options must be a list of GroupOption"
            raise TypeError(msg)
        if not all(isinstance(obj, GroupOption) for obj in value):
            msg = "all list items must subclass GroupOption"
            raise TypeError(msg)

        self._underlying.options = value

    @property
    def min_values(self) -> int:
        """:class:`int`: The minimum number of options that must be selected in this group."""
        return self._underlying.min_values

    @min_values.setter
    def min_values(self, value: int) -> None:
        self._underlying.min_values = int(value)

    @property
    def max_values(self) -> int:
        """:class:`int`: The maximum number of options that must be selected in this group."""
        return self._underlying.max_values

    @max_values.setter
    def max_values(self, value: int) -> None:
        self._underlying.max_values = int(value)

    @property
    def required(self) -> bool:
        """:class:`bool`: Whether the checkbox group is required."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool) -> None:
        self._underlying.required = bool(value)

    @classmethod
    def from_component(cls, component: CheckboxGroupComponent) -> Self:
        return cls(
            options=component.options,
            custom_id=component.custom_id,
            min_values=component.min_values,
            max_values=component.max_values,
            required=component.required,
            id=component.id,
        )
