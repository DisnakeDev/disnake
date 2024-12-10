# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import os
import sys
import traceback
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypeVar, Union, Type

from ..enums import TextInputStyle
from .action_row import ActionRow, components_to_rows
from .text_input import TextInput

if TYPE_CHECKING:
    from ..client import Client
    from ..interactions.modal import ModalInteraction
    from ..state import ConnectionState
    from ..types.components import Modal as ModalPayload
    from .action_row import Components, ModalUIComponent


__all__ = ("Modal",)


ClientT = TypeVar("ClientT", bound="Client")



class ModalMeta(type):
    """A metaclass for defining a modal"""
    
    def __new__(cls: Type[ModalMeta], *args: Any, **kwargs: Any) -> ModalMeta:
        name, bases, attrs = args
        if not bases:
            return super().__new__(cls, name, bases, attrs)
        
        components: Components[ModalUIComponent] = []
        for value in attrs.values():
            if isinstance(value, TextInput):
                components.append(value)
                
        if not components:
            raise TypeError(f"No text inputs found for class {name}")
        
        rows: List[ActionRow] = components_to_rows(components)
        if len(rows) > 5:
            raise ValueError("Maximum number of components exceeded. Max components - 5")
        
        attrs.update({"components": rows})
        return super().__new__(cls, name, bases, attrs)



class Modal(metaclass=ModalMeta):
    """Represents a UI Modal.

    Parameters
    ----------
    __title__: :class:`str`
        The title of the modal.
    __custom_id__: :class:`str`
        The custom ID of the modal.
    __timeout__: :class:`float`
        The time to wait until the modal is removed from cache, if no interaction is made.
        Modals without timeouts are not supported, since there's no event for when a modal is closed.
        Defaults to 600 seconds.
        
    Example:
        class MyModal(disnake.ui.Modal):
            __title__ = "Register"
            __custom_id__ = "register-modal"
            __timeout__ = 100
                
            username = TextInput(
                label="Username",
                custom_id="username"
            )
            email = TextInput(
                label="Email",
                custom_id="email"
            )
            age = TextInput(
                label="Age",
                custom_id="age",
                required=False
            )
    """
    __title__: str
    __custom_id__: str
    __timeout__: float
    
    __slots__ = ("title", "custom_id", "components", "timeout")

    def __init__(self) -> None:
        modal_dict = self.__class__.__dict__
        
        self.title: Union[str, None] = modal_dict.get("__title__")
        self.custom_id: Union[str, None] = modal_dict.get("__custom_id__")
        self.timeout: Union[float, None] = modal_dict.get("__timeout__")
        self.components: Union[List[ActionRow], None] = modal_dict.get("components")
        
        if self.title is None:
            raise TypeError("Missing required argument __title__")
        
        if self.custom_id is None:
            self.custom_id = os.urandom(16).hex()
            
        if self.timeout is None:
            self.timeout = 600
        
    def __repr__(self) -> str:
        return (
            f"<Modal custom_id={self.custom_id!r} title={self.title!r} "
            f"components={self.components!r}>"
        )

    def append_component(self, component: Union[TextInput, List[TextInput]]) -> None:
        """Adds one or multiple component(s) to the modal.

        Parameters
        ----------
        component: Union[:class:`~.ui.TextInput`, List[:class:`~.ui.TextInput`]]
            The component(s) to add to the modal.
            This can be a single component or a list of components.

        Raises
        ------
        ValueError
            Maximum number of components (5) exceeded.
        TypeError
            An object of type :class:`TextInput` was not passed.
        """
        if len(self.components) >= 5:
            raise ValueError("Maximum number of components exceeded.")

        if not isinstance(component, list):
            component = [component]

        for c in component:
            if not isinstance(c, TextInput):
                raise TypeError(
                    f"component must be of type 'TextInput' or a list of 'TextInput' objects, not {type(c).__name__}."
                )
            try:
                self.components[-1].append_item(c)
            except (ValueError, IndexError):
                self.components.append(ActionRow(c))

    def add_text_input(
        self,
        *,
        label: str,
        custom_id: str,
        style: TextInputStyle = TextInputStyle.short,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> None:
        """Creates and adds a text input component to the modal.

        To append a pre-existing instance of :class:`~disnake.ui.TextInput` use the
        :meth:`append_component` method.

        Parameters
        ----------
        label: :class:`str`
            The label of the text input.
        custom_id: :class:`str`
            The ID of the text input that gets received during an interaction.
        style: :class:`.TextInputStyle`
            The style of the text input.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is entered.
        value: Optional[:class:`str`]
            The pre-filled value of the text input.
        required: :class:`bool`
            Whether the text input is required. Defaults to ``True``.
        min_length: Optional[:class:`int`]
            The minimum length of the text input.
        max_length: Optional[:class:`int`]
            The maximum length of the text input.

        Raises
        ------
        ValueError
            Maximum number of components (5) exceeded.
        """
        self.append_component(
            TextInput(
                label=label,
                custom_id=custom_id,
                style=style,
                placeholder=placeholder,
                value=value,
                required=required,
                min_length=min_length,
                max_length=max_length,
            )
        )

    async def callback(self, interaction: ModalInteraction[ClientT], /) -> None:
        """|coro|

        The callback associated with this modal.

        This can be overriden by subclasses.

        Parameters
        ----------
        interaction: :class:`.ModalInteraction`
            The interaction that triggered this modal.
        """
        pass

    async def on_error(self, error: Exception, interaction: ModalInteraction[ClientT]) -> None:
        """|coro|

        A callback that is called when an error occurs.

        The default implementation prints the traceback to stderr.

        Parameters
        ----------
        error: :class:`Exception`
            The exception that was raised.
        interaction: :class:`.ModalInteraction`
            The interaction that triggered this modal.
        """
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)

    async def on_timeout(self) -> None:
        """|coro|

        A callback that is called when the modal is removed from the cache
        without an interaction being made.
        """
        pass
    

    def to_components(self) -> ModalPayload:
        payload: ModalPayload = {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": [component.to_component_dict() for component in self.components],
        }
        return payload

    async def _scheduled_task(self, interaction: ModalInteraction) -> None:
        try:
            await self.callback(interaction)
        except Exception as e:
            await self.on_error(e, interaction)
        finally:
            # if the interaction was responded to (no matter if in the callback or error handler),
            # the modal closed for the user and therefore can be removed from the store
            if interaction.response._response_type is not None:
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
        loop = asyncio.get_running_loop()
        self._modals[(user_id, modal.custom_id)] = modal
        loop.create_task(self.handle_timeout(user_id, modal.custom_id, modal.timeout))

    def remove_modal(self, user_id: int, modal_custom_id: str) -> Modal:
        return self._modals.pop((user_id, modal_custom_id))

    async def handle_timeout(self, user_id: int, modal_custom_id: str, timeout: float) -> None:
        # Waits for the timeout and then removes the modal from cache, this is done just in case
        # the user closed the modal, as there isn't an event for that.

        await asyncio.sleep(timeout)
        try:
            modal = self.remove_modal(user_id, modal_custom_id)
        except KeyError:
            # The modal has already been removed.
            pass
        else:
            await modal.on_timeout()

    def dispatch(self, interaction: ModalInteraction) -> None:
        key = (interaction.author.id, interaction.custom_id)
        modal = self._modals.get(key)
        if modal is not None:
            modal.dispatch(interaction)
