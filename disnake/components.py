# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Final,
    Generic,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from .colour import Colour
from .enums import (
    ButtonStyle,
    ChannelType,
    ComponentType,
    SelectDefaultValueType,
    SeparatorSpacingSize,
    TextInputStyle,
    try_enum,
)
from .partial_emoji import PartialEmoji, _EmojiTag
from .utils import MISSING, _get_as_snowflake, get_slots

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

    from .emoji import Emoji
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
    "Thumbnail",
    "MediaGallery",
    "MediaGalleryItem",
    "FileComponent",
    "Separator",
    "Container",
)

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
ActionRowMessageComponent = Union["Button", "AnySelectMenu"]
ActionRowModalComponent: TypeAlias = "TextInput"

# any child component type of action rows
ActionRowChildComponent = Union[ActionRowMessageComponent, ActionRowModalComponent]
# TODO: this might have to be covariant
ActionRowChildComponentT = TypeVar("ActionRowChildComponentT", bound=ActionRowChildComponent)

# valid `Section.accessory` types
SectionAccessoryComponent = Union["Thumbnail", "Button"]
# valid `Section.components` item types
SectionChildComponent: TypeAlias = "TextDisplay"

# valid `Container.components` item types
ContainerChildComponent = Union[
    "ActionRow[ActionRowMessageComponent]",
    "Section",
    "TextDisplay",
    "MediaGallery",
    "FileComponent",
    "Separator",
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
MessageTopLevelComponent = Union[MessageTopLevelComponentV1, MessageTopLevelComponentV2]


class Component:
    """Represents a Discord Bot UI Kit Component.

    Currently, the only components supported by Discord are:

    - :class:`ActionRow`
    - :class:`Button`
    - subtypes of :class:`BaseSelectMenu` (:class:`ChannelSelectMenu`, :class:`MentionableSelectMenu`, :class:`RoleSelectMenu`, :class:`StringSelectMenu`, :class:`UserSelectMenu`)
    - :class:`TextInput`

    ..
        TODO: add cv2 components to list

    This class is abstract and cannot be instantiated.

    .. versionadded:: 2.0

    Attributes
    ----------
    type: :class:`ComponentType`
        The type of component.
    """

    __slots__: Tuple[str, ...] = ("type",)

    __repr_info__: ClassVar[Tuple[str, ...]]
    type: ComponentType

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_info__)
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

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


class ActionRow(Component, Generic[ActionRowChildComponentT]):
    """Represents an action row.

    This is a component that holds up to 5 children components in a row.

    This inherits from :class:`Component`.

    .. versionadded:: 2.0

    Attributes
    ----------
    children: List[Union[:class:`Button`, :class:`BaseSelectMenu`, :class:`TextInput`]]
        The children components that this holds, if any.
    """

    __slots__: Tuple[str, ...] = ("children",)

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: ActionRowPayload) -> None:
        self.type: Literal[ComponentType.action_row] = ComponentType.action_row
        children = [_component_factory(d) for d in data.get("components", [])]
        self.children: List[ActionRowChildComponentT] = children  # type: ignore

    def to_dict(self) -> ActionRowPayload:
        return {
            "type": self.type.value,
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
    custom_id: Optional[:class:`str`]
        The ID of the button that gets received during an interaction.
        If this button is for a URL or an SKU, it does not have a custom ID.
    url: Optional[:class:`str`]
        The URL this button sends you to.
    disabled: :class:`bool`
        Whether the button is disabled or not.
    label: Optional[:class:`str`]
        The label of the button, if any.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji of the button, if available.
    sku_id: Optional[:class:`int`]
        The ID of a purchasable SKU, for premium buttons.
        Premium buttons additionally cannot have a ``label``, ``url``, or ``emoji``.

        .. versionadded:: 2.11
    """

    __slots__: Tuple[str, ...] = (
        "style",
        "custom_id",
        "url",
        "disabled",
        "label",
        "emoji",
        "sku_id",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: ButtonComponentPayload) -> None:
        self.type: Literal[ComponentType.button] = ComponentType.button
        self.style: ButtonStyle = try_enum(ButtonStyle, data["style"])
        self.custom_id: Optional[str] = data.get("custom_id")
        self.url: Optional[str] = data.get("url")
        self.disabled: bool = data.get("disabled", False)
        self.label: Optional[str] = data.get("label")
        self.emoji: Optional[PartialEmoji]
        try:
            self.emoji = PartialEmoji.from_dict(data["emoji"])
        except KeyError:
            self.emoji = None

        self.sku_id: Optional[int] = _get_as_snowflake(data, "sku_id")

    def to_dict(self) -> ButtonComponentPayload:
        payload: ButtonComponentPayload = {
            "type": self.type.value,
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
    """Represents an abstract select menu from the Discord Bot UI Kit.

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
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    options: List[:class:`SelectOption`]
        A list of options that can be selected in this select menu.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: List[:class:`SelectDefaultValue`]
        The list of values (users/roles/channels) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.
        Only available for auto-populated select menus.

        .. versionadded:: 2.10
    """

    __slots__: Tuple[str, ...] = (
        "custom_id",
        "placeholder",
        "min_values",
        "max_values",
        "disabled",
        "default_values",
    )

    # FIXME: this isn't pretty; we should decouple __repr__ from slots
    __repr_info__: ClassVar[Tuple[str, ...]] = tuple(s for s in __slots__ if s != "default_values")

    # n.b: ideally this would be `BaseSelectMenuPayload`,
    # but pyright made TypedDict keys invariant and doesn't
    # fully support readonly items yet (which would help avoid this)
    def __init__(self, data: AnySelectMenuPayload) -> None:
        component_type = try_enum(ComponentType, data["type"])
        self.type: SelectMenuType = component_type  # type: ignore

        self.custom_id: str = data["custom_id"]
        self.placeholder: Optional[str] = data.get("placeholder")
        self.min_values: int = data.get("min_values", 1)
        self.max_values: int = data.get("max_values", 1)
        self.disabled: bool = data.get("disabled", False)
        self.default_values: List[SelectDefaultValue] = [
            SelectDefaultValue._from_dict(d) for d in (data.get("default_values") or [])
        ]

    def to_dict(self) -> BaseSelectMenuPayload:
        payload: BaseSelectMenuPayload = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }

        if self.placeholder:
            payload["placeholder"] = self.placeholder

        if self.default_values:
            payload["default_values"] = [v.to_dict() for v in self.default_values]

        return payload


class StringSelectMenu(BaseSelectMenu):
    """Represents a string select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        string select menu is :class:`disnake.ui.StringSelect`.

    .. versionadded:: 2.0

    .. versionchanged:: 2.7
        Renamed from ``SelectMenu`` to ``StringSelectMenu``.

    Attributes
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    options: List[:class:`SelectOption`]
        A list of options that can be selected in this select menu.
    """

    __slots__: Tuple[str, ...] = ("options",)

    __repr_info__: ClassVar[Tuple[str, ...]] = BaseSelectMenu.__repr_info__ + __slots__
    type: Literal[ComponentType.string_select]

    def __init__(self, data: StringSelectMenuPayload) -> None:
        super().__init__(data)
        self.options: List[SelectOption] = [
            SelectOption.from_dict(option) for option in data.get("options", [])
        ]

    def to_dict(self) -> StringSelectMenuPayload:
        payload = cast("StringSelectMenuPayload", super().to_dict())
        payload["options"] = [op.to_dict() for op in self.options]
        return payload


SelectMenu = StringSelectMenu  # backwards compatibility


class UserSelectMenu(BaseSelectMenu):
    """Represents a user select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        user select menu is :class:`disnake.ui.UserSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: List[:class:`SelectDefaultValue`]
        The list of values (users/members) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    """

    __slots__: Tuple[str, ...] = ()

    type: Literal[ComponentType.user_select]

    if TYPE_CHECKING:

        def to_dict(self) -> UserSelectMenuPayload:
            return cast("UserSelectMenuPayload", super().to_dict())


class RoleSelectMenu(BaseSelectMenu):
    """Represents a role select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        role select menu is :class:`disnake.ui.RoleSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: List[:class:`SelectDefaultValue`]
        The list of values (roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    """

    __slots__: Tuple[str, ...] = ()

    type: Literal[ComponentType.role_select]

    if TYPE_CHECKING:

        def to_dict(self) -> RoleSelectMenuPayload:
            return cast("RoleSelectMenuPayload", super().to_dict())


class MentionableSelectMenu(BaseSelectMenu):
    """Represents a mentionable (user/member/role) select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        mentionable select menu is :class:`disnake.ui.MentionableSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    default_values: List[:class:`SelectDefaultValue`]
        The list of values (users/roles) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    """

    __slots__: Tuple[str, ...] = ()

    type: Literal[ComponentType.mentionable_select]

    if TYPE_CHECKING:

        def to_dict(self) -> MentionableSelectMenuPayload:
            return cast("MentionableSelectMenuPayload", super().to_dict())


class ChannelSelectMenu(BaseSelectMenu):
    """Represents a channel select menu from the Discord Bot UI Kit.

    .. note::
        The user constructible and usable type to create a
        channel select menu is :class:`disnake.ui.ChannelSelect`.

    .. versionadded:: 2.7

    Attributes
    ----------
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    disabled: :class:`bool`
        Whether the select menu is disabled or not.
    channel_types: Optional[List[:class:`ChannelType`]]
        A list of channel types that can be selected in this select menu.
        If ``None``, channels of all types may be selected.
    default_values: List[:class:`SelectDefaultValue`]
        The list of values (channels) that are selected by default.
        If set, the number of items must be within the bounds set by ``min_values`` and ``max_values``.

        .. versionadded:: 2.10
    """

    __slots__: Tuple[str, ...] = ("channel_types",)

    __repr_info__: ClassVar[Tuple[str, ...]] = BaseSelectMenu.__repr_info__ + __slots__
    type: Literal[ComponentType.channel_select]

    def __init__(self, data: ChannelSelectMenuPayload) -> None:
        super().__init__(data)
        # on the API side, an empty list is (currently) equivalent to no value
        channel_types = data.get("channel_types")
        self.channel_types: Optional[List[ChannelType]] = (
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
    description: Optional[:class:`str`]
        An additional description of the option, if any.
        Can only be up to 100 characters.
    emoji: Optional[Union[:class:`str`, :class:`Emoji`, :class:`PartialEmoji`]]
        The emoji of the option, if available.
    default: :class:`bool`
        Whether this option is selected by default.
    """

    __slots__: Tuple[str, ...] = (
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
        description: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
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
                raise TypeError(
                    f"expected emoji to be str, Emoji, or PartialEmoji not {emoji.__class__}"
                )

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
        try:
            emoji = PartialEmoji.from_dict(data["emoji"])
        except KeyError:
            emoji = None

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

    __slots__: Tuple[str, ...] = ("id", "type")

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
    label: Optional[:class:`str`]
        The label of the text input.
    custom_id: :class:`str`
        The ID of the text input that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is entered.
    value: Optional[:class:`str`]
        The pre-filled text of the text input.
    required: :class:`bool`
        Whether the text input is required. Defaults to ``True``.
    min_length: Optional[:class:`int`]
        The minimum length of the text input.
    max_length: Optional[:class:`int`]
        The maximum length of the text input.
    """

    __slots__: Tuple[str, ...] = (
        "style",
        "custom_id",
        "label",
        "placeholder",
        "value",
        "required",
        "max_length",
        "min_length",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: TextInputPayload) -> None:
        style = data.get("style", TextInputStyle.short.value)

        self.type: Literal[ComponentType.text_input] = ComponentType.text_input
        self.custom_id: str = data["custom_id"]
        self.style: TextInputStyle = try_enum(TextInputStyle, style)
        self.label: Optional[str] = data.get("label")
        self.placeholder: Optional[str] = data.get("placeholder")
        self.value: Optional[str] = data.get("value")
        self.required: bool = data.get("required", True)
        self.min_length: Optional[int] = data.get("min_length")
        self.max_length: Optional[int] = data.get("max_length")

    def to_dict(self) -> TextInputPayload:
        payload: TextInputPayload = {
            "type": self.type.value,
            "style": self.style.value,
            "label": cast(str, self.label),
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
    """Represents a section from the Discord Bot UI Kit (v2).

    This allows displaying an accessory (thumbnail or button) next to a block of text.

    .. note::
        The user constructible and usable type to create a
        section is :class:`disnake.ui.Section`.

    .. versionadded:: 2.11

    Attributes
    ----------
    accessory: Union[:class:`Thumbnail`, :class:`Button`]
        The accessory component displayed next to the section text.
    components: List[:class:`TextDisplay`]
        The text items in this section.
    """

    __slots__: Tuple[str, ...] = ("accessory", "components")

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: SectionComponentPayload) -> None:
        self.type: Literal[ComponentType.section] = ComponentType.section

        accessory = _component_factory(data["accessory"])
        self.accessory: SectionAccessoryComponent = accessory  # type: ignore

        self.components: List[SectionChildComponent] = [
            _component_factory(d, type=SectionChildComponent) for d in data.get("components", [])
        ]

    def to_dict(self) -> SectionComponentPayload:
        return {
            "type": self.type.value,
            "accessory": self.accessory.to_dict(),
            "components": [child.to_dict() for child in self.components],
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
    """

    __slots__: Tuple[str, ...] = ("content",)

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: TextDisplayComponentPayload) -> None:
        self.type: Literal[ComponentType.text_display] = ComponentType.text_display
        self.content: str = data["content"]

    def to_dict(self) -> TextDisplayComponentPayload:
        return {
            "type": self.type.value,
            "content": self.content,
        }


class Thumbnail(Component):
    """Represents a thumbnail from the Discord Bot UI Kit (v2).

    This is only supported as the :attr:`~Section.accessory` of a section component.

    .. note::
        The user constructible and usable type to create a
        thumbnail is :class:`disnake.ui.Thumbnail`.

    .. versionadded:: 2.11

    Attributes
    ----------
    media: Any
        n/a
    description: Optional[:class:`str`]
        The thumbnail's description ("alt text"), if any.
    spoiler: :class:`bool`
        Whether the thumbnail is marked as a spoiler. Defaults to ``False``.
    """

    __slots__: Tuple[str, ...] = (
        "media",
        "description",
        "spoiler",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: ThumbnailComponentPayload) -> None:
        self.type: Literal[ComponentType.thumbnail] = ComponentType.thumbnail
        self.media: Any = data["media"]  # TODO: UnfurledMediaItem
        self.description: Optional[str] = data.get("description")
        self.spoiler: bool = data.get("spoiler", False)

    def to_dict(self) -> ThumbnailComponentPayload:
        payload: ThumbnailComponentPayload = {
            "type": self.type.value,
            "media": self.media,
            "spoiler": self.spoiler,
        }

        if self.description:
            payload["description"] = self.description

        return payload


class MediaGallery(Component):
    """Represents a media gallery from the Discord Bot UI Kit (v2).

    This allows displaying up to 10 images in a gallery.

    .. note::
        The user constructible and usable type to create a
        media gallery is :class:`disnake.ui.MediaGallery`.

    .. versionadded:: 2.11

    Attributes
    ----------
    items: List[:class:`MediaGalleryItem`]
        The images in this gallery.
    """

    __slots__: Tuple[str, ...] = ("items",)

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: MediaGalleryComponentPayload) -> None:
        self.type: Literal[ComponentType.media_gallery] = ComponentType.media_gallery
        self.items: List[MediaGalleryItem] = [MediaGalleryItem(i) for i in data["items"]]

    def to_dict(self) -> MediaGalleryComponentPayload:
        return {
            "type": self.type.value,
            "items": [i.to_dict() for i in self.items],
        }


class MediaGalleryItem:
    """TODO"""

    __slots__: Tuple[str, ...] = (
        "media",
        "description",
        "spoiler",
    )

    # XXX: should this be user-instantiable?
    def __init__(self, data: MediaGalleryItemPayload) -> None:
        self.media: Any = data["media"]  # TODO: UnfurledMediaItem
        self.description: Optional[str] = data.get("description")
        self.spoiler: bool = data.get("spoiler", False)

    def to_dict(self) -> MediaGalleryItemPayload:
        payload: MediaGalleryItemPayload = {
            "media": self.media,
            "spoiler": self.spoiler,
        }

        if self.description:
            payload["description"] = self.description

        return payload

    def __repr__(self) -> str:
        return f"<MediaGalleryItem media={self.media!r} description={self.description!r}>"


# TODO: temporary(?) name to avoid shadowing `disnake.file.File`
class FileComponent(Component):
    """Represents a file component from the Discord Bot UI Kit (v2).

    This allows displaying attached files.

    .. note::
        The user constructible and usable type to create a
        file component is :class:`disnake.ui.File`.

    .. versionadded:: 2.11

    Attributes
    ----------
    file: Any
        n/a
    spoiler: :class:`bool`
        Whether the file is marked as a spoiler. Defaults to ``False``.
    """

    __slots__: Tuple[str, ...] = ("file", "spoiler")

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: FileComponentPayload) -> None:
        self.type: Literal[ComponentType.file] = ComponentType.file
        self.file: Any = data["file"]  # TODO: UnfurledMediaItem
        self.spoiler: bool = data.get("spoiler", False)

    def to_dict(self) -> FileComponentPayload:
        return {
            "type": self.type.value,
            "file": self.file,
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
    spacing: :class:`SeparatorSpacingSize`
        The size of the separator.
    """

    __slots__: Tuple[str, ...] = ("divider", "spacing")

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: SeparatorComponentPayload) -> None:
        self.type: Literal[ComponentType.separator] = ComponentType.separator
        self.divider: bool = data.get("divider", True)
        # TODO: `size` instead of `spacing`?
        self.spacing: SeparatorSpacingSize = try_enum(SeparatorSpacingSize, data.get("spacing", 1))

    def to_dict(self) -> SeparatorComponentPayload:
        return {
            "type": self.type.value,
            "divider": self.divider,
            "spacing": self.spacing.value,
        }


class Container(Component):
    """Represents a container from the Discord Bot UI Kit (v2).

    This is visually similar to :class:`Embed`\\s, and contains other components.

    .. note::
        The user constructible and usable type to create a
        container is :class:`disnake.ui.Container`.

    .. versionadded:: 2.11

    Attributes
    ----------
    spoiler: :class:`bool`
        Whether the container is marked as a spoiler. Defaults to ``False``.
    components: List[Union[:class:`ActionRow`, :class:`Section`, :class:`TextDisplay`, :class:`MediaGallery`, :class:`FileComponent`, :class:`Separator`]]
        The components in this container.
    """

    __slots__: Tuple[str, ...] = (
        "_accent_colour",
        "spoiler",
        "components",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = (
        "accent_colour",
        "spoiler",
        "components",
    )

    def __init__(self, data: ContainerComponentPayload) -> None:
        self.type: Literal[ComponentType.container] = ComponentType.container
        self._accent_colour: Optional[int] = data.get("accent_color")
        self.spoiler: bool = data.get("spoiler", False)

        components = [_component_factory(d) for d in data.get("components", [])]
        self.components: List[ContainerChildComponent] = components  # type: ignore

    def to_dict(self) -> ContainerComponentPayload:
        payload: ContainerComponentPayload = {
            "type": self.type.value,
            "spoiler": self.spoiler,
            "components": [child.to_dict() for child in self.components],
        }

        if self._accent_colour is not None:
            payload["accent_color"] = self._accent_colour

        return payload

    @property
    def accent_colour(self) -> Optional[Colour]:
        """Optional[:class:`Colour`]: Returns the accent colour of the container.
        An alias exists under ``accent_color``.
        """
        return Colour(self._accent_colour) if self._accent_colour is not None else None

    @property
    def accent_color(self) -> Optional[Colour]:
        """Optional[:class:`Colour`]: Returns the accent color of the container.
        An alias exists under ``accent_colour``.
        """
        return self.accent_colour


# see ActionRowMessageComponent
VALID_ACTION_ROW_MESSAGE_TYPES: Final = (
    Button,
    StringSelectMenu,
    UserSelectMenu,
    RoleSelectMenu,
    MentionableSelectMenu,
    ChannelSelectMenu,
)


def _walk_internal(component: Component, seen: Set[Component]) -> Iterator[Component]:
    if component in seen:
        # prevent infinite recursion if anyone manages to nest a component in itself
        return
    seen.add(component)

    yield component

    if isinstance(component, ActionRow):
        for item in component.children:
            yield from _walk_internal(item, seen)
    elif isinstance(component, Section):
        yield from _walk_internal(component.accessory, seen)
        for item in component.components:
            yield from _walk_internal(item, seen)
    elif isinstance(component, Container):
        for item in component.components:
            yield from _walk_internal(item, seen)


# yields *all* components recursively
def _walk_all_components(components: Sequence[Component]) -> Iterator[Component]:
    seen = set()
    for item in components:
        yield from _walk_internal(item, seen)


C = TypeVar("C", bound="Component")


COMPONENT_LOOKUP: Mapping[ComponentTypeLiteral, Type[Component]] = {
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
}


# NOTE: The type param is purely for type-checking, it has no implications on runtime behavior.
def _component_factory(data: ComponentPayload, *, type: Type[C] = Component) -> C:
    component_type = data["type"]

    if component_cls := COMPONENT_LOOKUP.get(component_type):
        return component_cls(data)  # type: ignore
    else:
        as_enum = try_enum(ComponentType, component_type)
        return Component._raw_construct(type=as_enum)  # type: ignore


# this is just a rebranded _component_factory,
# as a workaround to Python not supporting typescript-like mapped types
# XXX: an alternative would be declaring 14 _component_factory overloads, which also isn't too great.
def _message_component_factory(data: MessageTopLevelComponentPayload) -> MessageTopLevelComponent:
    return _component_factory(data)  # type: ignore
