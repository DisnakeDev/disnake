# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Final,
    Generic,
    Literal,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

from .asset import AssetMixin
from .colour import Colour
from .enums import (
    ButtonStyle,
    ChannelType,
    ComponentType,
    SelectDefaultValueType,
    SeparatorSpacing,
    TextInputStyle,
    try_enum,
)
from .partial_emoji import PartialEmoji, _EmojiTag
from .utils import MISSING, _get_as_snowflake, assert_never, get_slots

if TYPE_CHECKING:
    from typing import TypeAlias

    from typing_extensions import Self

    from .emoji import Emoji
    from .message import Attachment
    from .types.components import (
        ActionRow as ActionRowPayload,
        AnySelectMenu as AnySelectMenuPayload,
        BaseSelectMenu as BaseSelectMenuPayload,
        ButtonComponent as ButtonComponentPayload,
        ChannelSelectMenu as ChannelSelectMenuPayload,
        Component as ComponentPayload,
        ComponentType as ComponentTypeLiteral,
        ContainerComponent as ContainerComponentPayload,
        FileComponent as FileComponentPayload,
        FileUploadComponent as FileUploadComponentPayload,
        LabelComponent as LabelComponentPayload,
        MediaGalleryComponent as MediaGalleryComponentPayload,
        MediaGalleryItem as MediaGalleryItemPayload,
        MentionableSelectMenu as MentionableSelectMenuPayload,
        MessageTopLevelComponent as MessageTopLevelComponentPayload,
        RoleSelectMenu as RoleSelectMenuPayload,
        SectionComponent as SectionComponentPayload,
        SelectDefaultValue as SelectDefaultValuePayload,
        SelectOption as SelectOptionPayload,
        SeparatorComponent as SeparatorComponentPayload,
        StringSelectMenu as StringSelectMenuPayload,
        TextDisplayComponent as TextDisplayComponentPayload,
        TextInput as TextInputPayload,
        ThumbnailComponent as ThumbnailComponentPayload,
        UnfurledMediaItem as UnfurledMediaItemPayload,
        UserSelectMenu as UserSelectMenuPayload,
    )

__all__ = (
    "Component",
    "ActionRow",
    "Button",
    "BaseSelectMenu",
    "StringSelectMenu",
    "SelectMenu",
    "UserSelectMenu",
    "RoleSelectMenu",
    "MentionableSelectMenu",
    "ChannelSelectMenu",
    "SelectOption",
    "SelectDefaultValue",
    "TextInput",
    "Section",
    "TextDisplay",
    "UnfurledMediaItem",
    "Thumbnail",
    "MediaGallery",
    "MediaGalleryItem",
    "FileComponent",
    "Separator",
    "Container",
    "Label",
    "FileUpload",
)

# miscellaneous components-related type aliases

LocalMediaItemInput = Union[str, "UnfurledMediaItem"]
MediaItemInput = Union[LocalMediaItemInput, "AssetMixin", "Attachment"]

AnySelectMenu = Union[
    "StringSelectMenu",
    "UserSelectMenu",
    "RoleSelectMenu",
    "MentionableSelectMenu",
    "ChannelSelectMenu",
]

SelectMenuType = Literal[
    ComponentType.string_select,
    ComponentType.user_select,
    ComponentType.role_select,
    ComponentType.mentionable_select,
    ComponentType.channel_select,
]

# valid `ActionRow.components` item types in a message/modal
ActionRowMessageComponent: TypeAlias = Union["Button", "AnySelectMenu"]
ActionRowModalComponent: TypeAlias = "TextInput"

# any child component type of action rows
ActionRowChildComponent: TypeAlias = Union[ActionRowMessageComponent, ActionRowModalComponent]  # noqa: UP007
ActionRowChildComponentT = TypeVar("ActionRowChildComponentT", bound=ActionRowChildComponent)

# valid `Section.accessory` types
SectionAccessoryComponent: TypeAlias = Union["Thumbnail", "Button"]
# valid `Section.components` item types
SectionChildComponent: TypeAlias = "TextDisplay"

# valid `Container.components` item types
ContainerChildComponent: TypeAlias = Union[
    "ActionRow[ActionRowMessageComponent]",
    "Section",
    "TextDisplay",
    "MediaGallery",
    "FileComponent",
    "Separator",
]

# valid `Label.component` types
LabelChildComponent = Union[
    "TextInput",
    "FileUpload",
    "AnySelectMenu",
]

# valid `Message.components` item types (v1/v2)
MessageTopLevelComponentV1: TypeAlias = "ActionRow[ActionRowMessageComponent]"
MessageTopLevelComponentV2 = Union[
    "Section",
    "TextDisplay",
    "MediaGallery",
    "FileComponent",
    "Separator",
    "Container",
]
MessageTopLevelComponent: TypeAlias = Union[MessageTopLevelComponentV1, MessageTopLevelComponentV2]  # noqa: UP007


_SELECT_COMPONENT_TYPES = frozenset(
    (
        ComponentType.string_select,
        ComponentType.user_select,
        ComponentType.role_select,
        ComponentType.mentionable_select,
        ComponentType.channel_select,
    )
)

# not using `_SELECT_COMPONENT_TYPES` since pyright wouldn't infer the literal properly
_SELECT_COMPONENT_TYPE_VALUES = frozenset(
    (
        ComponentType.string_select.value,
        ComponentType.user_select.value,
        ComponentType.role_select.value,
        ComponentType.mentionable_select.value,
        ComponentType.channel_select.value,
    )
)


class Component:
    """Represents the base component that all other components inherit from.

    The components supported by Discord are:

    - :class:`ActionRow`
    - :class:`Button`
    - subtypes of :class:`BaseSelectMenu` (:class:`ChannelSelectMenu`, :class:`MentionableSelectMenu`, :class:`RoleSelectMenu`, :class:`StringSelectMenu`, :class:`UserSelectMenu`)
    - :class:`TextInput`
    - :class:`Section`
    - :class:`TextDisplay`
    - :class:`Thumbnail`
    - :class:`MediaGallery`
    - :class:`FileComponent`
    - :class:`Separator`
    - :class:`Container`
    - :class:`Label`
    - :class:`FileUpload`

    This class is abstract and cannot be instantiated.

    .. versionadded:: 2.0

    Attributes
    ----------
    type: :class:`ComponentType`
        The type of component.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.
        If set to ``0`` (the default) when sending a component, the API will assign sequential
        identifiers to the components in the message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("type", "id")

    __repr_attributes__: ClassVar[tuple[str, ...]]

    # subclasses are expected to overwrite this if they're only usable with `MessageFlags.is_components_v2`
    is_v2: ClassVar[bool] = False

    type: ComponentType
    id: int

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_attributes__)
        return f"<{self.__class__.__name__} {attrs}>"

    @classmethod
    def _raw_construct(cls, **kwargs) -> Self:
        self = cls.__new__(cls)
        for slot in get_slots(cls):
            try:
                value = kwargs[slot]
            except KeyError:
                pass
            else:
                setattr(self, slot, value)
        return self

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


class ActionRow(Component, Generic[ActionRowChildComponentT]):
    r"""Represents an action row.

    This is a component that holds up to 5 children components in a row.

    This inherits from :class:`Component`.

    .. versionadded:: 2.0

    Attributes
    ----------
    children: :class:`list`\[:class:`Button` | :class:`BaseSelectMenu` | :class:`TextInput`]
        The children components that this holds, if any.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("children",)

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    def __init__(self, data: ActionRowPayload) -> None:
        self.type: Literal[ComponentType.action_row] = ComponentType.action_row
        self.id = data.get("id", 0)

        children = [_component_factory(d) for d in data.get("components", [])]
        self.children: list[ActionRowChildComponentT] = children  # pyright: ignore[reportAttributeAccessIssue]

    def to_dict(self) -> ActionRowPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "components": [child.to_dict() for child in self.children],
        }


class Button(Component):
    """Represents a button from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        The user constructible and usable type to create a button is :class:`disnake.ui.Button`,
        not this one.

    .. versionadded:: 2.0

    Attributes
    ----------
    style: :class:`.ButtonStyle`
        The style of the button.
    custom_id: :class:`str` | :data:`None`
        The ID of the button that gets received during an interaction.
        If this button is for a URL or an SKU, it does not have a custom ID.
    url: :class:`str` | :data:`None`
        The URL this button sends you to.
    disabled: :class:`bool`
        Whether the button is disabled or not.
    label: :class:`str` | :data:`None`
        The label of the button, if any.
    emoji: :class:`PartialEmoji` | :data:`None`
        The emoji of the button, if available.
    sku_id: :class:`int` | :data:`None`
        The ID of a purchasable SKU, for premium buttons.
        Premium buttons additionally cannot have a ``label``, ``url``, or ``emoji``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = (
        "style",
        "custom_id",
        "url",
        "disabled",
        "label",
        "emoji",
        "sku_id",
    )

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    def __init__(self, data: ButtonComponentPayload) -> None:
        self.type: Literal[ComponentType.button] = ComponentType.button
        self.id = data.get("id", 0)

        self.style: ButtonStyle = try_enum(ButtonStyle, data["style"])
        self.custom_id: str | None = data.get("custom_id")
        self.url: str | None = data.get("url")
        self.disabled: bool = data.get("disabled", False)
        self.label: str | None = data.get("label")
        self.emoji: PartialEmoji | None = None
        if emoji_data := data.get("emoji"):
            self.emoji = PartialEmoji.from_dict(emoji_data)

        self.sku_id: int | None = _get_as_snowflake(data, "sku_id")

    def to_dict(self) -> ButtonComponentPayload:
        payload: ButtonComponentPayload = {
            "type": self.type.value,
            "id": self.id,
            "style": self.style.value,
            "disabled": self.disabled,
        }

        if self.label:
            payload["label"] = self.label

        if self.custom_id:
            payload["custom_id"] = self.custom_id

        if self.url:
            payload["url"] = self.url

        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()

        if self.sku_id:
            payload["sku_id"] = self.sku_id

        return payload


class BaseSelectMenu(Component):
    r"""Represents an abstract select menu from the Discord Bot UI Kit.

    A select menu is functionally the same as a dropdown, however
    on mobile it renders a bit differently.

    The currently supported select menus are:

    - :class:`~disnake.StringSelectMenu`
    - :class:`~disnake.UserSelectMenu`
    - :class:`~disnake.RoleSelectMenu`
    - :class:`~disnake.MentionableSelectMenu`
    - :class:`~disnake.ChannelSelectMenu`

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: :class:`str` | :data:`None`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    options: :class:`list`\[:class:`SelectOption`]
        A list of options that can be selected in this select menu.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: :class:`list`\[:class:`SelectDefaultValue`]
        The list of values (users/roles/channels) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.
        Only available for auto-populated select menus.

        .. versionadded:: 2.10
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "placeholder",
        "min_values",
        "max_values",
        "disabled",
        "default_values",
        "required",
    )

    # FIXME: this isn't pretty; we should decouple __repr__ from slots
    __repr_attributes__: ClassVar[tuple[str, ...]] = tuple(
        s for s in __slots__ if s != "default_values"
    )

    # n.b: ideally this would be `BaseSelectMenuPayload`,
    # but pyright made TypedDict keys invariant and doesn't
    # fully support readonly items yet (which would help avoid this)
    def __init__(self, data: AnySelectMenuPayload) -> None:
        component_type = try_enum(ComponentType, data["type"])
        self.type: SelectMenuType = component_type  # pyright: ignore[reportAttributeAccessIssue]
        self.id = data.get("id", 0)

        self.custom_id: str = data["custom_id"]
        self.placeholder: str | None = data.get("placeholder")
        self.min_values: int = data.get("min_values", 1)
        self.max_values: int = data.get("max_values", 1)
        self.disabled: bool = data.get("disabled", False)
        self.default_values: list[SelectDefaultValue] = [
            SelectDefaultValue._from_dict(d) for d in (data.get("default_values") or [])
        ]
        self.required: bool = data.get("required", True)

    def to_dict(self) -> BaseSelectMenuPayload:
        payload: BaseSelectMenuPayload = {
            "type": self.type.value,
            "id": self.id,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
            "required": self.required,
        }

        if self.placeholder:
            payload["placeholder"] = self.placeholder

        if self.default_values:
            payload["default_values"] = [v.to_dict() for v in self.default_values]

        return payload


class StringSelectMenu(BaseSelectMenu):
    r"""Represents a string select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        string select menu is :class:`disnake.ui.StringSelect`.

    .. versionadded:: 2.0

    .. versionchanged:: 2.7
        Renamed from ``SelectMenu`` to ``StringSelectMenu``.

    Attributes
    ----------
    custom_id: :class:`str` | :data:`None`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    options: :class:`list`\[:class:`SelectOption`]
        A list of options that can be selected in this select menu.
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("options",)

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        *BaseSelectMenu.__repr_attributes__,
        *__slots__,
    )
    type: Literal[ComponentType.string_select]

    def __init__(self, data: StringSelectMenuPayload) -> None:
        super().__init__(data)
        self.options: list[SelectOption] = [
            SelectOption.from_dict(option) for option in data.get("options", [])
        ]

    def to_dict(self) -> StringSelectMenuPayload:
        payload = cast("StringSelectMenuPayload", super().to_dict())
        payload["options"] = [op.to_dict() for op in self.options]
        return payload


SelectMenu = StringSelectMenu  # backwards compatibility


class UserSelectMenu(BaseSelectMenu):
    r"""Represents a user select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        user select menu is :class:`disnake.ui.UserSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: :class:`str` | :data:`None`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: :class:`list`\[:class:`SelectDefaultValue`]
        The list of values (users/members) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ()

    type: Literal[ComponentType.user_select]

    if TYPE_CHECKING:

        def to_dict(self) -> UserSelectMenuPayload:
            return cast("UserSelectMenuPayload", super().to_dict())


class RoleSelectMenu(BaseSelectMenu):
    r"""Represents a role select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        role select menu is :class:`disnake.ui.RoleSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: :class:`str` | :data:`None`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: :class:`list`\[:class:`SelectDefaultValue`]
        The list of values (roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ()

    type: Literal[ComponentType.role_select]

    if TYPE_CHECKING:

        def to_dict(self) -> RoleSelectMenuPayload:
            return cast("RoleSelectMenuPayload", super().to_dict())


class MentionableSelectMenu(BaseSelectMenu):
    r"""Represents a mentionable (user/member/role) select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        mentionable select menu is :class:`disnake.ui.MentionableSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: :class:`str` | :data:`None`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: :class:`list`\[:class:`SelectDefaultValue`]
        The list of values (users/roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ()

    type: Literal[ComponentType.mentionable_select]

    if TYPE_CHECKING:

        def to_dict(self) -> MentionableSelectMenuPayload:
            return cast("MentionableSelectMenuPayload", super().to_dict())


class ChannelSelectMenu(BaseSelectMenu):
    r"""Represents a channel select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        channel select menu is :class:`disnake.ui.ChannelSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: :class:`str` | :data:`None`
        The ID of the select menu that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    channel_types: :class:`list`\[:class:`ChannelType`] | :data:`None`
        A list of channel types that can be selected in this select menu.
        If :data:`None`, channels of all types may be selected.
    default_values: :class:`list`\[:class:`SelectDefaultValue`]
        The list of values (channels) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    required: :class:`bool`
        Whether the select menu is required. Only applies to components in modals.
        Defaults to ``True``.

        .. versionadded:: 2.11
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("channel_types",)

    __repr_attributes__: ClassVar[tuple[str, ...]] = (
        *BaseSelectMenu.__repr_attributes__,
        *__slots__,
    )
    type: Literal[ComponentType.channel_select]

    def __init__(self, data: ChannelSelectMenuPayload) -> None:
        super().__init__(data)
        # on the API side, an empty list is (currently) equivalent to no value
        channel_types = data.get("channel_types")
        self.channel_types: list[ChannelType] | None = (
            [try_enum(ChannelType, t) for t in channel_types] if channel_types else None
        )

    def to_dict(self) -> ChannelSelectMenuPayload:
        payload = cast("ChannelSelectMenuPayload", super().to_dict())
        if self.channel_types:
            payload["channel_types"] = [t.value for t in self.channel_types]
        return payload


class SelectOption:
    """Represents a string select menu's option.

    These can be created by users.

    .. versionadded:: 2.0

    Attributes
    ----------
    label: :class:`str`
        The label of the option. This is displayed to users.
        Can only be up to 100 characters.
    value: :class:`str`
        The value of the option. This is not displayed to users.
        If not provided when constructed then it defaults to the
        label. Can only be up to 100 characters.
    description: :class:`str` | :data:`None`
        An additional description of the option, if any.
        Can only be up to 100 characters.
    emoji: :class:`str` | :class:`Emoji` | :class:`PartialEmoji` | :data:`None`
        The emoji of the option, if available.
    default: :class:`bool`
        Whether this option is selected by default.
    """

    __slots__: tuple[str, ...] = (
        "label",
        "value",
        "description",
        "emoji",
        "default",
    )

    def __init__(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
        default: bool = False,
    ) -> None:
        self.label = label
        self.value = label if value is MISSING else value
        self.description = description

        if emoji is not None:
            if isinstance(emoji, str):
                emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                emoji = emoji._to_partial()
            else:
                msg = f"expected emoji to be str, Emoji, or PartialEmoji not {emoji.__class__}"
                raise TypeError(msg)

        self.emoji = emoji
        self.default = default

    def __repr__(self) -> str:
        return (
            f"<SelectOption label={self.label!r} value={self.value!r} description={self.description!r} "
            f"emoji={self.emoji!r} default={self.default!r}>"
        )

    def __str__(self) -> str:
        if self.emoji:
            base = f"{self.emoji} {self.label}"
        else:
            base = self.label

        if self.description:
            return f"{base}\n{self.description}"
        return base

    @classmethod
    def from_dict(cls, data: SelectOptionPayload) -> SelectOption:
        emoji = None
        if emoji_data := data.get("emoji"):
            emoji = PartialEmoji.from_dict(emoji_data)

        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            emoji=emoji,
            default=data.get("default", False),
        )

    def to_dict(self) -> SelectOptionPayload:
        payload: SelectOptionPayload = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }

        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()

        if self.description:
            payload["description"] = self.description

        return payload


class SelectDefaultValue:
    """Represents a default value of an auto-populated select menu (currently all
    select menu types except :class:`StringSelectMenu`).

    Depending on the :attr:`type` attribute, this can represent different types of objects.

    .. versionadded:: 2.10

    Attributes
    ----------
    id: :class:`int`
        The ID of the target object.
    type: :class:`SelectDefaultValueType`
        The type of the target object.
    """

    __slots__: tuple[str, ...] = ("id", "type")

    def __init__(self, id: int, type: SelectDefaultValueType) -> None:
        self.id: int = id
        self.type: SelectDefaultValueType = type

    @classmethod
    def _from_dict(cls, data: SelectDefaultValuePayload) -> Self:
        return cls(int(data["id"]), try_enum(SelectDefaultValueType, data["type"]))

    def to_dict(self) -> SelectDefaultValuePayload:
        return {
            "id": self.id,
            "type": self.type.value,
        }

    def __repr__(self) -> str:
        return f"<SelectDefaultValue id={self.id!r} type={self.type.value!r}>"


class TextInput(Component):
    """Represents a text input from the Discord Bot UI Kit.

    .. versionadded:: 2.4

    .. note::

        The user constructible and usable type to create a text input is
        :class:`disnake.ui.TextInput`, not this one.

    Attributes
    ----------
    style: :class:`TextInputStyle`
        The style of the text input.
    label: :class:`str` | :data:`None`
        The label of the text input.

        .. deprecated:: 2.11
            Deprecated in favor of :class:`Label`.

    custom_id: :class:`str`
        The ID of the text input that gets received during an interaction.
    placeholder: :class:`str` | :data:`None`
        The placeholder text that is shown if nothing is entered.
    value: :class:`str` | :data:`None`
        The pre-filled text of the text input.
    required: :class:`bool`
        Whether the text input is required. Defaults to ``True``.
    min_length: :class:`int` | :data:`None`
        The minimum length of the text input.
    max_length: :class:`int` | :data:`None`
        The maximum length of the text input.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = (
        "style",
        "custom_id",
        "label",
        "placeholder",
        "value",
        "required",
        "max_length",
        "min_length",
    )

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    def __init__(self, data: TextInputPayload) -> None:
        self.type: Literal[ComponentType.text_input] = ComponentType.text_input
        self.id = data.get("id", 0)

        self.custom_id: str = data["custom_id"]
        self.style: TextInputStyle = try_enum(
            TextInputStyle, data.get("style", TextInputStyle.short.value)
        )
        self.label: str | None = data.get("label")  # deprecated
        self.placeholder: str | None = data.get("placeholder")
        self.value: str | None = data.get("value")
        self.required: bool = data.get("required", True)
        self.min_length: int | None = data.get("min_length")
        self.max_length: int | None = data.get("max_length")

    def to_dict(self) -> TextInputPayload:
        payload: TextInputPayload = {
            "type": self.type.value,
            "id": self.id,
            "style": self.style.value,
            "label": self.label,
            "custom_id": self.custom_id,
            "required": self.required,
        }

        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder

        if self.value is not None:
            payload["value"] = self.value

        if self.min_length is not None:
            payload["min_length"] = self.min_length

        if self.max_length is not None:
            payload["max_length"] = self.max_length

        return payload


class Section(Component):
    r"""Represents a section from the Discord Bot UI Kit (v2).

    This allows displaying an accessory (thumbnail or button) next to a block of text.

    .. note::
        The user constructible and usable type to create a
        section is :class:`disnake.ui.Section`.

    .. versionadded:: 2.11

    Attributes
    ----------
    children: :class:`list`\[:class:`TextDisplay`]
        The text items in this section.
    accessory: :class:`Thumbnail` | :class:`Button`
        The accessory component displayed next to the section text.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("children", "accessory")

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: SectionComponentPayload) -> None:
        self.type: Literal[ComponentType.section] = ComponentType.section
        self.id = data.get("id", 0)

        self.children: list[SectionChildComponent] = [
            _component_factory(d, type=SectionChildComponent) for d in data.get("components", [])
        ]

        accessory = _component_factory(data["accessory"])
        self.accessory: SectionAccessoryComponent = accessory  # pyright: ignore[reportAttributeAccessIssue]

    def to_dict(self) -> SectionComponentPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "accessory": self.accessory.to_dict(),
            "components": [child.to_dict() for child in self.children],
        }


class TextDisplay(Component):
    """Represents a text display from the Discord Bot UI Kit (v2).

    .. note::
        The user constructible and usable type to create a
        text display is :class:`disnake.ui.TextDisplay`.

    .. versionadded:: 2.11

    Attributes
    ----------
    content: :class:`str`
        The text displayed by this component.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("content",)

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: TextDisplayComponentPayload) -> None:
        self.type: Literal[ComponentType.text_display] = ComponentType.text_display
        self.id = data.get("id", 0)

        self.content: str = data["content"]

    def to_dict(self) -> TextDisplayComponentPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "content": self.content,
        }


class UnfurledMediaItem:
    """Represents an unfurled/resolved media item within a component.

    .. versionadded:: 2.11

    Attributes
    ----------
    url: :class:`str`
        The URL of this media item.
    proxy_url: :class:`str`
        The proxied URL of this media item. This is a cached version of
        the :attr:`url` in the case of images.
    height: :class:`int` | :data:`None`
        The height of this media item, if applicable.
    width: :class:`int` | :data:`None`
        The width of this media item, if applicable.
    content_type: :class:`str` | :data:`None`
        The `media type <https://en.wikipedia.org/wiki/Media_type>`_ of this media item.
    attachment_id: :class:`int` | :data:`None`
        The ID of the uploaded attachment. Only present if the media item was
        uploaded as an attachment.
    """

    __slots__: tuple[str, ...] = (
        "url",
        "proxy_url",
        "height",
        "width",
        "content_type",
        "attachment_id",
    )

    # generally, users should also be able to pass a plain url where applicable instead of
    # an UnfurledMediaItem instance; this is largely for internal use
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.proxy_url: str | None = None
        self.height: int | None = None
        self.width: int | None = None
        self.content_type: str | None = None
        self.attachment_id: int | None = None

    @classmethod
    def from_dict(cls, data: UnfurledMediaItemPayload) -> Self:
        self = cls(data["url"])
        self.proxy_url = data.get("proxy_url")
        self.height = _get_as_snowflake(data, "height")
        self.width = _get_as_snowflake(data, "width")
        self.content_type = data.get("content_type")
        self.attachment_id = _get_as_snowflake(data, "attachment_id")
        return self

    def to_dict(self) -> UnfurledMediaItemPayload:
        # for sending, only `url` is required, and other fields are ignored regardless
        return {"url": self.url}

    def __repr__(self) -> str:
        return f"<UnfurledMediaItem url={self.url} content_type={self.content_type}>"


class Thumbnail(Component):
    """Represents a thumbnail from the Discord Bot UI Kit (v2).

    This is only supported as the :attr:`~Section.accessory` of a section component.

    .. note::
        The user constructible and usable type to create a
        thumbnail is :class:`disnake.ui.Thumbnail`.

    .. versionadded:: 2.11

    Attributes
    ----------
    media: :class:`UnfurledMediaItem`
        The media item to display. Can be an arbitrary URL or attachment
        reference (``attachment://<filename>``).
    description: :class:`str` | :data:`None`
        The thumbnail's description ("alt text"), if any.
    spoiler: :class:`bool`
        Whether the thumbnail is marked as a spoiler. Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = (
        "media",
        "description",
        "spoiler",
    )

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: ThumbnailComponentPayload) -> None:
        self.type: Literal[ComponentType.thumbnail] = ComponentType.thumbnail
        self.id = data.get("id", 0)

        self.media: UnfurledMediaItem = UnfurledMediaItem.from_dict(data["media"])
        self.description: str | None = data.get("description")
        self.spoiler: bool = data.get("spoiler", False)

    def to_dict(self) -> ThumbnailComponentPayload:
        payload: ThumbnailComponentPayload = {
            "type": self.type.value,
            "id": self.id,
            "media": self.media.to_dict(),
            "spoiler": self.spoiler,
        }

        if self.description:
            payload["description"] = self.description

        return payload


class MediaGallery(Component):
    r"""Represents a media gallery from the Discord Bot UI Kit (v2).

    This allows displaying up to 10 images in a gallery.

    .. note::
        The user constructible and usable type to create a
        media gallery is :class:`disnake.ui.MediaGallery`.

    .. versionadded:: 2.11

    Attributes
    ----------
    items: :class:`list`\[:class:`MediaGalleryItem`]
        The images in this gallery.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("items",)

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: MediaGalleryComponentPayload) -> None:
        self.type: Literal[ComponentType.media_gallery] = ComponentType.media_gallery
        self.id = data.get("id", 0)

        self.items: list[MediaGalleryItem] = [MediaGalleryItem.from_dict(i) for i in data["items"]]

    def to_dict(self) -> MediaGalleryComponentPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "items": [i.to_dict() for i in self.items],
        }


class MediaGalleryItem:
    """Represents an item inside a :class:`MediaGallery`.

    .. versionadded:: 2.11

    Parameters
    ----------
    media: :class:`str` | :class:`.Asset` | :class:`.Attachment` | :class:`.UnfurledMediaItem`
        The media item to display. Can be an arbitrary URL or attachment
        reference (``attachment://<filename>``).
    description: :class:`str` | :data:`None`
        The item's description ("alt text"), if any.
    spoiler: :class:`bool`
        Whether the item is marked as a spoiler. Defaults to ``False``.
    """

    __slots__: tuple[str, ...] = (
        "media",
        "description",
        "spoiler",
    )

    def __init__(
        self,
        media: MediaItemInput,
        description: str | None = None,
        *,
        spoiler: bool = False,
    ) -> None:
        self.media: UnfurledMediaItem = handle_media_item_input(media)
        self.description: str | None = description
        self.spoiler: bool = spoiler

    @classmethod
    def from_dict(cls, data: MediaGalleryItemPayload) -> Self:
        return cls(
            media=UnfurledMediaItem.from_dict(data["media"]),
            description=data.get("description"),
            spoiler=data.get("spoiler", False),
        )

    def to_dict(self) -> MediaGalleryItemPayload:
        payload: MediaGalleryItemPayload = {
            "media": self.media.to_dict(),
            "spoiler": self.spoiler,
        }

        if self.description:
            payload["description"] = self.description

        return payload

    def __repr__(self) -> str:
        return f"<MediaGalleryItem media={self.media!r} description={self.description!r}>"


class FileComponent(Component):
    """Represents a file component from the Discord Bot UI Kit (v2).

    This allows displaying attached files.

    .. note::
        The user constructible and usable type to create a
        file component is :class:`disnake.ui.File`.

    .. versionadded:: 2.11

    Attributes
    ----------
    file: :class:`UnfurledMediaItem`
        The file to display. This **only** supports attachment references (i.e.
        using the ``attachment://<filename>`` syntax), not arbitrary URLs.
    spoiler: :class:`bool`
        Whether the file is marked as a spoiler. Defaults to ``False``.
    name: :class:`str` | :data:`None`
        The name of the file.
        This is available in objects from the API, and ignored when sending.
    size: :class:`int` | :data:`None`
        The size of the file.
        This is available in objects from the API, and ignored when sending.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("file", "spoiler", "name", "size")

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: FileComponentPayload) -> None:
        self.type: Literal[ComponentType.file] = ComponentType.file
        self.id = data.get("id", 0)

        self.file: UnfurledMediaItem = UnfurledMediaItem.from_dict(data["file"])
        self.spoiler: bool = data.get("spoiler", False)

        self.name: str | None = data.get("name")
        self.size: int | None = data.get("size")

    def to_dict(self) -> FileComponentPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "file": self.file.to_dict(),
            "spoiler": self.spoiler,
        }


class Separator(Component):
    """Represents a separator from the Discord Bot UI Kit (v2).

    This allows vertically separating components.

    .. note::
        The user constructible and usable type to create a
        separator is :class:`disnake.ui.Separator`.

    .. versionadded:: 2.11

    Attributes
    ----------
    divider: :class:`bool`
        Whether the separator should be visible, instead of just being vertical padding/spacing.
        Defaults to ``True``.
    spacing: :class:`SeparatorSpacing`
        The size of the separator padding.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = ("divider", "spacing")

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: SeparatorComponentPayload) -> None:
        self.type: Literal[ComponentType.separator] = ComponentType.separator
        self.id = data.get("id", 0)

        self.divider: bool = data.get("divider", True)
        self.spacing: SeparatorSpacing = try_enum(SeparatorSpacing, data.get("spacing", 1))

    def to_dict(self) -> SeparatorComponentPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "divider": self.divider,
            "spacing": self.spacing.value,
        }


class Container(Component):
    r"""Represents a container from the Discord Bot UI Kit (v2).

    This is visually similar to :class:`Embed`\s, and contains other components.

    .. note::
        The user constructible and usable type to create a
        container is :class:`disnake.ui.Container`.

    .. versionadded:: 2.11

    Attributes
    ----------
    children: :class:`list`\[:class:`ActionRow` | :class:`Section` | :class:`TextDisplay` | :class:`MediaGallery` | :class:`FileComponent` | :class:`Separator`]
        The child components in this container.
    accent_colour: :class:`Colour` | :data:`None`
        The accent colour of the container. An alias exists under ``accent_color``.
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler. Defaults to ``False``.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.

        .. versionadded:: 2.11
    """

    __slots__: tuple[str, ...] = (
        "children",
        "accent_colour",
        "spoiler",
    )

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    is_v2 = True

    def __init__(self, data: ContainerComponentPayload) -> None:
        self.type: Literal[ComponentType.container] = ComponentType.container
        self.id = data.get("id", 0)

        components = [_component_factory(d) for d in data.get("components", [])]
        self.children: list[ContainerChildComponent] = components  # pyright: ignore[reportAttributeAccessIssue]

        self.accent_colour: Colour | None = (
            Colour(accent_color) if (accent_color := data.get("accent_color")) is not None else None
        )
        self.spoiler: bool = data.get("spoiler", False)

    def to_dict(self) -> ContainerComponentPayload:
        payload: ContainerComponentPayload = {
            "type": self.type.value,
            "id": self.id,
            "spoiler": self.spoiler,
            "components": [child.to_dict() for child in self.children],
        }

        if self.accent_colour is not None:
            payload["accent_color"] = self.accent_colour.value

        return payload

    @property
    def accent_color(self) -> Colour | None:
        """:class:`Colour` | :data:`None`: The accent color of the container.
        An alias exists under ``accent_colour``.
        """
        return self.accent_colour


class Label(Component):
    """Represents a label from the Discord Bot UI Kit.

    This wraps other components with a label and an optional description,
    and can only be used in modals.

    .. versionadded:: 2.11

    .. note::

        The user constructible and usable type to create a label is
        :class:`disnake.ui.Label`, not this one.

    Attributes
    ----------
    text: :class:`str`
        The label text.
    description: :class:`str` | :data:`None`
        The description text for the label.
    component: :class:`TextInput` | :class:`FileUpload` | :class:`BaseSelectMenu`
        The component within the label.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a message.
    """

    __slots__: tuple[str, ...] = (
        "text",
        "description",
        "component",
    )

    __repr_info__: ClassVar[tuple[str, ...]] = __slots__

    def __init__(self, data: LabelComponentPayload) -> None:
        self.type: Literal[ComponentType.label] = ComponentType.label
        self.id = data.get("id", 0)

        self.text: str = data["label"]
        self.description: str | None = data.get("description")

        component = _component_factory(data["component"])
        self.component: LabelChildComponent = component  # pyright: ignore[reportAttributeAccessIssue]

    def to_dict(self) -> LabelComponentPayload:
        payload: LabelComponentPayload = {
            "type": self.type.value,
            "id": self.id,
            "label": self.text,
            "component": self.component.to_dict(),
        }

        if self.description is not None:
            payload["description"] = self.description

        return payload


class FileUpload(Component):
    """Represents a file upload component from the Discord Bot UI Kit.

    This allows you to receive files from users, and can only be used in modals.

    .. note::
        The user constructible and usable type to create a
        file upload is :class:`disnake.ui.FileUpload`.

    .. versionadded:: |vnext|

    Attributes
    ----------
    custom_id: :class:`str`
        The ID of the file upload that gets received during an interaction.
    min_values: :class:`int`
        The minimum number of files that must be uploaded.
        Defaults to 1 and must be between 0 and 10.
    max_values: :class:`int`
        The maximum number of files that must be uploaded.
        Defaults to 1 and must be between 1 and 10.
    required: :class:`bool`
        Whether the file upload is required.
        Defaults to ``True``.
    id: :class:`int`
        The numeric identifier for the component.
        This is always present in components received from the API,
        and unique within a modal.
    """

    __slots__: tuple[str, ...] = (
        "custom_id",
        "min_values",
        "max_values",
        "required",
    )

    __repr_attributes__: ClassVar[tuple[str, ...]] = __slots__

    def __init__(self, data: FileUploadComponentPayload) -> None:
        self.type: Literal[ComponentType.file_upload] = ComponentType.file_upload
        self.id = data.get("id", 0)

        self.custom_id: str = data["custom_id"]
        self.min_values: int = data.get("min_values", 1)
        self.max_values: int = data.get("max_values", 1)
        self.required: bool = data.get("required", True)

    def to_dict(self) -> FileUploadComponentPayload:
        return {
            "type": self.type.value,
            "id": self.id,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "required": self.required,
        }


# types of components that are allowed in a message's action rows;
# see also `ActionRowMessageComponent` type alias
VALID_ACTION_ROW_MESSAGE_COMPONENT_TYPES: Final = (
    Button,
    StringSelectMenu,
    UserSelectMenu,
    RoleSelectMenu,
    MentionableSelectMenu,
    ChannelSelectMenu,
)


def handle_media_item_input(value: MediaItemInput) -> UnfurledMediaItem:
    if isinstance(value, UnfurledMediaItem):
        return value
    elif isinstance(value, str):
        return UnfurledMediaItem(value)

    # circular import
    from .message import Attachment

    if isinstance(value, (AssetMixin, Attachment)):
        return UnfurledMediaItem(value.url)

    assert_never(value)
    msg = f"{type(value).__name__} cannot be converted to UnfurledMediaItem"
    raise TypeError(msg)


C = TypeVar("C", bound="Component")


COMPONENT_LOOKUP: Mapping[ComponentTypeLiteral, type[Component]] = {
    ComponentType.action_row.value: ActionRow,
    ComponentType.button.value: Button,
    ComponentType.string_select.value: StringSelectMenu,
    ComponentType.text_input.value: TextInput,
    ComponentType.user_select.value: UserSelectMenu,
    ComponentType.role_select.value: RoleSelectMenu,
    ComponentType.mentionable_select.value: MentionableSelectMenu,
    ComponentType.channel_select.value: ChannelSelectMenu,
    ComponentType.section.value: Section,
    ComponentType.text_display.value: TextDisplay,
    ComponentType.thumbnail.value: Thumbnail,
    ComponentType.media_gallery.value: MediaGallery,
    ComponentType.file.value: FileComponent,
    ComponentType.separator.value: Separator,
    ComponentType.container.value: Container,
    ComponentType.label.value: Label,
    ComponentType.file_upload.value: FileUpload,
}


# NOTE: The type param is purely for type-checking, it has no implications on runtime behavior.
# FIXME: could be improved with https://peps.python.org/pep-0747/
def _component_factory(data: ComponentPayload, *, type: type[C] = Component) -> C:
    component_type = data["type"]

    try:
        component_cls = COMPONENT_LOOKUP[component_type]
    except KeyError:
        # if we encounter an unknown component type, just construct a placeholder component for it
        as_enum = try_enum(ComponentType, component_type)
        return Component._raw_construct(type=as_enum)  # pyright: ignore[reportReturnType]
    else:
        return component_cls(data)  # pyright: ignore[reportCallIssue, reportReturnType]


# this is just a rebranded _component_factory, as a workaround to Python not supporting typescript-like mapped types
if TYPE_CHECKING:

    def _message_component_factory(
        data: MessageTopLevelComponentPayload,
    ) -> MessageTopLevelComponent: ...

else:
    _message_component_factory = _component_factory
