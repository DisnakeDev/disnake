# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Tuple

from ..components import Separator as SeparatorComponent
from ..enums import ComponentType, SeparatorSpacingSize
from ..utils import MISSING
from .item import UIComponent

__all__ = ("Separator",)


class Separator(UIComponent):
    """Represents a UI separator.

    .. versionadded:: 2.11

    Parameters
    ----------
    divider: :class:`bool`
        Whether the separator should be visible, instead of just being vertical padding/spacing.
        Defaults to ``True``.
    spacing: :class:`.SeparatorSpacingSize`
        The size of the separator.
        Defaults to :attr:`~.SeparatorSpacingSize.small`.
    """

    __repr_attributes__: Tuple[str, ...] = (
        "divider",
        "spacing",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: SeparatorComponent = MISSING

    def __init__(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacingSize = SeparatorSpacingSize.small,
    ) -> None:
        self._underlying = SeparatorComponent._raw_construct(
            type=ComponentType.separator,
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
    def spacing(self) -> SeparatorSpacingSize:
        """:class:`.SeparatorSpacingSize`: The size of the separator."""
        return self._underlying.spacing

    @spacing.setter
    def spacing(self, value: SeparatorSpacingSize) -> None:
        self._underlying.spacing = value
