# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generator,
    Generic,
    Iterator,
    List,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from ..components import (
    ActionRow as ActionRowComponent,
    ActionRowChildComponent,
    ActionRowMessageComponent as ActionRowMessageComponentRaw,
    Button as ButtonComponent,
    ChannelSelectMenu as ChannelSelectComponent,
    Component,
    Container as ContainerComponent,
    FileComponent as FileComponent,
    Label as LabelComponent,
    MediaGallery as MediaGalleryComponent,
    MentionableSelectMenu as MentionableSelectComponent,
    RoleSelectMenu as RoleSelectComponent,
    Section as SectionComponent,
    Separator as SeparatorComponent,
    StringSelectMenu as StringSelectComponent,
    TextDisplay as TextDisplayComponent,
    TextInput as TextInputComponent,
    Thumbnail as ThumbnailComponent,
    UserSelectMenu as UserSelectComponent,
)
from ..enums import ButtonStyle, ChannelType, ComponentType, TextInputStyle
from ..utils import MISSING, SequenceProxy, assert_never, copy_doc, deprecated
from ._types import (
    ActionRowChildT,
    ActionRowMessageComponent,
    ActionRowModalComponent,
    ComponentInput,
    MessageTopLevelComponent,
    NonActionRowChildT,
)
from .button import Button
from .container import Container
from .file import File
from .item import UIComponent, WrappedComponent
from .label import Label
from .media_gallery import MediaGallery
from .section import Section
from .select import ChannelSelect, MentionableSelect, RoleSelect, StringSelect, UserSelect
from .separator import Separator
from .text_display import TextDisplay
from .text_input import TextInput
from .thumbnail import Thumbnail

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

    from ..abc import AnyChannel
    from ..emoji import Emoji
    from ..member import Member
    from ..message import Message
    from ..partial_emoji import PartialEmoji
    from ..role import Role
    from ..types.components import (
        ActionRow as ActionRowPayload,
        MessageTopLevelComponent as MessageTopLevelComponentPayload,
    )
    from ..user import User
    from .select.base import SelectDefaultValueInputType, SelectDefaultValueMultiInputType
    from .select.string import SelectOptionInput

__all__ = (
    "ActionRow",
    "Components",
    "MessageUIComponent",
    "ModalUIComponent",
    "MessageActionRow",
    "ModalActionRow",
    "walk_components",
    "components_from_message",
)

# FIXME(3.0): legacy
MessageUIComponent: TypeAlias = ActionRowMessageComponent
ModalUIComponent: TypeAlias = ActionRowModalComponent
Components: TypeAlias = ComponentInput[ActionRowChildT, NoReturn]

StrictActionRowChildT = TypeVar(
    "StrictActionRowChildT", ActionRowMessageComponent, ActionRowModalComponent
)

# this is cursed
ButtonCompatibleActionRowT = TypeVar(
    "ButtonCompatibleActionRowT",
    bound="Union[ActionRow[ActionRowMessageComponent], ActionRow[WrappedComponent]]",
)
SelectCompatibleActionRowT = TypeVar(
    "SelectCompatibleActionRowT",
    bound="Union[ActionRow[ActionRowMessageComponent], ActionRow[WrappedComponent]]",
)
TextInputCompatibleActionRowT = TypeVar(
    "TextInputCompatibleActionRowT",
    bound="Union[ActionRow[ActionRowModalComponent], ActionRow[WrappedComponent]]",
)


class ActionRow(UIComponent, Generic[ActionRowChildT]):
    """Represents a UI action row. Useful for lower level component manipulation.

    .. collapse:: operations

        .. describe:: x[i]

            Returns the component at position ``i``. Also supports slices.

            .. versionadded:: 2.6

        .. describe:: len(x)

            Returns the number of components in this row.
            Note that this means empty rows will be considered falsy.

            .. versionadded:: 2.6

        .. describe:: iter(x)

            Returns an iterator for the components in this row.

            .. versionadded:: 2.6

    To handle interactions created by components sent in action rows or entirely independently,
    event listeners must be used. For buttons and selects, the related events are
    :func:`disnake.on_button_click` and :func:`disnake.on_dropdown`, respectively. Alternatively,
    :func:`disnake.on_message_interaction` can be used for either. For modals, the related event is
    :func:`disnake.on_modal_submit`.

    .. versionadded:: 2.4

    .. versionchanged:: 2.6
        Requires and provides stricter typing for contained components.

    Parameters
    ----------
    *components: :class:`WrappedComponent`
        The components of this action row.

        .. versionchanged:: 2.6
            Components can now be either valid in the context of a message, or in the
            context of a modal. Combining components from both contexts is not supported.
    id: :class:`int`
        The numeric identifier for the component. Must be unique within the message.
        If set to ``0`` (the default) when sending a component, the API will assign
        sequential identifiers to the components in the message.

        .. versionadded:: 2.11
    """

    __repr_attributes__: ClassVar[Tuple[str, ...]] = ("_children",)

    # When unspecified and called empty, default to an ActionRow that takes any kind of component.

    @overload
    def __init__(self: ActionRow[WrappedComponent], *, id: int = 0) -> None: ...

    # Explicit definitions are needed to make
    # "ActionRow(StringSelect(), TextInput())" and
    # "ActionRow(StringSelect(), Button())"
    # differentiate themselves properly.

    @overload
    def __init__(
        self: ActionRow[ActionRowMessageComponent],
        *components: ActionRowMessageComponent,
        id: int = 0,
    ) -> None: ...

    @overload
    def __init__(
        self: ActionRow[ActionRowModalComponent],
        *components: ActionRowModalComponent,
        id: int = 0,
    ) -> None: ...

    @overload
    def __init__(self, *components: ActionRowChildT, id: int = 0) -> None: ...

    # n.b. this should be `*components: ActionRowChildT`, but pyright does not like it
    def __init__(self, *components: WrappedComponent, id: int = 0) -> None:
        self._id: int = id
        self._children: List[ActionRowChildT] = []

        for component in components:
            if not isinstance(component, WrappedComponent):
                msg = f"components should be of type WrappedComponent, got {type(component).__name__}."
                raise TypeError(msg)
            self.append_item(component)  # type: ignore

    def __len__(self) -> int:
        return len(self._children)

    # these are reimplemented here to store the value in a separate attribute,
    # since `ActionRow` lazily constructs `_underlying`, unlike most components
    @property
    @copy_doc(UIComponent.id)
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def children(self) -> Sequence[ActionRowChildT]:
        """Sequence[:class:`WrappedComponent`]:
        A read-only proxy of the UI components stored in this action row. To add/remove
        components to/from the action row, use its methods to directly modify it.

        .. versionchanged:: 2.6
            Returns an immutable sequence instead of a list.
        """
        return SequenceProxy(self._children)

    @property
    def width(self) -> int:
        return sum(child.width for child in self._children)

    def append_item(self, item: ActionRowChildT) -> Self:
        """Append a component to the action row. The component's type must match that
        of the action row.

        This function returns the class instance to allow for fluent-style chaining.

        Parameters
        ----------
        item: :class:`WrappedComponent`
            The component to append to the action row.

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.insert_item(len(self), item)
        return self

    def insert_item(self, index: int, item: ActionRowChildT) -> Self:
        """Insert a component to the action row at a given index. The component's
        type must match that of the action row.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.6

        Parameters
        ----------
        index: :class:`int`
            The index at which to insert the component into the action row.
        item: :class:`WrappedComponent`
            The component to insert into the action row.

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        if self.width + item.width > 5:
            msg = "Too many components in this row, can not append a new one."
            raise ValueError(msg)

        self._children.insert(index, item)
        return self

    def add_button(
        self: ButtonCompatibleActionRowT,
        index: Optional[int] = None,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        sku_id: Optional[int] = None,
        id: int = 0,
    ) -> ButtonCompatibleActionRowT:
        """Add a button to the action row. Can only be used if the action
        row holds message components.

        To append a pre-existing :class:`~disnake.ui.Button` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionchanged:: 2.6
            Now allows for inserting at a given index. The default behaviour of
            appending is preserved.

        Parameters
        ----------
        index: :class:`int`
            The index at which to insert the button into the action row. If not provided,
            this method defaults to appending the button to the action row.
        style: :class:`.ButtonStyle`
            The style of the button.
        custom_id: Optional[:class:`str`]
            The ID of the button that gets received during an interaction.
            If this button is for a URL, it does not have a custom ID.
        url: Optional[:class:`str`]
            The URL this button sends you to.
        disabled: :class:`bool`
            Whether the button is disabled or not.
        label: Optional[:class:`str`]
            The label of the button, if any.
        emoji: Optional[Union[:class:`.PartialEmoji`, :class:`.Emoji`, :class:`str`]]
            The emoji of the button, if available.
        sku_id: Optional[:class:`int`]
            The ID of a purchasable SKU, for premium buttons.
            Premium buttons additionally cannot have a ``label``, ``url``, or ``emoji``.

            .. versionadded:: 2.11
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.insert_item(
            len(self) if index is None else index,
            Button(
                id=id,
                style=style,
                label=label,
                disabled=disabled,
                custom_id=custom_id,
                url=url,
                emoji=emoji,
                sku_id=sku_id,
            ),
        )
        return self

    def add_string_select(
        self: SelectCompatibleActionRowT,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        options: SelectOptionInput = MISSING,
        disabled: bool = False,
        id: int = 0,
    ) -> SelectCompatibleActionRowT:
        """Add a string select menu to the action row. Can only be used if the action
        row holds message components.

        To append a pre-existing :class:`~disnake.ui.StringSelect` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionchanged:: 2.7
            Renamed from ``add_select`` to ``add_string_select``.

        Parameters
        ----------
        custom_id: :class:`str`
            The ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        options: Union[List[:class:`disnake.SelectOption`], List[:class:`str`], Dict[:class:`str`, :class:`str`]]
            A list of options that can be selected in this menu. Use explicit :class:`.SelectOption`\\s
            for fine-grained control over the options. Alternatively, a list of strings will be treated
            as a list of labels, and a dict will be treated as a mapping of labels to values.
        disabled: :class:`bool`
            Whether the select is disabled or not.
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.append_item(
            StringSelect(
                id=id,
                custom_id=custom_id,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                options=options,
                disabled=disabled,
            ),
        )
        return self

    add_select = add_string_select  # backwards compatibility

    def add_user_select(
        self: SelectCompatibleActionRowT,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Optional[Sequence[SelectDefaultValueInputType[Union[User, Member]]]] = None,
        id: int = 0,
    ) -> SelectCompatibleActionRowT:
        """Add a user select menu to the action row. Can only be used if the action
        row holds message components.

        To append a pre-existing :class:`~disnake.ui.UserSelect` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.7

        Parameters
        ----------
        custom_id: :class:`str`
            The ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        disabled: :class:`bool`
            Whether the select is disabled. Defaults to ``False``.
        default_values: Optional[Sequence[Union[:class:`~disnake.User`, :class:`.Member`, :class:`.SelectDefaultValue`, :class:`.Object`]]]
            The list of values (users/members) that are selected by default.
            If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

            .. versionadded:: 2.10
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.append_item(
            UserSelect(
                id=id,
                custom_id=custom_id,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                disabled=disabled,
                default_values=default_values,
            ),
        )
        return self

    def add_role_select(
        self: SelectCompatibleActionRowT,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Optional[Sequence[SelectDefaultValueInputType[Role]]] = None,
        id: int = 0,
    ) -> SelectCompatibleActionRowT:
        """Add a role select menu to the action row. Can only be used if the action
        row holds message components.

        To append a pre-existing :class:`~disnake.ui.RoleSelect` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.7

        Parameters
        ----------
        custom_id: :class:`str`
            The ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        disabled: :class:`bool`
            Whether the select is disabled. Defaults to ``False``.
        default_values: Optional[Sequence[Union[:class:`.Role`, :class:`.SelectDefaultValue`, :class:`.Object`]]]
            The list of values (roles) that are selected by default.
            If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

            .. versionadded:: 2.10
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.append_item(
            RoleSelect(
                id=id,
                custom_id=custom_id,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                disabled=disabled,
                default_values=default_values,
            ),
        )
        return self

    def add_mentionable_select(
        self: SelectCompatibleActionRowT,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        default_values: Optional[
            Sequence[SelectDefaultValueMultiInputType[Union[User, Member, Role]]]
        ] = None,
        id: int = 0,
    ) -> SelectCompatibleActionRowT:
        """Add a mentionable (user/member/role) select menu to the action row. Can only be used if the action
        row holds message components.

        To append a pre-existing :class:`~disnake.ui.MentionableSelect` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.7

        Parameters
        ----------
        custom_id: :class:`str`
            The ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        disabled: :class:`bool`
            Whether the select is disabled. Defaults to ``False``.
        default_values: Optional[Sequence[Union[:class:`~disnake.User`, :class:`.Member`, :class:`.Role`, :class:`.SelectDefaultValue`]]]
            The list of values (users/roles) that are selected by default.
            If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

            Note that unlike other select menu types, this does not support :class:`.Object`\\s due to ambiguities.

            .. versionadded:: 2.10
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.append_item(
            MentionableSelect(
                id=id,
                custom_id=custom_id,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                disabled=disabled,
                default_values=default_values,
            ),
        )
        return self

    def add_channel_select(
        self: SelectCompatibleActionRowT,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        channel_types: Optional[List[ChannelType]] = None,
        default_values: Optional[Sequence[SelectDefaultValueInputType[AnyChannel]]] = None,
        id: int = 0,
    ) -> SelectCompatibleActionRowT:
        """Add a channel select menu to the action row. Can only be used if the action
        row holds message components.

        To append a pre-existing :class:`~disnake.ui.ChannelSelect` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.7

        Parameters
        ----------
        custom_id: :class:`str`
            The ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        disabled: :class:`bool`
            Whether the select is disabled. Defaults to ``False``.
        channel_types: Optional[List[:class:`.ChannelType`]]
            The list of channel types that can be selected in this select menu.
            Defaults to all types (i.e. ``None``).
        default_values: Optional[Sequence[Union[:class:`.abc.GuildChannel`, :class:`.Thread`, :class:`.abc.PrivateChannel`, :class:`.PartialMessageable`, :class:`.SelectDefaultValue`, :class:`.Object`]]]
            The list of values (channels) that are selected by default.
            If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

            .. versionadded:: 2.10
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.append_item(
            ChannelSelect(
                id=id,
                custom_id=custom_id,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                disabled=disabled,
                channel_types=channel_types,
                default_values=default_values,
            ),
        )
        return self

    @deprecated('Label("<text>", TextInput(...))')
    def add_text_input(
        self: TextInputCompatibleActionRowT,
        *,
        label: str,
        custom_id: str,
        style: TextInputStyle = TextInputStyle.short,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        id: int = 0,
    ) -> TextInputCompatibleActionRowT:
        """Add a text input to the action row. Can only be used if the action
        row holds modal components.

        To append a pre-existing :class:`~disnake.ui.TextInput` use the
        :meth:`append_item` method instead.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.4

        .. deprecated:: 2.11
            Use of action rows in modals is deprecated, use
            ``Label("<text>", TextInput(...))`` directly instead.

        Parameters
        ----------
        style: :class:`.TextInputStyle`
            The style of the text input.
        label: :class:`str`
            The label of the text input.
        custom_id: :class:`str`
            The ID of the text input that gets received during an interaction.
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
        id: :class:`int`
            The numeric identifier for the component.
            If set to ``0`` (the default) when sending a component, the API will assign
            sequential identifiers to the components in the message.

            .. versionadded:: 2.11

        Raises
        ------
        ValueError
            The width of the action row exceeds 5.
        """
        self.append_item(
            TextInput(
                id=id,
                label=label,
                custom_id=custom_id,
                style=style,
                placeholder=placeholder,
                value=value,
                required=required,
                min_length=min_length,
                max_length=max_length,
            ),
        )

        return self

    def clear_items(self) -> Self:
        """Remove all components from the action row.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.6
        """
        self._children.clear()
        return self

    def remove_item(self, item: ActionRowChildT) -> Self:
        """Remove a component from the action row.

        This function returns the class instance to allow for fluent-style chaining.

        .. versionadded:: 2.6

        Parameters
        ----------
        item: :class:`WrappedComponent`
            The component to remove from the action row.

        Raises
        ------
        ValueError
            The component could not be found on the action row.
        """
        self._children.remove(item)
        return self

    def pop(self, index: int) -> ActionRowChildT:
        """Pop the component at the provided index from the action row.

        .. versionadded:: 2.6

        Parameters
        ----------
        index: :class:`int`
            The index at which to pop the component.

        Raises
        ------
        IndexError
            There is no component at the provided index.
        """
        self.remove_item(component := self[index])
        return component

    @property
    def _underlying(self) -> ActionRowComponent[ActionRowChildComponent]:
        return ActionRowComponent._raw_construct(
            type=ComponentType.action_row,
            id=self._id,
            children=[comp._underlying for comp in self._children],
        )

    # already provided by base type, reimplemented here for more precise return types
    def to_component_dict(self) -> ActionRowPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls, action_row: ActionRowComponent) -> Self:
        return cls(
            *cast(
                "List[ActionRowChildT]",
                [_to_ui_component(c) for c in action_row.children],
            ),
            id=action_row.id,
        )

    def __delitem__(self, index: Union[int, slice]) -> None:
        del self._children[index]

    @overload
    def __getitem__(self, index: int) -> ActionRowChildT: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[ActionRowChildT]: ...

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[ActionRowChildT, Sequence[ActionRowChildT]]:
        return self._children[index]

    def __iter__(self) -> Iterator[ActionRowChildT]:
        return iter(self._children)

    @classmethod
    @deprecated()
    def with_modal_components(cls, *, id: int = 0) -> ActionRow[ActionRowModalComponent]:
        """Create an empty action row meant to store components compatible with
        :class:`disnake.ui.Modal`. Saves the need to import type specifiers to
        typehint empty action rows.

        .. versionadded:: 2.6

        .. deprecated:: 2.11
            Use of action rows in modals is deprecated, compatible components
            can be passed directly to modals.

        Returns
        -------
        :class:`ActionRow`:
            The newly created empty action row, intended for modal components.
        """
        return ActionRow[ActionRowModalComponent](id=id)

    @classmethod
    def with_message_components(cls, *, id: int = 0) -> ActionRow[ActionRowMessageComponent]:
        """Create an empty action row meant to store components compatible with
        :class:`disnake.Message`. Saves the need to import type specifiers to
        typehint empty action rows.

        .. versionadded:: 2.6

        Returns
        -------
        :class:`ActionRow`:
            The newly created empty action row, intended for message components.
        """
        return ActionRow[ActionRowMessageComponent](id=id)

    @classmethod
    def rows_from_message(
        cls,
        message: Message,
        *,
        strict: bool = True,
    ) -> List[ActionRow[ActionRowMessageComponent]]:
        """Create a list of up to 5 action rows from the components on an existing message.

        This will abide by existing component format on the message, including component
        ordering and rows. Components will be transformed to UI kit components, such that
        they can be easily modified and re-sent as action rows.

        .. note::
            This only supports :class:`ActionRow`\\s and associated components, i.e. no v2 components.
            See :func:`.ui.components_from_message` for a function that supports all component types.

        .. versionadded:: 2.6

        Parameters
        ----------
        message: :class:`disnake.Message`
            The message from which to extract the components.
        strict: :class:`bool`
            Whether or not to raise an exception if an unknown component type is encountered.

        Raises
        ------
        TypeError
            Strict-mode is enabled, and an unknown component type is encountered
            or message uses v2 components (see also :attr:`.MessageFlags.is_components_v2`).

        Returns
        -------
        List[:class:`ActionRow`]:
            The action rows parsed from the components on the message.
        """
        rows: List[ActionRow[ActionRowMessageComponent]] = []
        for row in message.components:
            if not isinstance(row, ActionRowComponent):
                # can happen if message uses components v2
                if strict:
                    msg = f"Unexpected top-level component type: {row.type!r}"
                    raise TypeError(msg)
                continue

            rows.append(current_row := ActionRow.with_message_components())
            for component in row.children:
                if item := _message_component_to_item(component):
                    current_row.append_item(item)
                elif strict:
                    msg = f"Encountered unknown component type: {component.type!r}."
                    raise TypeError(msg)

        return rows

    @staticmethod
    def walk_components(
        action_rows: Sequence[ActionRow[ActionRowChildT]],
    ) -> Generator[Tuple[ActionRow[ActionRowChildT], ActionRowChildT], None, None]:
        """Iterate over the components in a sequence of action rows, yielding each
        individual component together with the action row of which it is a child.

        .. note::
            This only supports :class:`ActionRow`\\s, i.e. no v2 components.
            See :func:`.ui.walk_components` for a function that supports all component types.

        .. versionadded:: 2.6

        Parameters
        ----------
        action_rows: Sequence[:class:`ActionRow`]
            The sequence of action rows over which to iterate.

        Yields
        ------
        Tuple[:class:`ActionRow`, :class:`WrappedComponent`]
            A tuple containing an action row and a component of that action row.
        """
        for row in tuple(action_rows):
            for component in tuple(row._children):
                yield row, component


# FIXME(3.0): consider removing
MessageActionRow = ActionRow[ActionRowMessageComponent]
ModalActionRow = ActionRow[ActionRowModalComponent]


# n.b. the typings with `modal = True` are technically slightly off here,
# however this is only used internally and does not affect public typings
@overload
def normalize_components(
    components: ComponentInput[NoReturn, NonActionRowChildT], /, modal: bool = False
) -> Sequence[NonActionRowChildT]: ...


@overload
def normalize_components(
    components: ComponentInput[ActionRowChildT, NonActionRowChildT], /, modal: bool = False
) -> Sequence[Union[ActionRow[ActionRowChildT], NonActionRowChildT]]: ...


def normalize_components(
    components: ComponentInput[ActionRowChildT, NonActionRowChildT], /, modal: bool = False
) -> Sequence[Union[ActionRow[ActionRowChildT], NonActionRowChildT]]:
    """Wraps consecutive actionrow-compatible components or lists in `ActionRow`s,
    while respecting the width limit. Other components are returned as-is.

    If `modal` is `True`, only wraps `TextInput`s in action rows, and returns other (otherwise
    actionrow-compatible) components as-is.
    """
    if not isinstance(components, Sequence):
        components = [components]

    result: List[Union[ActionRow[ActionRowChildT], NonActionRowChildT]] = []
    auto_row: ActionRow[ActionRowChildT] = ActionRow[ActionRowChildT]()

    wrap_types = TextInput if modal else WrappedComponent

    for component in components:
        if isinstance(component, wrap_types):
            # action row child component, try to insert into current row, otherwise create new row
            try:
                auto_row.append_item(component)
            except ValueError:
                result.append(auto_row)
                auto_row = ActionRow[ActionRowChildT](component)
        else:
            if auto_row.width > 0:
                # if the current action row has items, finish it
                result.append(auto_row)
                auto_row = ActionRow[ActionRowChildT]()

            if isinstance(component, UIComponent):
                # append non-actionrow-child components as-is
                # (action rows, v2 components, or actionrow-child components in modals)
                result.append(component)

            elif isinstance(component, Sequence):
                result.append(ActionRow[ActionRowChildT](*component))

            else:
                assert_never(component)
                msg = (
                    "`components` must be a single component, "
                    "a sequence/list of components (or action rows), "
                    "or a nested sequence/list of action row compatible components"
                )
                raise TypeError(msg)

    if auto_row.width > 0:
        result.append(auto_row)

    return result


def normalize_components_to_dict(
    components: ComponentInput[ActionRowChildT, NonActionRowChildT],
) -> Tuple[List[MessageTopLevelComponentPayload], bool]:
    """`normalize_components`, but also turns components into dicts.
    Returns ([d1, d2, ...], has_v2_component).
    """
    component_payloads: List[Mapping[str, Any]] = []
    is_v2 = False

    for c in normalize_components(components):
        component_payloads.append(c.to_component_dict())
        is_v2 |= c.is_v2

    return cast("List[MessageTopLevelComponentPayload]", component_payloads), is_v2


ComponentT = TypeVar("ComponentT", Component, UIComponent)


def _walk_internal(component: ComponentT, seen: Set[ComponentT]) -> Iterator[ComponentT]:
    if component in seen:
        # prevent infinite recursion in case anyone manages to nest a component in itself
        return
    # add current component, while also creating a copy to allow reusing a component multiple times,
    # as long as it's not within itself
    seen = {*seen, component}

    yield component

    if isinstance(component, (ActionRowComponent, ActionRow)):
        for item in component.children:
            yield from _walk_internal(item, seen)
    elif isinstance(component, (SectionComponent, Section)):
        yield from _walk_internal(component.accessory, seen)
        for item in component.children:
            yield from _walk_internal(item, seen)  # type: ignore  # this is fine, pyright loses the conditional type when iterating
    elif isinstance(component, (ContainerComponent, Container)):
        for item in component.children:
            yield from _walk_internal(item, seen)  # type: ignore
    elif isinstance(component, (LabelComponent, Label)):
        yield from _walk_internal(component.component, seen)


def walk_components(components: Sequence[ComponentT]) -> Iterator[ComponentT]:
    """Iterate over given components, yielding each individual component,
    including child components where applicable (e.g. for :class:`ActionRow` and :class:`Container`).

    .. versionadded:: 2.11

    Parameters
    ----------
    components: Union[Sequence[:class:`~disnake.Component`], Sequence[:class:`UIComponent`]]
        The sequence of components to iterate over. This supports both :class:`disnake.Component`
        objects and :class:`.ui.UIComponent` objects.

    Yields
    ------
    Union[:class:`~disnake.Component`, :class:`UIComponent`]
        A component from the given sequence or child component thereof.
    """
    seen: Set[ComponentT] = set()
    for item in components:
        yield from _walk_internal(item, seen)


def components_from_message(message: Message) -> List[MessageTopLevelComponent]:
    """Create a list of :class:`UIComponent`\\s from the components of an existing message.

    This will abide by existing component format on the message, including component
    ordering. Components will be transformed to UI kit components, such that
    they can be easily modified and re-sent.

    .. versionadded:: 2.11

    Parameters
    ----------
    message: :class:`disnake.Message`
        The message from which to extract the components.

    Raises
    ------
    TypeError
        An unknown component type is encountered.

    Returns
    -------
    List[:class:`UIComponent`]:
        The ui components parsed from the components on the message.
    """
    components: List[UIComponent] = [_to_ui_component(c) for c in message.components]
    return cast("List[MessageTopLevelComponent]", components)


UI_COMPONENT_LOOKUP: Mapping[Type[Component], Type[UIComponent]] = {
    ActionRowComponent: ActionRow,
    ButtonComponent: Button,
    StringSelectComponent: StringSelect,
    TextInputComponent: TextInput,
    UserSelectComponent: UserSelect,
    RoleSelectComponent: RoleSelect,
    MentionableSelectComponent: MentionableSelect,
    ChannelSelectComponent: ChannelSelect,
    SectionComponent: Section,
    TextDisplayComponent: TextDisplay,
    ThumbnailComponent: Thumbnail,
    MediaGalleryComponent: MediaGallery,
    FileComponent: File,
    SeparatorComponent: Separator,
    ContainerComponent: Container,
    LabelComponent: Label,
}


def _to_ui_component(component: Component) -> UIComponent:
    try:
        ui_cls = UI_COMPONENT_LOOKUP[type(component)]
    except KeyError:
        # this should never happen
        msg = f"unknown component type: {type(component)}"
        raise TypeError(msg) from None
    else:
        return ui_cls.from_component(component)


def _message_component_to_item(
    component: ActionRowMessageComponentRaw,
) -> Optional[ActionRowMessageComponent]:
    if isinstance(
        component,
        (
            ButtonComponent,
            StringSelectComponent,
            UserSelectComponent,
            RoleSelectComponent,
            MentionableSelectComponent,
            ChannelSelectComponent,
        ),
    ):
        return _to_ui_component(component)  # type: ignore

    assert_never(component)
    return None
