"""
The MIT License (MIT)

Copyright (c) 2021-present DisnakeDev

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

import asyncio
import sys
import traceback
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union, overload

from ..components import Modal as ModalComponent
from .input_text import InputText

if TYPE_CHECKING:
    from ..interactions.modal import ModalInteraction
    from ..state import ConnectionState


__all__ = ["Modal"]


class Modal:
    """Represents a UI Modal.

    .. versionadded:: 2.4

    Parameters
    ----------
    title: str
        The title of the modal
    custom_id: str
        The custom ID of the modal.
    components: List[:class:`.ui.InputText`]
        A list of components to display in the modal. Maximum of 5.
    """

    def __init__(
        self,
        *,
        title: str,
        custom_id: str,
        components: List[InputText],  # Discord will support other components as well.
    ) -> None:
        if len(components) > 5:
            raise ValueError("maximum of components is 5.")

        for component in components:
            if not isinstance(component, InputText):
                raise TypeError(
                    f"components must be a list of InputTexts, but {component.__class__.__name__} was given."
                )

        self._underlying = ModalComponent._raw_construct(
            title=title, custom_id=custom_id, components=components
        )

    def __repr__(self) -> str:
        return f"<Modal {self.title}, custom_id={self.custom_id}, components={self.components}>"

    @property
    def title(self) -> str:
        """:class:`str`: The title of the modal."""
        return self._underlying.title

    @title.setter
    def title(self, title: str) -> None:
        self._underlying.title = title

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the modal that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, custom_id: str) -> None:
        self._underlying.custom_id = custom_id

    @property
    def components(self) -> List[InputText]:
        """List[:class:`.ui.InputText`]: A list of components the modal contains."""
        return self._underlying.components

    @overload
    def add_component(self, component: List[InputText]) -> None:
        ...

    @overload
    def add_component(self, component: InputText) -> None:
        ...

    def add_component(self, component: Union[InputText, List[InputText]]) -> None:
        """Adds a component to the modal.

        Parameters
        ----------
        component: Union[:class:`.ui.InputText`, List[:class:`.ui.InputText`]]
            The component to add to the modal.

        Raises
        ------
        ValueError
            Maximum of components exceeded. (5)
        TypeError
            An :class:`InputText` object was not passed.
        """
        if len(self.components) == 5:
            raise ValueError("maximum of components exceeded.")

        if not isinstance(component, list):
            component = [component]

        for c in component:
            if not isinstance(c, InputText):
                raise TypeError(
                    f"component must be of type InputText or a list of InputText, not {c.__class__.__name__}."
                )
            self._underlying.components.append(c)

    async def callback(self, interaction: ModalInteraction) -> None:
        """|coro|

        The callback associated with this modal.

        This can be overriden by subclasses.

        Parameters
        ----------
        interaction: :class:`ModalInteraction`
            The interaction that triggered this modal.
        """
        pass

    async def on_error(self, error: Exception, interaction: ModalInteraction) -> None:
        """|coro|

        A callback that is called when an error occurs.

        The default implementation prints the traceback to stderr.

        Parameters
        ----------
        error: :class:`Exception`
            The exception that was raised.
        interaction: :class:`ModalInteraction`
            The interaction that triggered this modal.
        """
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)

    def to_components(self) -> Dict[str, Any]:
        components: Dict[str, Any] = {
            "title": self._underlying.title,
            "custom_id": self._underlying.custom_id,
            "components": [],
        }

        for component in self._underlying.components:
            components["components"].append(
                {"type": 1, "components": [component.to_component_dict()]}
            )

        return components

    async def _scheduled_task(self, interaction: ModalInteraction) -> None:
        try:
            await self.callback(interaction)
        except Exception as e:
            await self.on_error(e, interaction)
        else:
            interaction._state._modal_store.remove_modal(
                interaction.author.id, interaction.custom_id
            )

    def dispatch(self, interaction: ModalInteraction) -> None:
        asyncio.create_task(
            self._scheduled_task(interaction), name=f"disnake-ui-modal-dispatch-{self.custom_id}"
        )


class ModalStore:
    def __init__(self, state: ConnectionState) -> None:
        self._state = state
        # (user_id, Modal.custom_id): Modal
        self._modals: Dict[Tuple[int, str], Modal] = {}

    def add_modal(self, user_id: int, modal: Modal) -> None:
        loop = asyncio.get_event_loop()
        self._modals[(user_id, modal.custom_id)] = modal
        loop.create_task(self.handle_timeout(user_id, modal.custom_id))

    def remove_modal(self, user_id: int, modal_custom_id: str) -> None:
        self._modals.pop((user_id, modal_custom_id))

    async def handle_timeout(self, user_id: int, modal_custom_id: str) -> None:
        # Waits 10 minutes and then removes the modal from cache, this is done just in case the user closed the modal,
        # as there isn't an event for that.

        # TODO: on_modal_timeout event?
        await asyncio.sleep(600)
        try:
            self.remove_modal(user_id, modal_custom_id)
        except KeyError:
            # The modal has already been removed.
            pass

    def dispatch(self, interaction: ModalInteraction) -> None:
        key = (interaction.author.id, interaction.custom_id)
        modal = self._modals.get(key)
        if modal is not None:
            modal.dispatch(interaction)
