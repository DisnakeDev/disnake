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

from typing import TYPE_CHECKING, Dict, Generator, List

from ..components import ActionRow, NestedComponent, TextInput
from ..utils import cached_slot_property
from .base import Interaction

if TYPE_CHECKING:
    from ..state import ConnectionState
    from ..types.interactions import (
        Interaction as InteractionPayload,
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
    locale: :class:`str`
        The selected language of the interaction's author.
    guild_locale: Optional[:class:`str`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.
    me: Union[:class:`.Member`, :class:`.ClientUser`]
        Similar to :attr:`.Guild.me`
    permissions: :class:`Permissions`
        The resolved permissions of the member in the channel, including overwrites.
    response: :class:`InteractionResponse`
        Returns an object responsible for handling responding to the interaction.
    followup: :class:`Webhook`
        Returns the follow up webhook for follow up interactions.
    data: :class:`ModalInteractionData`
        The wrapped interaction data.
    client: :class:`Client`
        The interaction client.
    """

    __slots__ = ("data", "_cs_text_values")

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        super().__init__(data=data, state=state)
        self.data = ModalInteractionData(data=data["data"])  # type: ignore

    def walk_components(self) -> Generator[NestedComponent, None, None]:
        """Returns a generator that yields components from action rows one by one.

        :return type: Generator[Union[:class:`Button`, :class:`SelectMenu`, :class:`TextInput`], None, None]
        """
        for action_row in self.data._components:
            yield from action_row.children

    @cached_slot_property("_cs_text_values")
    def text_values(self) -> Dict[str, str]:
        """Dict[:class:`str`, :class:`str`]: Returns the text values the user has entered in the modal.
        This is a dict of the form ``{custom_id: value}``."""
        return {
            component.custom_id: component.value or ""
            for component in self.walk_components()
            if isinstance(component, TextInput)
        }

    @property
    def custom_id(self) -> str:
        """:class:`str`: The custom ID of the modal."""
        return self.data.custom_id


class ModalInteractionData:
    """Represents the data of an interaction with a modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    custom_id: :class:`str`
        The custom ID of the modal.
    """

    __slots__ = ("custom_id", "_components")

    def __init__(self, *, data: ModalInteractionDataPayload):
        self.custom_id: str = data["custom_id"]
        # this attribute is not meant to be used since it lacks most of the component data
        self._components: List[ActionRow] = [ActionRow(d) for d in data["components"]]
