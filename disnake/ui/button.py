# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import os
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from ..components import Button as ButtonComponent
from ..enums import ButtonStyle, ComponentType
from ..partial_emoji import PartialEmoji, _EmojiTag
from ..utils import MISSING
from .item import DecoratedItem, Item

__all__ = (
    "Button",
    "button",
)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Self

    from ..emoji import Emoji
    from .item import ItemCallbackType
    from .view import View

else:
    ParamSpec = TypeVar

B = TypeVar("B", bound="Button")
B_co = TypeVar("B_co", bound="Button", covariant=True)
V_co = TypeVar("V_co", bound="Optional[View]", covariant=True)
P = ParamSpec("P")


class Button(Item[V_co]):
    """Represents a UI button.

    .. versionadded:: 2.0

    Parameters
    ----------
    style: :class:`disnake.ButtonStyle`
        The style of the button.
    custom_id: Optional[:class:`str`]
        The ID of the button that gets received during an interaction.
        If this button is for a URL or an SKU, it does not have a custom ID.
    url: Optional[:class:`str`]
        The URL this button sends you to.
    disabled: :class:`bool`
        Whether the button is disabled.
    label: Optional[:class:`str`]
        The label of the button, if any.
    emoji: Optional[Union[:class:`.PartialEmoji`, :class:`.Emoji`, :class:`str`]]
        The emoji of the button, if available.
    sku_id: Optional[:class:`int`]
        The ID of a purchasable SKU, for premium buttons.
        Premium buttons additionally cannot have a ``label``, ``url``, or ``emoji``.

        .. versionadded:: 2.11
    row: Optional[:class:`int`]
        The relative row this button belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    __repr_attributes__: Tuple[str, ...] = (
        "style",
        "url",
        "disabled",
        "label",
        "emoji",
        "sku_id",
        "row",
    )
    # We have to set this to MISSING in order to overwrite the abstract property from UIComponent
    _underlying: ButtonComponent = MISSING

    @overload
    def __init__(
        self: Button[None],
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        sku_id: Optional[int] = None,
        row: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(
        self: Button[V_co],
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        sku_id: Optional[int] = None,
        row: Optional[int] = None,
    ) -> None: ...

    def __init__(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        sku_id: Optional[int] = None,
        row: Optional[int] = None,
    ) -> None:
        super().__init__()

        self._provided_custom_id = custom_id is not None
        mutually_exclusive = 3 - (custom_id, url, sku_id).count(None)

        if mutually_exclusive == 0:
            custom_id = os.urandom(16).hex()
        elif mutually_exclusive != 1:
            raise TypeError("cannot mix url, sku_id and custom_id with Button")

        if url is not None:
            style = ButtonStyle.link
        if sku_id is not None:
            style = ButtonStyle.premium

        if emoji is not None:
            if isinstance(emoji, str):
                emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                emoji = emoji._to_partial()
            else:
                raise TypeError(
                    f"expected emoji to be str, Emoji, or PartialEmoji not {emoji.__class__}"
                )

        self._underlying = ButtonComponent._raw_construct(
            type=ComponentType.button,
            custom_id=custom_id,
            url=url,
            disabled=disabled,
            label=label,
            style=style,
            emoji=emoji,
            sku_id=sku_id,
        )
        self.row = row

    @property
    def width(self) -> int:
        return 1

    @property
    def style(self) -> ButtonStyle:
        """:class:`disnake.ButtonStyle`: The style of the button."""
        return self._underlying.style

    @style.setter
    def style(self, value: ButtonStyle) -> None:
        self._underlying.style = value

    @property
    def custom_id(self) -> Optional[str]:
        """Optional[:class:`str`]: The ID of the button that gets received during an interaction.

        If this button is for a URL or an SKU, it does not have a custom ID.
        """
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("custom_id must be None or str")

        self._underlying.custom_id = value

    @property
    def url(self) -> Optional[str]:
        """Optional[:class:`str`]: The URL this button sends you to."""
        return self._underlying.url

    @url.setter
    def url(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("url must be None or str")
        self._underlying.url = value

    @property
    def disabled(self) -> bool:
        """:class:`bool`: Whether the button is disabled."""
        return self._underlying.disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._underlying.disabled = bool(value)

    @property
    def label(self) -> Optional[str]:
        """Optional[:class:`str`]: The label of the button, if available."""
        return self._underlying.label

    @label.setter
    def label(self, value: Optional[str]) -> None:
        self._underlying.label = str(value) if value is not None else value

    @property
    def emoji(self) -> Optional[PartialEmoji]:
        """Optional[:class:`.PartialEmoji`]: The emoji of the button, if available."""
        return self._underlying.emoji

    @emoji.setter
    def emoji(self, value: Optional[Union[str, Emoji, PartialEmoji]]) -> None:
        if value is not None:
            if isinstance(value, str):
                self._underlying.emoji = PartialEmoji.from_str(value)
            elif isinstance(value, _EmojiTag):
                self._underlying.emoji = value._to_partial()
            else:
                raise TypeError(
                    f"expected str, Emoji, or PartialEmoji, received {value.__class__} instead"
                )
        else:
            self._underlying.emoji = None

    @property
    def sku_id(self) -> Optional[int]:
        """Optional[:class:`int`]: The ID of a purchasable SKU, for premium buttons.

        .. versionadded:: 2.11
        """
        return self._underlying.sku_id

    @sku_id.setter
    def sku_id(self, value: Optional[int]) -> None:
        if value is not None and not isinstance(value, int):
            raise TypeError("sku_id must be None or int")
        self._underlying.sku_id = value

    @classmethod
    def from_component(cls, button: ButtonComponent) -> Self:
        return cls(
            style=button.style,
            label=button.label,
            disabled=button.disabled,
            custom_id=button.custom_id,
            url=button.url,
            emoji=button.emoji,
            sku_id=button.sku_id,
            row=None,
        )

    def is_dispatchable(self) -> bool:
        return self.custom_id is not None

    def is_persistent(self) -> bool:
        if self.style is ButtonStyle.link:
            return self.url is not None
        elif self.style is ButtonStyle.premium:
            return self.sku_id is not None
        return super().is_persistent()

    def refresh_component(self, button: ButtonComponent) -> None:
        self._underlying = button


@overload
def button(
    *,
    label: Optional[str] = None,
    custom_id: Optional[str] = None,
    disabled: bool = False,
    style: ButtonStyle = ButtonStyle.secondary,
    emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
    row: Optional[int] = None,
) -> Callable[[ItemCallbackType[V_co, Button[V_co]]], DecoratedItem[Button[V_co]]]: ...


@overload
def button(
    cls: Callable[P, B_co], *_: P.args, **kwargs: P.kwargs
) -> Callable[[ItemCallbackType[V_co, B_co]], DecoratedItem[B_co]]: ...


def button(
    cls: Callable[..., B_co] = Button[Any], **kwargs: Any
) -> Callable[[ItemCallbackType[V_co, B_co]], DecoratedItem[B_co]]:
    """A decorator that attaches a button to a component.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`disnake.ui.View`, the :class:`disnake.ui.Button` that was
    interacted with, and the :class:`disnake.MessageInteraction`.

    .. note::

        Link/Premium buttons cannot be created with this function,
        since these buttons do not have a callback associated with them.
        Consider creating a :class:`Button` manually instead, and adding it
        using :meth:`View.add_item`.

    Parameters
    ----------
    cls: Callable[..., :class:`Button`]
        A callable (may be a :class:`Button` subclass) to create a new instance of this component.
        If provided, the other parameters described below do not apply.
        Instead, this decorator will accept the same keywords as the passed callable/class does.

        .. versionadded:: 2.6
    label: Optional[:class:`str`]
        The label of the button, if any.
    custom_id: Optional[:class:`str`]
        The ID of the button that gets received during an interaction.
        It is recommended not to set this parameter to prevent conflicts.
    style: :class:`.ButtonStyle`
        The style of the button. Defaults to :attr:`.ButtonStyle.grey`.
    disabled: :class:`bool`
        Whether the button is disabled. Defaults to ``False``.
    emoji: Optional[Union[:class:`str`, :class:`.Emoji`, :class:`.PartialEmoji`]]
        The emoji of the button. This can be in string form or a :class:`.PartialEmoji`
        or a full :class:`.Emoji`.
    row: Optional[:class:`int`]
        The relative row this button belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """
    if not callable(cls):
        raise TypeError("cls argument must be callable")

    def decorator(func: ItemCallbackType[V_co, B_co]) -> DecoratedItem[B_co]:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("button function must be a coroutine function")

        func.__discord_ui_model_type__ = cls
        func.__discord_ui_model_kwargs__ = kwargs
        return func  # type: ignore

    return decorator
