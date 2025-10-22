# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from disnake.components import Separator as SeparatorComponent
from disnake.enums import ComponentType, SeparatorSpacing
from disnake.ui.item import UIComponent
from disnake.utils import MISSING

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("Separator",)


class Separator(UIComponent):
    """Represents a UI separator.

    .. versionadded:: 2.11

    Parameters
    ----------
    divider: :class:`bool`
        Whether the separator should be visible, instead of just being vertical padding/spacing.
        Defaults to ``True``.
    spacing: :class:`.SeparatorSpacing`
        The size of the separator padding.
        Defaults to :attr:`~.SeparatorSpacing.small`.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.
    """

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        "divider",
        "spacing",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: SeparatorComponent = MISSING

    def __init__(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacing = SeparatorSpacing.small,
        id: int = 0,
    ) -> None:
        self._underlying = SeparatorComponent._raw_construct(
            type=ComponentType.separator,
            id=id,
            divider=divider,
            spacing=spacing,
        )

    @property
    def divider(self) -> bool:
        """:class:`bool`: Whether the separator should be visible, instead of just being vertical padding/spacing."""
        return self._underlying.divider

    @divider.setter
    def divider(self, value: bool) -> None:
        self._underlying.divider = value

    @property
    def spacing(self) -> SeparatorSpacing:
        """:class:`.SeparatorSpacing`: The size of the separator."""
        return self._underlying.spacing

    @spacing.setter
    def spacing(self, value: SeparatorSpacing) -> None:
        self._underlying.spacing = value

    @classmethod
    def from_component(cls, separator: SeparatorComponent) -> Self:
        return cls(
            divider=separator.divider,
            spacing=separator.spacing,
            id=separator.id,
        )
