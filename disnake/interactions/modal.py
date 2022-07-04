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

from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional

from ..enums import ComponentType
from ..message import Message
from ..utils import cached_slot_property
from .base import Interaction

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.interactions import (
        ModalInteraction as ModalInteractionPayload,
        ModalInteractionActionRow as ModalInteractionActionRowPayload,
        ModalInteractionComponentData as ModalInteractionComponentDataPayload,
        ModalInteractionData as ModalInteractionDataPayload,
    )

__all__ = ("ModalInteraction", "ModalInteractionData")


class ModalInteraction(Interaction):
    """Represents an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    application_id: :class:`int`
        The application ID that the interaction was for.
    token: :class:`str`
        The token to continue the interaction.
        These are valid for 15 minutes.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel_id: :class:`int`
        The channel ID the interaction was sent from.
    author: Union[:class:`User`, :class:`Member`]
        The user or member that sent the interaction.
    locale: :class:`Locale`
        The selected language of the interaction's author.

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    guild_locale: Optional[:class:`Locale`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    message: Optional[:class:`Message`]
        The message that this interaction's modal originated from,
        if the modal was sent in response to a component interaction.

        .. versionadded:: 2.5

    data: :class:`ModalInteractionData`
        The wrapped interaction data.
    client: :class:`Client`
        The interaction client.
    """

    __slots__ = (
        "data",
        "message",
        "_cs_text_values",
        "_cs_select_values",
    )

    def __init__(self, *, data: ModalInteractionPayload, state: ConnectionState):
        super().__init__(data=data, state=state)
        self.data = ModalInteractionData(data=data["data"])

        if message_data := data.get("message"):
            message = Message(state=self._state, channel=self.channel, data=message_data)
        else:
            message = None
        self.message: Optional[Message] = message

    def walk_raw_components(self) -> Generator[ModalInteractionComponentDataPayload, None, None]:
        """
        Returns a generator that yields raw component data from action rows one by one, as provided by Discord.
        This does not contain all fields of the components due to API limitations.

        .. versionadded:: 2.6

        Returns
        -------
        Generator[:class:`dict`, None, None]
        """
        for action_row in self.data.components:
            yield from action_row["components"]

    @cached_slot_property("_cs_text_values")
    def text_values(self) -> Dict[str, str]:
        """Dict[:class:`str`, :class:`str`]: Returns the text values the user has entered in the modal.
        This is a dict of the form ``{custom_id: value, ...}``."""
        text_input_type = ComponentType.text_input.value
        return {
            component["custom_id"]: component.get("value") or ""
            for component in self.walk_raw_components()
            if component.get("type") == text_input_type
        }

    @cached_slot_property("_cs_select_values")
    def select_values(self) -> Dict[str, List[str]]:
        """Dict[:class:`str`, List[:class:`str`]]: Returns the select values the user has entered in the modal.
        This is a dict of the form ``{custom_id: [value1, value2, ...], ...}``.

        .. versionadded:: 2.6
        """
        select_type = ComponentType.select.value
        return {
            component["custom_id"]: component.get("values") or []
            for component in self.walk_raw_components()
            if component.get("type") == select_type
        }

    @property
    def custom_id(self) -> str:
        """:class:`str`: The custom ID of the modal."""
        return self.data.custom_id


class ModalInteractionData(Dict[str, Any]):
    """Represents the data of an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    custom_id: :class:`str`
        The custom ID of the modal.
    components: List[:class:`dict`]
        The raw component data of the modal interaction, as provided by Discord.
        This does not contain all fields of the components due to API limitations.

        .. versionadded:: 2.6
    """

    __slots__ = ("custom_id", "components")

    def __init__(self, *, data: ModalInteractionDataPayload):
        super().__init__(data)
        self.custom_id: str = data["custom_id"]
        # This uses a stripped-down action row TypedDict, as we only receive
        # partial data from the API, generally only containing `type`, `custom_id`,
        # and relevant fields like a select's `values`.
        self.components: List[ModalInteractionActionRowPayload] = data["components"]

    def __repr__(self):
        return f"<ModalInteractionData custom_id={self.custom_id!r} components={self.components!r}>"
