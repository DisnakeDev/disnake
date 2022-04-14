# The MIT License (MIT)

# Copyright (c) 2021-present EQUENOS

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import math
import re
import warnings
from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from .abc import User
from .custom_warnings import ConfigWarning
from .enums import (
    ApplicationCommandType,
    ChannelType,
    Locale,
    OptionType,
    enum_if_int,
    try_enum,
    try_enum_to_int,
)
from .errors import InvalidArgument
from .i18n import LocalizationValue
from .role import Role
from .utils import MISSING, _get_as_snowflake, _maybe_cast

if TYPE_CHECKING:
    from .i18n import LocalizationProtocol, Localizations
    from .state import ConnectionState
    from .types.interactions import (
        ApplicationCommand as ApplicationCommandPayload,
        ApplicationCommandOption as ApplicationCommandOptionPayload,
        ApplicationCommandOptionChoice as ApplicationCommandOptionChoicePayload,
        ApplicationCommandOptionChoiceValue,
        ApplicationCommandPermissions as ApplicationCommandPermissionsPayload,
        ApplicationCommandPermissionType,
        EditApplicationCommand as EditApplicationCommandPayload,
        GuildApplicationCommandPermissions as GuildApplicationCommandPermissionsPayload,
        PartialGuildApplicationCommandPermissions as PartialGuildApplicationCommandPermissionsPayload,
    )

    Choices = Union[
        List["OptionChoice"],
        List[ApplicationCommandOptionChoiceValue],
        Dict[str, ApplicationCommandOptionChoiceValue],
    ]

    APIApplicationCommand = Union["APIUserCommand", "APIMessageCommand", "APISlashCommand"]


__all__ = (
    "application_command_factory",
    "ApplicationCommand",
    "SlashCommand",
    "APISlashCommand",
    "UserCommand",
    "APIUserCommand",
    "MessageCommand",
    "APIMessageCommand",
    "OptionChoice",
    "Option",
    "ApplicationCommandPermissions",
    "GuildApplicationCommandPermissions",
    "PartialGuildApplicationCommandPermissions",
    "PartialGuildAppCmdPerms",
    "UnresolvedGuildApplicationCommandPermissions",
)


def application_command_factory(data: ApplicationCommandPayload) -> APIApplicationCommand:
    cmd_type = try_enum(ApplicationCommandType, data.get("type", 1))
    if cmd_type is ApplicationCommandType.chat_input:
        return APISlashCommand.from_dict(data)
    if cmd_type is ApplicationCommandType.user:
        return APIUserCommand.from_dict(data)
    if cmd_type is ApplicationCommandType.message:
        return APIMessageCommand.from_dict(data)

    raise TypeError(f"Application command of type {cmd_type} is not valid")


def _validate_name(name: str) -> None:
    # used for slash command names and option names
    # see https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming

    assert name == name.lower() and re.fullmatch(r"[\w-]{1,32}", name), (
        f"Slash command or option name '{name}' should be lowercase, "
        "between 1 and 32 characters long, and only consist of "
        "these symbols: a-z, 0-9, -, _, and other languages'/scripts' symbols"
    )


class OptionChoice:
    """Represents an option choice.

    Parameters
    ----------
    name: :class:`str`
        The name of the option choice (visible to users).
    value: Union[:class:`str`, :class:`int`]
        The value of the option choice.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    """

    def __init__(
        self,
        name: str,
        value: ApplicationCommandOptionChoiceValue,
        *,
        name_localizations: Localizations = None,
    ):
        self.name: str = name
        self.value: ApplicationCommandOptionChoiceValue = value
        self.name_localizations: LocalizationValue = LocalizationValue(name_localizations)

    def __repr__(self) -> str:
        return f"<OptionChoice name={self.name!r} value={self.value!r}>"

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name
            and self.value == other.value
            and self.name_localizations == other.name_localizations
        )

    def to_dict(self, *, locale: Optional[Locale] = None) -> ApplicationCommandOptionChoicePayload:
        localizations = self.name_localizations.to_dict()

        name: Optional[str] = None
        # if `locale` provided, get localized name from dict
        if locale is not None and localizations:
            name = localizations.get(str(locale))

        # fall back to default name if no locale or no localized name
        if name is None:
            name = self.name

        payload: ApplicationCommandOptionChoicePayload = {
            "name": name,
            "value": self.value,
        }
        # if no `locale` provided, include all localizations in payload
        if locale is None and localizations:
            payload["name_localizations"] = localizations
        return payload

    @classmethod
    def from_dict(cls, data: ApplicationCommandOptionChoicePayload):
        return OptionChoice(
            name=data["name"],
            value=data["value"],
            name_localizations=data.get("name_localizations"),
        )

    def localize(self, store: LocalizationProtocol) -> None:
        self.name_localizations._link(store)


class Option:
    """Represents a slash command option.

    Parameters
    ----------
    name: :class:`str`
        The option's name.
    description: :class:`str`
        The option's description.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    description_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``description``.

        .. versionadded:: 2.5
    type: :class:`OptionType`
        The option type, e.g. :class:`OptionType.user`.
    required: :class:`bool`
        Whether this option is required.
    choices: Union[List[:class:`OptionChoice`], List[Union[:class:`str`, :class:`int`]], Dict[:class:`str`, Union[:class:`str`, :class:`int`]]]
        The list of option choices.
    options: List[:class:`Option`]
        The list of sub options. Normally you don't have to specify it directly,
        instead consider using ``@main_cmd.sub_command`` or ``@main_cmd.sub_command_group`` decorators.
    channel_types: List[:class:`ChannelType`]
        The list of channel types that your option supports, if the type is :class:`OptionType.channel`.
        By default, it supports all channel types.
    autocomplete: :class:`bool`
        Whether this option can be autocompleted.
    min_value: Union[:class:`int`, :class:`float`]
        The minimum value permitted.
    max_value: Union[:class:`int`, :class:`float`]
        The maximum value permitted.
    """

    __slots__ = (
        "name",
        "description",
        "type",
        "required",
        "choices",
        "options",
        "channel_types",
        "autocomplete",
        "min_value",
        "max_value",
        "name_localizations",
        "description_localizations",
    )

    def __init__(
        self,
        name: str,
        description: str = None,
        type: Union[OptionType, int] = None,
        required: bool = False,
        choices: Choices = None,
        options: list = None,
        channel_types: List[ChannelType] = None,
        autocomplete: bool = False,
        min_value: float = None,
        max_value: float = None,
        name_localizations: Localizations = None,
        description_localizations: Localizations = None,
    ):
        self.name: str = name.lower()
        _validate_name(self.name)
        self.description: str = description or "-"
        self.type: OptionType = enum_if_int(OptionType, type) or OptionType.string
        self.required: bool = required
        self.options: List[Option] = options or []

        if min_value and self.type is OptionType.integer:
            min_value = math.ceil(min_value)
        if max_value and self.type is OptionType.integer:
            max_value = math.floor(max_value)

        self.min_value: Optional[float] = min_value
        self.max_value: Optional[float] = max_value

        if channel_types is not None and not all(isinstance(t, ChannelType) for t in channel_types):
            raise InvalidArgument("channel_types must be a list of `ChannelType`s")

        self.channel_types: List[ChannelType] = channel_types or []

        self.choices: List[OptionChoice] = []
        if choices is not None:
            if autocomplete:
                raise InvalidArgument("can not specify both choices and autocomplete args")

            if isinstance(choices, Mapping):
                self.choices = [OptionChoice(name, value) for name, value in choices.items()]
            else:
                for c in choices:
                    if not isinstance(c, OptionChoice):
                        c = OptionChoice(str(c), c)
                    self.choices.append(c)

        self.autocomplete: bool = autocomplete

        self.name_localizations: LocalizationValue = LocalizationValue(name_localizations)
        self.description_localizations: LocalizationValue = LocalizationValue(
            description_localizations
        )

    def __repr__(self) -> str:
        return (
            f"<Option name={self.name!r} description={self.description!r}"
            f" type={self.type!r} required={self.required!r} choices={self.choices!r}"
            f" options={self.options!r} min_value={self.min_value!r} max_value={self.max_value!r}>"
        )

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name
            and self.description == other.description
            and self.type == other.type
            and self.required == other.required
            and self.choices == other.choices
            and self.options == other.options
            and set(self.channel_types) == set(other.channel_types)
            and self.autocomplete == other.autocomplete
            and self.min_value == other.min_value
            and self.max_value == other.max_value
            and self.name_localizations == other.name_localizations
            and self.description_localizations == other.description_localizations
        )

    @classmethod
    def from_dict(cls, data: ApplicationCommandOptionPayload) -> Option:
        return Option(
            name=data["name"],
            description=data.get("description"),
            type=data.get("type"),
            required=data.get("required", False),
            choices=_maybe_cast(
                data.get("choices", MISSING), lambda x: list(map(OptionChoice.from_dict, x))
            ),
            options=_maybe_cast(
                data.get("options", MISSING), lambda x: list(map(Option.from_dict, x))
            ),
            channel_types=_maybe_cast(
                data.get("channel_types", MISSING), lambda x: [try_enum(ChannelType, t) for t in x]
            ),
            autocomplete=data.get("autocomplete", False),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            name_localizations=data.get("name_localizations"),
            description_localizations=data.get("description_localizations"),
        )

    def add_choice(
        self,
        name: str,
        value: Union[str, int],
        name_localizations: Localizations = None,
    ) -> None:
        """Adds an OptionChoice to the list of current choices,
        parameters are the same as for :class:`OptionChoice`.
        """
        self.choices.append(
            OptionChoice(
                name=name,
                value=value,
                name_localizations=name_localizations,
            )
        )

    def add_option(
        self,
        name: str,
        description: str = None,
        type: OptionType = None,
        required: bool = False,
        choices: List[OptionChoice] = None,
        options: list = None,
        channel_types: List[ChannelType] = None,
        autocomplete: bool = False,
        min_value: float = None,
        max_value: float = None,
        name_localizations: Localizations = None,
        description_localizations: Localizations = None,
    ) -> None:
        """Adds an option to the current list of options,
        parameters are the same as for :class:`Option`."""
        type = type or OptionType.string
        self.options.append(
            Option(
                name=name,
                description=description,
                type=type,
                required=required,
                choices=choices,
                options=options,
                channel_types=channel_types,
                autocomplete=autocomplete,
                min_value=min_value,
                max_value=max_value,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
        )

    def to_dict(self) -> ApplicationCommandOptionPayload:
        payload: ApplicationCommandOptionPayload = {
            "name": self.name,
            "description": self.description,
            "type": try_enum_to_int(self.type),
        }
        if self.required:
            payload["required"] = True
        if self.autocomplete:
            payload["autocomplete"] = True
        if self.choices:
            payload["choices"] = [c.to_dict() for c in self.choices]
        if self.options:
            payload["options"] = [o.to_dict() for o in self.options]
        if self.channel_types:
            payload["channel_types"] = [v.value for v in self.channel_types]
        if self.min_value is not None:
            payload["min_value"] = self.min_value
        if self.max_value is not None:
            payload["max_value"] = self.max_value
        if (loc := self.name_localizations.to_dict()) is not None:
            payload["name_localizations"] = loc
        if (loc := self.description_localizations.to_dict()) is not None:
            payload["description_localizations"] = loc
        return payload

    def localize(self, store: LocalizationProtocol) -> None:
        self.name_localizations._link(store)
        self.description_localizations._link(store)

        if (name_loc := self.name_localizations.to_dict()) is not None:
            for value in name_loc.values():
                _validate_name(value)

        for c in self.choices:
            c.localize(store)
        for o in self.options:
            o.localize(store)


class ApplicationCommand(ABC):
    """
    The base class for application commands

    Attributes
    ----------
    type: :class:`ApplicationCommandType`
        The command type
    name: :class:`str`
        The command name
    default_permission: :class:`bool`
        Whether the command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    """

    __repr_info__: ClassVar[Tuple[str, ...]] = ("type", "name")

    def __init__(
        self,
        type: ApplicationCommandType,
        name: str,
        default_permission: bool = True,
        name_localizations: Localizations = None,
    ):
        self.type: ApplicationCommandType = enum_if_int(ApplicationCommandType, type)
        self.name: str = name
        self.default_permission: bool = default_permission
        self.name_localizations: LocalizationValue = LocalizationValue(name_localizations)

        self._always_synced: bool = False

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_info__)
        return f"<{type(self).__name__} {attrs}>"

    def __eq__(self, other) -> bool:
        return (
            self.type == other.type
            and self.name == other.name
            and self.default_permission == other.default_permission
            and self.name_localizations == other.name_localizations
        )

    def to_dict(self) -> EditApplicationCommandPayload:
        data: EditApplicationCommandPayload = {
            "type": try_enum_to_int(self.type),
            "name": self.name,
        }
        if not self.default_permission:
            data["default_permission"] = False
        if (loc := self.name_localizations.to_dict()) is not None:
            data["name_localizations"] = loc
        return data

    def localize(self, store: LocalizationProtocol) -> None:
        self.name_localizations._link(store)


class _APIApplicationCommandMixin:
    __repr_info__ = ("id",)

    def _update_common(self, data: ApplicationCommandPayload) -> None:
        self.id: int = int(data["id"])
        self.application_id: int = int(data["application_id"])
        self.guild_id: Optional[int] = _get_as_snowflake(data, "guild_id")
        self.version: int = int(data["version"])


class UserCommand(ApplicationCommand):
    """
    A user context menu command

    Attributes
    ----------
    name: :class:`str`
        The user command's name.
    default_permission: :class:`bool`
        Whether the user command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    """

    __repr_info__ = ("name", "default_permission")

    def __init__(
        self,
        name: str,
        default_permission: bool = True,
        name_localizations: Localizations = None,
    ):
        super().__init__(
            type=ApplicationCommandType.user,
            name=name,
            default_permission=default_permission,
            name_localizations=name_localizations,
        )


class APIUserCommand(UserCommand, _APIApplicationCommandMixin):
    """
    A user context menu command returned by the API

    .. versionadded:: 2.4

    Attributes
    ----------
    name: :class:`str`
        The user command's name.
    default_permission: :class:`bool`
        Whether the user command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    id: :class:`int`
        The user command's ID.
    application_id: :class:`int`
        The application ID this command belongs to.
    guild_id: Optional[:class:`int`]
        The ID of the guild this user command is enabled in, or ``None`` if it's global.
    version: :class:`int`
        Autoincrementing version identifier updated during substantial record changes.
    """

    __repr_info__ = UserCommand.__repr_info__ + _APIApplicationCommandMixin.__repr_info__

    @classmethod
    def from_dict(cls, data: ApplicationCommandPayload) -> APIUserCommand:
        cmd_type = data.get("type", 0)
        if cmd_type != ApplicationCommandType.user.value:
            raise ValueError(f"Invalid payload type for UserCommand: {cmd_type}")

        self = cls(
            name=data["name"],
            default_permission=data.get("default_permission", True),
            name_localizations=data.get("name_localizations"),
        )
        self._update_common(data)
        return self


class MessageCommand(ApplicationCommand):
    """
    A message context menu command

    Attributes
    ----------
    name: :class:`str`
        The message command's name.
    default_permission: :class:`bool`
        Whether the message command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    """

    __repr_info__ = ("name", "default_permission")

    def __init__(
        self,
        name: str,
        default_permission: bool = True,
        name_localizations: Localizations = None,
    ):
        super().__init__(
            type=ApplicationCommandType.message,
            name=name,
            default_permission=default_permission,
            name_localizations=name_localizations,
        )


class APIMessageCommand(MessageCommand, _APIApplicationCommandMixin):
    """
    A message context menu command returned by the API

    .. versionadded:: 2.4

    Attributes
    ----------
    name: :class:`str`
        The message command's name.
    default_permission: :class:`bool`
        Whether the message command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    id: :class:`int`
        The message command's ID.
    application_id: :class:`int`
        The application ID this command belongs to.
    guild_id: Optional[:class:`int`]
        The ID of the guild this message command is enabled in, or ``None`` if it's global.
    version: :class:`int`
        Autoincrementing version identifier updated during substantial record changes.
    """

    __repr_info__ = MessageCommand.__repr_info__ + _APIApplicationCommandMixin.__repr_info__

    @classmethod
    def from_dict(cls, data: ApplicationCommandPayload) -> APIMessageCommand:
        cmd_type = data.get("type", 0)
        if cmd_type != ApplicationCommandType.message.value:
            raise ValueError(f"Invalid payload type for MessageCommand: {cmd_type}")

        self = cls(
            name=data["name"],
            default_permission=data.get("default_permission", True),
            name_localizations=data.get("name_localizations"),
        )
        self._update_common(data)
        return self


class SlashCommand(ApplicationCommand):
    """
    The base class for building slash commands.

    Parameters
    ----------
    name: :class:`str`
        The slash command's name.
    default_permission: :class:`bool`
        Whether the slash command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    description: :class:`str`
        The slash command's description.
    options: List[:class:`Option`]
        The list of options the slash command has.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    description_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``description``.

        .. versionadded:: 2.5
    """

    __repr_info__ = ("name", "description", "options", "default_permission")

    def __init__(
        self,
        name: str,
        description: str,
        options: List[Option] = None,
        default_permission: bool = True,
        name_localizations: Localizations = None,
        description_localizations: Localizations = None,
    ):
        name = name.lower()
        _validate_name(name)

        super().__init__(
            type=ApplicationCommandType.chat_input,
            name=name,
            default_permission=default_permission,
            name_localizations=name_localizations,
        )
        self.description: str = description
        self.options: List[Option] = options or []
        self.description_localizations: LocalizationValue = LocalizationValue(
            description_localizations
        )

    def __str__(self) -> str:
        return f"<SlashCommand name={self.name!r}>"

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.description == other.description
            and self.options == other.options
            and self.description_localizations == other.description_localizations
        )

    def add_option(
        self,
        name: str,
        description: str = None,
        type: OptionType = None,
        required: bool = False,
        choices: List[OptionChoice] = None,
        options: list = None,
        channel_types: List[ChannelType] = None,
        autocomplete: bool = False,
        min_value: float = None,
        max_value: float = None,
        name_localizations: Localizations = None,
        description_localizations: Localizations = None,
    ) -> None:
        """Adds an option to the current list of options,
        parameters are the same as for :class:`Option`
        """
        self.options.append(
            Option(
                name=name,
                description=description,
                type=type or OptionType.string,
                required=required,
                choices=choices,
                options=options,
                channel_types=channel_types,
                autocomplete=autocomplete,
                min_value=min_value,
                max_value=max_value,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
        )

    def to_dict(self) -> EditApplicationCommandPayload:
        res = super().to_dict()
        res["description"] = self.description
        res["options"] = [o.to_dict() for o in self.options]
        if (loc := self.description_localizations.to_dict()) is not None:
            res["description_localizations"] = loc
        return res

    def localize(self, store: LocalizationProtocol) -> None:
        super().localize(store)
        if (name_loc := self.name_localizations.to_dict()) is not None:
            for value in name_loc.values():
                _validate_name(value)

        self.description_localizations._link(store)

        for o in self.options:
            o.localize(store)


class APISlashCommand(SlashCommand, _APIApplicationCommandMixin):
    """
    A slash command returned by the API

    .. versionadded:: 2.4

    Attributes
    ----------
    name: :class:`str`
        The slash command's name.
    default_permission: :class:`bool`
        Whether the slash command is enabled by default. If set to ``False``, this command
        cannot be used in guilds (unless explicit command permissions are set), or in DMs.
    id: :class:`int`
        The slash command's ID.
    description: :class:`str`
        The slash command's description.
    options: List[:class:`Option`]
        The list of options the slash command has.
    name_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``name``.

        .. versionadded:: 2.5
    description_localizations: Union[:class:`str`, Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        Localizations for ``description``.

        .. versionadded:: 2.5
    application_id: :class:`int`
        The application ID this command belongs to.
    guild_id: Optional[:class:`int`]
        The ID of the guild this slash command is enabled in, or ``None`` if it's global.
    version: :class:`int`
        Autoincrementing version identifier updated during substantial record changes.
    """

    __repr_info__ = SlashCommand.__repr_info__ + _APIApplicationCommandMixin.__repr_info__

    @classmethod
    def from_dict(cls, data: ApplicationCommandPayload) -> APISlashCommand:
        cmd_type = data.get("type", 0)
        if cmd_type != ApplicationCommandType.chat_input.value:
            raise ValueError(f"Invalid payload type for SlashCommand: {cmd_type}")

        self = cls(
            name=data["name"],
            description=data["description"],
            default_permission=data.get("default_permission", True),
            options=_maybe_cast(
                data.get("options", MISSING), lambda x: list(map(Option.from_dict, x))
            ),
            name_localizations=data.get("name_localizations"),
            description_localizations=data.get("description_localizations"),
        )
        self._update_common(data)
        return self


class ApplicationCommandPermissions:
    """Represents application command permissions for a role or a user.

    Attributes
    ----------
    id: :class:`int`
        The ID of the role or user.
    type: :class:`int`
        The type of the target.
        1 if target is a role; 2 if target is a user.
    permission: :class:`bool`
        Whether to allow or deny the access to the application command.
    """

    __slots__ = ("id", "type", "permission")

    def __init__(self, *, data: ApplicationCommandPermissionsPayload):
        self.id: int = int(data["id"])
        self.type: ApplicationCommandPermissionType = data["type"]
        self.permission: bool = data["permission"]

    def __repr__(self):
        return f"<ApplicationCommandPermissions id={self.id!r} type={self.type!r} permission={self.permission!r}>"

    def __eq__(self, other):
        return (
            self.id == other.id and self.type == other.type and self.permission == other.permission
        )

    def to_dict(self) -> ApplicationCommandPermissionsPayload:
        return {"id": self.id, "type": self.type, "permission": self.permission}


class GuildApplicationCommandPermissions:
    """Represents application command permissions in a guild.

    Attributes
    ----------
    id: :class:`int`
        The application command's ID.
    application_id: :class:`int`
        The application ID this command belongs to.
    guild_id: :class:`int`
        The ID of the guild where these permissions are applied.
    permissions: List[:class:`ApplicationCommandPermissions`]
        A list of :class:`ApplicationCommandPermissions`.
    """

    __slots__ = ("_state", "id", "application_id", "guild_id", "permissions")

    def __init__(self, *, state: ConnectionState, data: GuildApplicationCommandPermissionsPayload):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.application_id: int = int(data["application_id"])
        self.guild_id: int = int(data["guild_id"])

        self.permissions: List[ApplicationCommandPermissions] = [
            ApplicationCommandPermissions(data=elem) for elem in data["permissions"]
        ]

    def __repr__(self):
        return (
            f"<GuildApplicationCommandPermissions id={self.id!r} application_id={self.application_id!r}"
            f" guild_id={self.guild_id!r} permissions={self.permissions!r}>"
        )

    def to_dict(self) -> GuildApplicationCommandPermissionsPayload:
        return {
            "id": self.id,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "permissions": [perm.to_dict() for perm in self.permissions],
        }

    async def edit(
        self,
        *,
        permissions: Dict[Union[Role, User], bool] = None,
        role_ids: Dict[int, bool] = None,
        user_ids: Dict[int, bool] = None,
    ) -> GuildApplicationCommandPermissions:
        """Replaces the current permissions with the specified ones.

        Parameters
        ----------
        permissions: Mapping[Union[:class:`Role`, :class:`disnake.abc.User`], :class:`bool`]
            Roles or users to booleans. ``True`` means "allow", ``False`` means "deny".
        role_ids: Mapping[:class:`int`, :class:`bool`]
            Role IDs to booleans.
        user_ids: Mapping[:class:`int`, :class:`bool`]
            User IDs to booleans.

        Returns
        -------
        :class:`GuildApplicationCommandPermissions`
            The newly updated permissions.
        """
        data: List[ApplicationCommandPermissionsPayload] = []

        if permissions is not None:
            for obj, value in permissions.items():
                if isinstance(obj, Role):
                    target_type = 1
                elif isinstance(obj, User):
                    target_type = 2
                else:
                    raise ValueError("Permission target should be an instance of Role or abc.User")
                data.append({"id": obj.id, "type": target_type, "permission": value})

        if role_ids is not None:
            for role_id, value in role_ids.items():
                data.append({"id": role_id, "type": 1, "permission": value})

        if user_ids is not None:
            for user_id, value in user_ids.items():
                data.append({"id": user_id, "type": 2, "permission": value})

        res = await self._state.http.edit_application_command_permissions(
            self.application_id, self.guild_id, self.id, {"permissions": data}
        )

        return GuildApplicationCommandPermissions(state=self._state, data=res)


class PartialGuildApplicationCommandPermissions:
    """Creates a partial object representing permissions of the application command.

    Parameters
    ----------
    command_id: :class:`int`
        The ID of the application command you want to apply these permissions to.
    permissions: Mapping[Union[:class:`Role`, :class:`disnake.abc.User`], :class:`bool`]
        Roles or users to booleans. ``True`` means "allow", ``False`` means "deny".
    role_ids: Mapping[:class:`int`, :class:`bool`]
        Role IDs to booleans.
    user_ids: Mapping[:class:`int`, :class:`bool`]
        User IDs to booleans.
    """

    def __init__(
        self,
        command_id: int,
        *,
        permissions: Mapping[Union[Role, User], bool] = None,
        role_ids: Mapping[int, bool] = None,
        user_ids: Mapping[int, bool] = None,
    ):
        self.id: int = command_id
        self.permissions: List[ApplicationCommandPermissions] = []

        if permissions is not None:
            for obj, value in permissions.items():
                if isinstance(obj, Role):
                    target_type = 1
                elif isinstance(obj, User):
                    target_type = 2
                else:
                    raise ValueError("Permission target should be an instance of Role or abc.User")
                data: ApplicationCommandPermissionsPayload = {
                    "id": obj.id,
                    "type": target_type,
                    "permission": value,
                }
                self.permissions.append(ApplicationCommandPermissions(data=data))

        if role_ids is not None:
            for role_id, value in role_ids.items():
                data: ApplicationCommandPermissionsPayload = {
                    "id": role_id,
                    "type": 1,
                    "permission": value,
                }
                self.permissions.append(ApplicationCommandPermissions(data=data))

        if user_ids is not None:
            for user_id, value in user_ids.items():
                data: ApplicationCommandPermissionsPayload = {
                    "id": user_id,
                    "type": 2,
                    "permission": value,
                }
                self.permissions.append(ApplicationCommandPermissions(data=data))

    def to_dict(self) -> PartialGuildApplicationCommandPermissionsPayload:
        return {
            "id": self.id,
            "permissions": [perm.to_dict() for perm in self.permissions],
        }


PartialGuildAppCmdPerms = PartialGuildApplicationCommandPermissions


class UnresolvedGuildApplicationCommandPermissions:
    """Creates an object representing permissions of an application command,
    without a specific command ID.

    Parameters
    ----------
    permissions: Mapping[Union[:class:`Role`, :class:`disnake.abc.User`], :class:`bool`]
        Roles or users to booleans. ``True`` means "allow", ``False`` means "deny".
    role_ids: Mapping[:class:`int`, :class:`bool`]
        Role IDs to booleans.
    user_ids: Mapping[:class:`int`, :class:`bool`]
        User IDs to booleans.
    owner: :class:`bool`
        Whether to allow or deny the bot owner(s).
    """

    def __init__(
        self,
        *,
        permissions: Mapping[Union[Role, User], bool] = None,
        role_ids: Mapping[int, bool] = None,
        user_ids: Mapping[int, bool] = None,
        owner: bool = None,
    ):
        self.permissions: Optional[Mapping[Union[Role, User], bool]] = permissions
        self.role_ids: Optional[Mapping[int, bool]] = role_ids
        self.user_ids: Optional[Mapping[int, bool]] = user_ids
        self.owner: Optional[bool] = owner

    def resolve(
        self, *, command_id: int, owners: Iterable[int]
    ) -> PartialGuildApplicationCommandPermissions:
        """
        Creates a new :class:`PartialGuildApplicationCommandPermissions` object,
        combining the previously supplied permission values with the provided
        command ID and owner IDs.

        Parameters
        ----------
        command_id: :class:`int`
            The command ID to use.
        owners: Iterable[:class:`int`]
            The owner IDs, used for extending the user ID mapping
            based on the previously set ``owner`` permission if applicable

        Returns
        -------
        :class:`PartialGuildApplicationCommandPermissions`
            A new permissions object based on this instance
            and the provided command ID and owner IDs.
        """
        resolved_users: Optional[Mapping[int, bool]]
        if self.owner is not None:
            owner_ids = dict.fromkeys(owners, self.owner)
            if not owner_ids:
                raise ValueError("Cannot properly resolve permissions without owner IDs")

            users = self.user_ids or {}
            common_ids = owner_ids.keys() & users.keys()
            if any(users[id] != owner_ids[id] for id in common_ids):
                warnings.warn(
                    "Conflicting permissions for owner(s) provided in users", ConfigWarning
                )

            resolved_users = {**users, **owner_ids}
        else:
            resolved_users = self.user_ids

        return PartialGuildApplicationCommandPermissions(
            command_id=command_id,
            permissions=self.permissions,
            role_ids=self.role_ids,
            user_ids=resolved_users,
        )
