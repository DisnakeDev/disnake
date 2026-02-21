# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from ..components import GroupOption, RadioGroup as RadioGroupComponent, _parse_group_options
from ..enums import ComponentType
from ..utils import MISSING
from .item import UIComponent

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..components import GroupOptionInput

__all__ = ("RadioGroup",)


class RadioGroup(UIComponent):
    r"""Represents a UI radio group.

    .. versionadded:: |vnext|

    Parameters
    ----------
    custom_id: :class:`str`
        The ID of the radio group that gets received during an interaction.
        If not given then one is generated for you.
    options: :class:`~collections.abc.Sequence`\[:class:`.GroupOption` | :class:`str`] | :class:`dict`\[:class:`str`, :class:`str`]
        A list of options that can be selected in this group (2-10). Use explicit :class:`.GroupOption`\s
        for fine-grained control over the options. Alternatively, a list of strings will be treated
        as a list of labels, and a dict will be treated as a mapping of labels to values.
    required: :class:`bool`
        Whether the radio group is required.
        Defaults to ``True``.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within a modal.
        This is always present in components received from the API.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the modal.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = ("options", "required")
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: RadioGroupComponent = MISSING

    def __init__(
        self,
        options: GroupOptionInput,
        *,
        custom_id: str = MISSING,
        required: bool = True,
        id: int = 0,
    ) -> None:
        custom_id = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self._underlying = RadioGroupComponent._raw_construct(
            type=ComponentType.radio_group,
            id=id,
            custom_id=custom_id,
            options=_parse_group_options(options),
            required=required,
        )

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the radio group that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        self._underlying.custom_id = value

    @property
    def options(self) -> list[GroupOption]:
        r""":class:`list`\[:class:`disnake.GroupOption`]: A list of options that can be selected in this radio group."""
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
    def required(self) -> bool:
        """:class:`bool`: Whether the radio group is required."""
        return self._underlying.required

    @required.setter
    def required(self, value: bool) -> None:
        self._underlying.required = bool(value)

    @classmethod
    def from_component(cls, component: RadioGroupComponent) -> Self:
        return cls(
            options=component.options,
            custom_id=component.custom_id,
            required=component.required,
            id=component.id,
        )
