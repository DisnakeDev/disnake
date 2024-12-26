# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import os
import sys
import traceback
from functools import partial
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from ..enums import TextInputStyle
from ..utils import MISSING
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


class Modal:
    """Represents a UI Modal.

    .. versionadded:: 2.4

    Parameters
    ----------
    title: :class:`str`
        The title of the modal.
    components: |components_type|
        The components to display in the modal. Up to 5 action rows.
    custom_id: :class:`str`
        The custom ID of the modal. This is usually not required.
        If not given, then a unique one is generated for you.

        .. note::
            :class:`Modal`\\s are identified based on the user ID that triggered the
            modal, and this ``custom_id``.
            This can result in collisions when a user opens a modal with the same ``custom_id`` on
            two separate devices, for example.

            To avoid such issues, consider not specifying a ``custom_id`` to use an automatically generated one,
            or include a unique value in the custom ID (e.g. the original interaction ID).

    timeout: :class:`float`
        The time to wait until the modal is removed from cache, if no interaction is made.
        Modals without timeouts are not supported, since there's no event for when a modal is closed.
        Defaults to 600 seconds.
    """

    __slots__ = (
        "title",
        "custom_id",
        "components",
        "timeout",
        "__remove_callback",
        "__timeout_handle",
    )

    def __init__(
        self,
        *,
        title: str,
        components: Components[ModalUIComponent],
        custom_id: str = MISSING,
        timeout: float = 600,
    ) -> None:
        if timeout is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise ValueError("Timeout may not be None")

        rows = components_to_rows(components)
        if len(rows) > 5:
            raise ValueError("Maximum number of components exceeded.")

        self.title: str = title
        self.custom_id: str = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self.components: List[ActionRow] = rows
        self.timeout: float = timeout

        # function for the modal to remove itself from the store, if any
        self.__remove_callback: Optional[Callable[[Modal], None]] = None
        # timer handle for the scheduled timeout
        self.__timeout_handle: Optional[asyncio.TimerHandle] = None

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
            if interaction.response._response_type is None:
                # If the interaction was not successfully responded to, the modal didn't close for the user.
                # Since the timeout was already stopped at this point, restart it.
                self._start_listening(self.__remove_callback)
            else:
                # Otherwise, the modal closed for the user; remove it from the store.
                self._stop_listening()

    def _start_listening(self, remove_callback: Optional[Callable[[Modal], None]]) -> None:
        self.__remove_callback = remove_callback

        loop = asyncio.get_running_loop()
        if self.__timeout_handle is not None:
            # shouldn't get here, but handled just in case
            self.__timeout_handle.cancel()

        # start timeout
        self.__timeout_handle = loop.call_later(self.timeout, self._dispatch_timeout)

    def _stop_listening(self) -> None:
        # cancel timeout
        if self.__timeout_handle is not None:
            self.__timeout_handle.cancel()
            self.__timeout_handle = None

        # remove modal from store
        if self.__remove_callback is not None:
            self.__remove_callback(self)
            self.__remove_callback = None

    def _dispatch_timeout(self) -> None:
        self._stop_listening()
        asyncio.create_task(self.on_timeout(), name=f"disnake-ui-modal-timeout-{self.custom_id}")

    def dispatch(self, interaction: ModalInteraction) -> None:
        # stop the timeout, but don't remove the modal from the store yet in case the
        # response fails and the modal stays open
        if self.__timeout_handle is not None:
            self.__timeout_handle.cancel()

        asyncio.create_task(
            self._scheduled_task(interaction), name=f"disnake-ui-modal-dispatch-{self.custom_id}"
        )


class ModalStore:
    def __init__(self, state: ConnectionState) -> None:
        self._state = state
        # (user_id, Modal.custom_id): Modal
        self._modals: Dict[Tuple[int, str], Modal] = {}

    def add_modal(self, user_id: int, modal: Modal) -> None:
        key = (user_id, modal.custom_id)

        # if another modal with the same user+custom_id already exists,
        # stop its timeout to avoid overlaps/collisions
        if (existing := self._modals.get(key)) is not None:
            existing._stop_listening()

        # start timeout, store modal
        remove_callback = partial(self.remove_modal, user_id)
        modal._start_listening(remove_callback)
        self._modals[key] = modal

    def remove_modal(self, user_id: int, modal: Modal) -> None:
        self._modals.pop((user_id, modal.custom_id), None)

    def dispatch(self, interaction: ModalInteraction) -> None:
        key = (interaction.author.id, interaction.custom_id)
        if (modal := self._modals.get(key)) is not None:
            modal.dispatch(interaction)
