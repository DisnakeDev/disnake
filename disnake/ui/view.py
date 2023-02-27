# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import os
import sys
import time
import traceback
from functools import partial
from itertools import groupby
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)

from ..components import (
    ActionRow as ActionRowComponent,
    Button as ButtonComponent,
    ChannelSelectMenu as ChannelSelectComponent,
    MentionableSelectMenu as MentionableSelectComponent,
    MessageComponent,
    RoleSelectMenu as RoleSelectComponent,
    StringSelectMenu as StringSelectComponent,
    UserSelectMenu as UserSelectComponent,
    _component_factory,
)
from ..enums import ComponentType, try_enum_to_int
from ..utils import assert_never
from .item import Item

__all__ = ("View",)


if TYPE_CHECKING:
    from typing_extensions import Self

    from ..interactions import MessageInteraction
    from ..message import Message
    from ..state import ConnectionState
    from ..types.components import ActionRow as ActionRowPayload, Component as ComponentPayload
    from .item import ItemCallbackType


def _walk_all_components(
    components: List[ActionRowComponent[MessageComponent]],
) -> Iterator[MessageComponent]:
    for item in components:
        yield from item.children


def _component_to_item(component: MessageComponent) -> Item:
    if isinstance(component, ButtonComponent):
        from .button import Button

        return Button.from_component(component)
    if isinstance(component, StringSelectComponent):
        from .select import StringSelect

        return StringSelect.from_component(component)
    if isinstance(component, UserSelectComponent):
        from .select import UserSelect

        return UserSelect.from_component(component)
    if isinstance(component, RoleSelectComponent):
        from .select import RoleSelect

        return RoleSelect.from_component(component)
    if isinstance(component, MentionableSelectComponent):
        from .select import MentionableSelect

        return MentionableSelect.from_component(component)
    if isinstance(component, ChannelSelectComponent):
        from .select import ChannelSelect

        return ChannelSelect.from_component(component)

    assert_never(component)
    return Item.from_component(component)


class _ViewWeights:
    __slots__ = ("weights",)

    def __init__(self, children: List[Item]) -> None:
        self.weights: List[int] = [0, 0, 0, 0, 0]

        key: Callable[[Item[View]], int] = lambda i: sys.maxsize if i.row is None else i.row
        children = sorted(children, key=key)
        for _, group in groupby(children, key=key):
            for item in group:
                self.add_item(item)

    def find_open_space(self, item: Item) -> int:
        for index, weight in enumerate(self.weights):
            if weight + item.width <= 5:
                return index

        raise ValueError("could not find open space for item")

    def add_item(self, item: Item) -> None:
        if item.row is not None:
            total = self.weights[item.row] + item.width
            if total > 5:
                raise ValueError(f"item would not fit at row {item.row} ({total} > 5 width)")
            self.weights[item.row] = total
            item._rendered_row = item.row
        else:
            index = self.find_open_space(item)
            self.weights[index] += item.width
            item._rendered_row = index

    def remove_item(self, item: Item) -> None:
        if item._rendered_row is not None:
            self.weights[item._rendered_row] -= item.width
            item._rendered_row = None

    def clear(self) -> None:
        self.weights = [0, 0, 0, 0, 0]


class View:
    """Represents a UI view.

    This object must be inherited to create a UI within Discord.

    Alternatively, components can be handled with :class:`disnake.ui.ActionRow`\\s and event
    listeners for a more low-level approach. Relevant events are :func:`disnake.on_button_click`,
    :func:`disnake.on_dropdown`, and the more generic :func:`disnake.on_message_interaction`.

    .. versionadded:: 2.0

    Parameters
    ----------
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.

    Attributes
    ----------
    timeout: Optional[:class:`float`]
        Timeout from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    children: List[:class:`Item`]
        The list of children attached to this view.
    """

    __discord_ui_view__: ClassVar[bool] = True
    __view_children_items__: ClassVar[List[ItemCallbackType[Item]]] = []

    def __init_subclass__(cls) -> None:
        children: List[ItemCallbackType[Item]] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    children.append(member)

        if len(children) > 25:
            raise TypeError("View cannot have more than 25 children")

        cls.__view_children_items__ = children

    def __init__(self, *, timeout: Optional[float] = 180.0) -> None:
        self.timeout = timeout
        self.children: List[Item] = []
        for func in self.__view_children_items__:
            item: Item = func.__discord_ui_model_type__(**func.__discord_ui_model_kwargs__)
            item.callback = partial(func, self, item)
            item._view = self
            setattr(self, func.__name__, item)
            self.children.append(item)

        self.__weights = _ViewWeights(self.children)
        loop = asyncio.get_running_loop()
        self.id: str = os.urandom(16).hex()
        self.__cancel_callback: Optional[Callable[[View], None]] = None
        self.__timeout_expiry: Optional[float] = None
        self.__timeout_task: Optional[asyncio.Task[None]] = None
        self.__stopped: asyncio.Future[bool] = loop.create_future()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} timeout={self.timeout} children={len(self.children)}>"

    async def __timeout_task_impl(self) -> None:
        while True:
            # Guard just in case someone changes the value of the timeout at runtime
            if self.timeout is None:
                return

            if self.__timeout_expiry is None:
                return self._dispatch_timeout()

            # Check if we've elapsed our currently set timeout
            now = time.monotonic()
            if now >= self.__timeout_expiry:
                return self._dispatch_timeout()

            # Wait N seconds to see if timeout data has been refreshed
            await asyncio.sleep(self.__timeout_expiry - now)

    def to_components(self) -> List[ActionRowPayload]:
        def key(item: Item) -> int:
            return item._rendered_row or 0

        children = sorted(self.children, key=key)
        components: List[ActionRowPayload] = []
        for _, group in groupby(children, key=key):
            children = [item.to_component_dict() for item in group]
            if not children:
                continue

            components.append(
                {
                    "type": 1,
                    "components": children,
                }
            )

        return components

    @classmethod
    def from_message(cls, message: Message, /, *, timeout: Optional[float] = 180.0) -> View:
        """Converts a message's components into a :class:`View`.

        The :attr:`.Message.components` of a message are read-only
        and separate types from those in the ``disnake.ui`` namespace.
        In order to modify and edit message components they must be
        converted into a :class:`View` first.

        Parameters
        ----------
        message: :class:`disnake.Message`
            The message with components to convert into a view.
        timeout: Optional[:class:`float`]
            The timeout of the converted view.

        Returns
        -------
        :class:`View`
            The converted view. This always returns a :class:`View` and not
            one of its subclasses.
        """
        view = View(timeout=timeout)
        for component in _walk_all_components(message.components):
            view.add_item(_component_to_item(component))
        return view

    @property
    def _expires_at(self) -> Optional[float]:
        if self.timeout:
            return time.monotonic() + self.timeout
        return None

    def add_item(self, item: Item) -> Self:
        """Adds an item to the view.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        item: :class:`Item`
            The item to add to the view.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        ValueError
            Maximum number of children has been exceeded (25)
            or the row the item is trying to be added to is full.
        """
        if len(self.children) > 25:
            raise ValueError("maximum number of children exceeded")

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")

        self.__weights.add_item(item)

        item._view = self
        self.children.append(item)
        return self

    def remove_item(self, item: Item) -> Self:
        """Removes an item from the view.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        item: :class:`Item`
            The item to remove from the view.
        """
        try:
            self.children.remove(item)
        except ValueError:
            pass
        else:
            self.__weights.remove_item(item)
        return self

    def clear_items(self) -> Self:
        """Removes all items from the view.

        This function returns the class instance to allow for fluent-style
        chaining.
        """
        self.children.clear()
        self.__weights.clear()
        return self

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        """|coro|

        A callback that is called when an interaction happens within the view
        that checks whether the view should process item callbacks for the interaction.

        This is useful to override if, for example, you want to ensure that the
        interaction author is a given user.

        The default implementation of this returns ``True``.

        .. note::

            If an exception occurs within the body then the check
            is considered a failure and :meth:`on_error` is called.

        Parameters
        ----------
        interaction: :class:`.MessageInteraction`
            The interaction that occurred.

        Returns
        -------
        :class:`bool`
            Whether the view children's callbacks should be called.
        """
        return True

    async def on_timeout(self) -> None:
        """|coro|

        A callback that is called when a view's timeout elapses without being explicitly stopped.
        """
        pass

    async def on_error(self, error: Exception, item: Item, interaction: MessageInteraction) -> None:
        """|coro|

        A callback that is called when an item's callback or :meth:`interaction_check`
        fails with an error.

        The default implementation prints the traceback to stderr.

        Parameters
        ----------
        error: :class:`Exception`
            The exception that was raised.
        item: :class:`Item`
            The item that failed the dispatch.
        interaction: :class:`.MessageInteraction`
            The interaction that led to the failure.
        """
        print(f"Ignoring exception in view {self} for item {item}:", file=sys.stderr)
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)

    async def _scheduled_task(self, item: Item, interaction: MessageInteraction):
        try:
            if self.timeout:
                self.__timeout_expiry = time.monotonic() + self.timeout

            allow = await self.interaction_check(interaction)
            if not allow:
                return

            await item.callback(interaction)
        except Exception as e:
            return await self.on_error(e, item, interaction)

    def _start_listening_from_store(self, store: ViewStore) -> None:
        self.__cancel_callback = partial(store.remove_view)
        if self.timeout:
            loop = asyncio.get_running_loop()
            if self.__timeout_task is not None:
                self.__timeout_task.cancel()

            self.__timeout_expiry = time.monotonic() + self.timeout
            self.__timeout_task = loop.create_task(self.__timeout_task_impl())

    def _dispatch_timeout(self) -> None:
        if self.__stopped.done():
            return

        self.__stopped.set_result(True)
        asyncio.create_task(self.on_timeout(), name=f"disnake-ui-view-timeout-{self.id}")

    def _dispatch_item(self, item: Item, interaction: MessageInteraction) -> None:
        if self.__stopped.done():
            return

        asyncio.create_task(
            self._scheduled_task(item, interaction), name=f"disnake-ui-view-dispatch-{self.id}"
        )

    def refresh(self, components: List[ActionRowComponent[MessageComponent]]) -> None:
        # TODO: this is pretty hacky at the moment
        old_state: Dict[Tuple[int, str], Item] = {
            (item.type.value, item.custom_id): item  # type: ignore
            for item in self.children
            if item.is_dispatchable()
        }
        children: List[Item] = []
        for component in _walk_all_components(components):
            older: Optional[Item] = None
            try:
                older = old_state[(component.type.value, component.custom_id)]  # type: ignore
            except (KeyError, AttributeError):
                # workaround for url buttons, since they're not part of `old_state`
                if isinstance(component, ButtonComponent):
                    for child in self.children:
                        if (
                            child.type is ComponentType.button
                            and child.label == component.label  # type: ignore
                            and child.url == component.url  # type: ignore
                        ):
                            older = child
                            break

            if older:
                older.refresh_component(component)
                children.append(older)
            else:
                children.append(_component_to_item(component))

        self.children = children

    def stop(self) -> None:
        """Stops listening to interaction events from this view.

        This operation cannot be undone.
        """
        if not self.__stopped.done():
            self.__stopped.set_result(False)

        self.__timeout_expiry = None
        if self.__timeout_task is not None:
            self.__timeout_task.cancel()
            self.__timeout_task = None

        if self.__cancel_callback:
            self.__cancel_callback(self)
            self.__cancel_callback = None

    def is_finished(self) -> bool:
        """Whether the view has finished interacting.

        :return type: :class:`bool`
        """
        return self.__stopped.done()

    def is_dispatching(self) -> bool:
        """Whether the view has been added for dispatching purposes.

        :return type: :class:`bool`
        """
        return self.__cancel_callback is not None

    def is_persistent(self) -> bool:
        """Whether the view is set up as persistent.

        A persistent view has all their components with a set ``custom_id`` and
        a :attr:`timeout` set to ``None``.

        :return type: :class:`bool`
        """
        return self.timeout is None and all(item.is_persistent() for item in self.children)

    async def wait(self) -> bool:
        """Waits until the view has finished interacting.

        A view is considered finished when :meth:`stop` is called
        or it times out.

        Returns
        -------
        :class:`bool`
            If ``True``, then the view timed out. If ``False`` then
            the view finished normally.
        """
        return await self.__stopped


class ViewStore:
    def __init__(self, state: ConnectionState) -> None:
        # (component_type, message_id, custom_id): (View, Item)
        self._views: Dict[Tuple[int, Optional[int], str], Tuple[View, Item]] = {}
        # message_id: View
        self._synced_message_views: Dict[int, View] = {}
        self._state: ConnectionState = state

    @property
    def persistent_views(self) -> Sequence[View]:
        views = {view.id: view for view, _ in self._views.values() if view.is_persistent()}
        return list(views.values())

    def __verify_integrity(self) -> None:
        to_remove: List[Tuple[int, Optional[int], str]] = []
        for k, (view, _) in self._views.items():
            if view.is_finished():
                to_remove.append(k)

        for k in to_remove:
            del self._views[k]

    def add_view(self, view: View, message_id: Optional[int] = None) -> None:
        self.__verify_integrity()

        view._start_listening_from_store(self)
        for item in view.children:
            if item.is_dispatchable():
                self._views[(item.type.value, message_id, item.custom_id)] = (view, item)  # type: ignore

        if message_id is not None:
            self._synced_message_views[message_id] = view

    def remove_view(self, view: View) -> None:
        for item in view.children:
            if item.is_dispatchable():
                self._views.pop((item.type.value, item.custom_id), None)  # type: ignore

        for key, value in self._synced_message_views.items():
            if value.id == view.id:
                del self._synced_message_views[key]
                break

    def dispatch(self, interaction: MessageInteraction) -> None:
        self.__verify_integrity()
        message_id: Optional[int] = interaction.message and interaction.message.id
        component_type = try_enum_to_int(interaction.data.component_type)
        custom_id = interaction.data.custom_id
        key = (component_type, message_id, custom_id)
        # Fallback to None message_id searches in case a persistent view
        # was added without an associated message_id
        value = self._views.get(key) or self._views.get((component_type, None, custom_id))
        if value is None:
            return

        view, item = value
        item.refresh_state(interaction)
        view._dispatch_item(item, interaction)

    def is_message_tracked(self, message_id: int) -> bool:
        return message_id in self._synced_message_views

    def remove_message_tracking(self, message_id: int) -> Optional[View]:
        return self._synced_message_views.pop(message_id, None)

    def update_from_message(self, message_id: int, components: List[ComponentPayload]) -> None:
        # pre-req: is_message_tracked == true
        view = self._synced_message_views[message_id]
        view.refresh(
            [_component_factory(d, type=ActionRowComponent[MessageComponent]) for d in components]
        )
