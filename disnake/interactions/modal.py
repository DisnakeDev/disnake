"""
The MIT License (MIT)

Copyright (c) 2021-present Disnake Development

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

from typing import TYPE_CHECKING, Dict, List

from .base import Interaction

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.components import ActionRow as ActionRowPayload
    from ..types.interactions import (
        Interaction as InteractionPayload,
        ModalInteractionData as ModalInteractionDataPayload,
    )

__all__ = ("ModalInteraction", "ModalInteractionData")


class ModalInteraction(Interaction):
    """Represents an Interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    data: :class:`ModalInteractionData`
        The wrapped interaction data.
    """

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        super().__init__(data=data, state=state)
        self.data = ModalInteractionData(data=data.get("data", {}))  # type: ignore

    @property
    def values(self) -> Dict[str, str]:
        """Dict[str, str]: Returns the values the user has entered in the modal.
        This is a dict of the form ``{custom_id: value}``."""
        values: Dict[str, str] = {}
        for action_row in self.data.components:
            component = action_row["components"][0]
            values[component["custom_id"]] = component["value"]  # type: ignore
        return values

    @property
    def custom_id(self) -> str:
        """:class:`str`: The custom ID of the modal."""
        return self.data.custom_id


class ModalInteractionData:
    """Represents the data of an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    custom_id: str
        The custom ID of the modal.
    components: List[:class:`ActionRow`]
        A list with the components of the modal.
    """

    __slots__ = ("custom_id", "components")

    def __init__(self, *, data: ModalInteractionDataPayload):
        self.custom_id: str = data.get("custom_id")  # type: ignore # Is the custom ID always present?
        self.components: List[ActionRowPayload] = data.get("components", [])
