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
from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Dict, List, Mapping, Optional, Tuple, Union

from .enums import (
    ApplicationCommandPermissionType,
    ApplicationCommandType,
    ChannelType,
    OptionType,
    enum_if_int,
    try_enum,
    try_enum_to_int,
)
from .errors import InvalidArgument
from .permissions import Permissions
from .utils import MISSING, _get_as_snowflake, _maybe_cast, warn_deprecated

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.interactions import (
        ApplicationCommand as ApplicationCommandPayload,
        ApplicationCommandOption as ApplicationCommandOptionPayload,
        ApplicationCommandOptionChoice as ApplicationCommandOptionChoicePayload,
        ApplicationCommandOptionChoiceValue,
        ApplicationCommandPermissions as ApplicationCommandPermissionsPayload,
        EditApplicationCommand as EditApplicationCommandPayload,
        GuildApplicationCommandPermissions as GuildApplicationCommandPermissionsPayload,
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

    if name != name.lower() or not re.fullmatch(r"[\w-]{1,32}", name):
        raise InvalidArgument(
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
    """

    def __init__(self, name: str, value: ApplicationCommandOptionChoiceValue):
        self.name: str = name
        self.value: ApplicationCommandOptionChoiceValue = value

    def __repr__(self) -> str:
        return f"<OptionChoice name={self.name!r} value={self.value!r}>"

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.value == other.value

    def to_dict(self) -> ApplicationCommandOptionChoicePayload:
        return {"name": self.name, "value": self.value}

    @classmethod
    def from_dict(cls, data: ApplicationCommandOptionChoicePayload):
        return OptionChoice(name=data["name"], value=data["value"])


class Option:
    """Represents a slash command option.

    Parameters
    ----------
    name: :class:`str`
        The option's name.
    description: :class:`str`
        The option's description.
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
    ):
        _validate_name(name)
        self.name: str = name
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
        )

    def add_choice(self, name: str, value: Union[str, int]) -> None:
        """Adds an OptionChoice to the list of current choices,
        parameters are the same as for :class:`OptionChoice`.
        """
        self.choices.append(OptionChoice(name=name, value=value))

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
        return payload


class ApplicationCommand(ABC):
    """
    The base class for application commands

    Attributes
    ----------
    type: :class:`ApplicationCommandType`
        The command type
    name: :class:`str`
        The command name
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
    """

    __repr_info__: ClassVar[Tuple[str, ...]] = ("type", "name")

    def __init__(
        self,
        type: ApplicationCommandType,
        name: str,
        default_permission: bool = MISSING,
        dm_permission: bool = MISSING,
        default_member_permissions: Optional[Permissions] = MISSING,
    ):
        self.type: ApplicationCommandType = enum_if_int(ApplicationCommandType, type)
        self.name: str = name

        if default_permission is not MISSING:
            warn_deprecated(
                "default_permission is deprecated. "
                "Please use dm_permission and default_member_permissions instead",
                DeprecationWarning,
                stacklevel=2,
            )
            if default_permission:
                self.dm_permission = True
                default_member_permissions = None
            else:
                self.dm_permission = False
                default_member_permissions = Permissions(0)

        if dm_permission is not MISSING:
            self.dm_permission: bool = dm_permission

        self._default_member_permissions: Optional[int]
        if default_member_permissions is None:
            # allow everyone to use the command if its not supplied
            self._default_member_permissions = None
        else:
            self._default_member_permissions = default_member_permissions.value

        self._always_synced: bool = False

    @property
    def default_member_permissions(self) -> Optional[Permissions]:
        """Optional[:class:`Permissions`]: The default member permissions for this command.

        If no permissions are returned, this means everyone can use the command by default.

        If an empty :class:`Permissions` object is returned, this means no one can use the command.

        .. versionadded:: 2.5
        """
        if self._default_member_permissions is None:
            return None
        else:
            return Permissions(self._default_member_permissions)

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_info__)
        return f"<{type(self).__name__} {attrs}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return (
            self.type == other.type
            and self.name == other.name
            and self.dm_permission == other.dm_permission
            and self._default_member_permissions == other._default_member_permissions
        )

    def to_dict(self) -> EditApplicationCommandPayload:
        data: EditApplicationCommandPayload = {
            "type": try_enum_to_int(self.type),
            "name": self.name,
        }

        if not self.dm_permission:
            data["dm_permission"] = False

        if self._default_member_permissions is None:
            data["default_member_permissions"] = None
        else:
            data["default_member_permissions"] = str(self._default_member_permissions)

        return data


class _APIApplicationCommandMixin:
    __repr_info__ = ("id",)

    def _update_common(self, data: ApplicationCommandPayload) -> None:
        self.id: int = int(data["id"])
        self.application_id: int = int(data["application_id"])
        self.guild_id: Optional[int] = _get_as_snowflake(data, "guild_id")
        self.version: int = int(data["version"])
        self.dm_permission: bool = data.get("dm_permission", True)
        default_member_permissions = data.get("default_member_permissions")
        if default_member_permissions is not None:
            self._default_member_permissions: Optional[int] = int(default_member_permissions)
        else:
            self._default_member_permissions: Optional[int] = None


class UserCommand(ApplicationCommand):
    """
    A user context menu command

    Attributes
    ----------
    name: :class:`str`
        The user command's name.
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
    """

    __repr_info__ = ("name", "dm_permission", "default_member_permissions")

    def __init__(
        self,
        name: str,
        default_permission: bool = MISSING,
        dm_permission: bool = True,
        default_member_permissions: Optional[Permissions] = None,
    ):
        super().__init__(
            type=ApplicationCommandType.user,
            name=name,
            default_permission=default_permission,
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
        )


class APIUserCommand(UserCommand, _APIApplicationCommandMixin):
    """
    A user context menu command returned by the API

    .. versionadded:: 2.4

    Attributes
    ----------
    name: :class:`str`
        The user command's name.
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
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

        self = cls(name=data["name"])
        self._update_common(data)
        return self


class MessageCommand(ApplicationCommand):
    """
    A message context menu command

    Attributes
    ----------
    name: :class:`str`
        The message command's name.
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
    """

    __repr_info__ = ("name", "dm_permission", "default_member_permissions")

    def __init__(
        self,
        name: str,
        default_permission: bool = MISSING,
        dm_permission: bool = True,
        default_member_permissions: Optional[Permissions] = None,
    ):
        super().__init__(
            type=ApplicationCommandType.message,
            name=name,
            default_permission=default_permission,
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
        )


class APIMessageCommand(MessageCommand, _APIApplicationCommandMixin):
    """
    A message context menu command returned by the API

    .. versionadded:: 2.4

    Attributes
    ----------
    name: :class:`str`
        The message command's name.
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
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

        self = cls(name=data["name"])
        self._update_common(data)
        return self


class SlashCommand(ApplicationCommand):
    """
    The base class for building slash commands.

    Parameters
    ----------
    name: :class:`str`
        The slash command's name.
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
    description: :class:`str`
        The slash command's description.
    options: List[:class:`Option`]
        The list of options the slash command has.
    """

    __repr_info__ = (
        "name",
        "description",
        "options",
        "dm_permission",
        "default_member_permissions",
    )

    def __init__(
        self,
        name: str,
        description: str,
        options: List[Option] = None,
        default_permission: bool = MISSING,
        dm_permission: bool = True,
        default_member_permissions: Optional[Permissions] = None,
    ):
        _validate_name(name)

        super().__init__(
            type=ApplicationCommandType.chat_input,
            name=name,
            default_permission=default_permission,
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
        )
        self.description: str = description
        self.options: List[Option] = options or []

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.description == other.description
            and self.options == other.options
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
            )
        )

    def to_dict(self) -> EditApplicationCommandPayload:
        res = super().to_dict()
        res["description"] = self.description
        res["options"] = [o.to_dict() for o in self.options]
        return res


class APISlashCommand(SlashCommand, _APIApplicationCommandMixin):
    """
    A slash command returned by the API

    .. versionadded:: 2.4

    Attributes
    ----------
    name: :class:`str`
        The slash command's name.
    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
    id: :class:`int`
        The slash command's ID.
    description: :class:`str`
        The slash command's description.
    options: List[:class:`Option`]
        The list of options the slash command has.
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
            options=_maybe_cast(
                data.get("options", MISSING), lambda x: list(map(Option.from_dict, x))
            ),
        )
        self._update_common(data)
        return self


class ApplicationCommandPermissions:
    """Represents application command permissions for a role, user, or channel.

    Attributes
    ----------
    id: :class:`int`
        The ID of the role, user, or channel.
    type: ApplicationCommandPermissionType
        The type of the target.
        1 if target is a role; 2 if target is a user; 3 if target is a channel.
    permission: :class:`bool`
        Whether to allow or deny the access to the application command.
    """

    __slots__ = ("id", "type", "permission", "_guild_id")

    def __init__(self, *, data: ApplicationCommandPermissionsPayload, guild_id: int):
        self.id: int = int(data["id"])
        self.type: ApplicationCommandPermissionType = try_enum(
            ApplicationCommandPermissionType, data["type"]
        )
        self.permission: bool = data["permission"]
        self._guild_id: Optional[int] = guild_id

    def __repr__(self):
        return f"<ApplicationCommandPermissions id={self.id!r} type={self.type!r} permission={self.permission!r}>"

    def __eq__(self, other):
        return (
            self.id == other.id and self.type == other.type and self.permission == other.permission
        )

    def to_dict(self) -> ApplicationCommandPermissionsPayload:
        return {"id": self.id, "type": int(self.type), "permission": self.permission}  # type: ignore

    def is_everyone(self) -> bool:
        """Whether this permission object is affecting the @everyone role.

        .. versionadded:: 2.5

        :return type: :class:`bool`
        """
        return self.id == self._guild_id

    def is_all_channels(self) -> bool:
        """Whether this permission object is affecting all channels.

        .. versionadded:: 2.5

        :return type: :class:`bool`
        """
        return self.id - 1 == self._guild_id


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

    def __init__(self, *, data: GuildApplicationCommandPermissionsPayload, state: ConnectionState):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.application_id: int = int(data["application_id"])
        self.guild_id: int = int(data["guild_id"])

        self.permissions: List[ApplicationCommandPermissions] = [
            ApplicationCommandPermissions(data=elem, guild_id=self.guild_id)
            for elem in data["permissions"]
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
