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
from abc import ABC

import re
import math
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Union, cast

from .member import Member
from .enums import (
    ApplicationCommandType,
    ChannelType,
    OptionType,
    try_enum,
    enum_if_int,
    try_enum_to_int,
)
from .errors import InvalidArgument
from .role import Role
from .utils import _get_as_snowflake

if TYPE_CHECKING:
    from .state import ConnectionState

__all__ = (
    "application_command_factory",
    "ApplicationCommand",
    "SlashCommand",
    "UserCommand",
    "MessageCommand",
    "OptionChoice",
    "Option",
    "ApplicationCommandPermissions",
    "GuildApplicationCommandPermissions",
    "PartialGuildApplicationCommandPermissions",
    "PartialGuildAppCmdPerms",
    "UnresolvedGuildApplicationCommandPermissions",
)


def application_command_factory(data: Mapping[str, Any]) -> Any:
    data = dict(data)
    cmd_type = try_enum(ApplicationCommandType, data.get("type", 1))
    if cmd_type is ApplicationCommandType.chat_input:
        return SlashCommand.from_dict(data)
    if cmd_type is ApplicationCommandType.user:
        return UserCommand.from_dict(data)
    if cmd_type is ApplicationCommandType.message:
        return MessageCommand.from_dict(data)

    raise TypeError(f"Application command of type {cmd_type} is not valid")


ChoiceValue = Union[str, int, float]


class OptionChoice:
    """
    Represents an option choice.

    Parameters
    ----------
    name: :class:`str`
        the name of the option choice (visible to users)
    value: Union[:class:`str`, :class:`int`]
        the value of the option choice
    """

    def __init__(self, name: str, value: ChoiceValue):
        self.name: str = name
        self.value: ChoiceValue = value

    def __repr__(self) -> str:
        return f"<OptionChoice name={self.name!r} value={self.value!r}>"

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.value == other.value

    def to_dict(self) -> Dict[str, ChoiceValue]:
        return {"name": self.name, "value": self.value}


Choices = Union[List[OptionChoice], List[ChoiceValue], Dict[str, ChoiceValue]]


class Option:
    """
    Represents a slash command option.

    Parameters
    ----------
    name: :class:`str`
        option's name
    description: :class:`str`
        option's description
    type: :class:`OptionType`
        the option type, e.g. :class:`OptionType.user`
    required: :class:`bool`
        whether this option is required or not
    choices: Union[List[:class:`OptionChoice`], Dict[:class:`str`, Union[:class:`str`, :class:`int`]]]
        the list of option choices
    options: List[:class:`Option`]
        the list of sub options. Normally you don't have to specify it directly,
        instead consider using ``@main_cmd.sub_command`` or ``@main_cmd.sub_command_group`` decorators.
    channel_types: List[:class:`ChannelType`]
        the list of channel types that your option supports, if the type is :class:`OptionType.channel`.
        By default, it supports all channel types.
    autocomplete: :class:`bool`
        whether this option can be autocompleted.
    min_value: Union[:class:`int`, :class:`float`]
        the minimum value permitted
    max_value: Union[:class:`int`, :class:`float`]
        the maximum value permitted
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
        type: OptionType = None,
        required: bool = False,
        choices: Choices = None,
        options: list = None,
        channel_types: List[ChannelType] = None,
        autocomplete: bool = False,
        min_value: float = None,
        max_value: float = None,
    ):
        assert name.islower(), f"Option name {name!r} must be lowercase"

        self.name: str = name
        self.description: Optional[str] = description
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
            raise InvalidArgument("channel_types must be instances of ChannelType")

        self.channel_types: List[ChannelType] = channel_types or []

        if choices is not None and autocomplete:
            raise InvalidArgument("can not specify both choices and autocomplete args")

        if choices is None:
            choices = []
        elif isinstance(choices, Mapping):
            choices = [OptionChoice(name, value) for name, value in choices.items()]
        elif isinstance(choices, Iterable) and not isinstance(choices[0], OptionChoice):
            choices = [OptionChoice(str(value), value) for value in choices]  # type: ignore
        else:
            choices = cast(List[OptionChoice], choices)

        self.choices: List[OptionChoice] = choices
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
            and self.channel_types == other.channel_types
            and self.autocomplete == other.autocomplete
            and self.min_value == other.min_value
            and self.max_value == other.max_value
        )

    @classmethod
    def from_dict(cls, payload: dict):
        if "options" in payload:
            payload["options"] = [Option.from_dict(p) for p in payload["options"]]
        if "choices" in payload:
            payload["choices"] = [OptionChoice(**p) for p in payload["choices"]]
        if "channel_types" in payload:
            payload["channel_types"] = [try_enum(ChannelType, v) for v in payload["channel_types"]]
        return Option(**payload)

    def add_choice(self, name: str, value: Union[str, int]) -> None:
        """
        Adds an OptionChoice to the list of current choices
        Parameters are the same as for :class:`OptionChoice`
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
        """
        Adds an option to the current list of options
        Parameters are the same as for :class:`Option`
        """
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

    def to_dict(self) -> Dict[str, Any]:
        payload = {
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
    """

    def __init__(
        self, type: ApplicationCommandType, name: str, default_permission: bool = True, **kwargs
    ):
        self.type: ApplicationCommandType = enum_if_int(ApplicationCommandType, type)
        self.name: str = name
        self.default_permission: bool = default_permission

        self.id: Optional[int] = _get_as_snowflake(kwargs, "id")
        self.application_id: Optional[int] = _get_as_snowflake(kwargs, "application_id")
        self.guild_id: Optional[int] = _get_as_snowflake(kwargs, "guild_id")
        self.version: Optional[int] = _get_as_snowflake(kwargs, "version")

        self._state: Optional[ConnectionState] = None
        self._always_synced: bool = False

    def __repr__(self) -> str:
        return f"<ApplicationCommand type={self.type!r} name={self.name!r}>"

    def __eq__(self, other) -> bool:
        return (
            self.type == other.type
            and self.name == other.name
            and self.default_permission == other.default_permission
        )

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "type": try_enum_to_int(self.type),
            "name": self.name,
        }
        if not self.default_permission:
            data["default_permission"] = False
        return data


class UserCommand(ApplicationCommand):
    def __init__(self, name: str, default_permission: bool = True, **kwargs):
        super().__init__(
            type=ApplicationCommandType.user,
            name=name,
            default_permission=default_permission,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<UserCommand name={self.name!r}>"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if data.pop("type", 0) == ApplicationCommandType.user.value:
            return UserCommand(**data)


class MessageCommand(ApplicationCommand):
    def __init__(self, name: str, default_permission: bool = True, **kwargs):
        super().__init__(
            type=ApplicationCommandType.message,
            name=name,
            default_permission=default_permission,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<MessageCommand name={self.name!r}>"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if data.pop("type", 0) == ApplicationCommandType.message.value:
            return MessageCommand(**data)


class SlashCommand(ApplicationCommand):
    """
    The base class for building slash commands.

    Parameters
    ----------
    name : :class:`str`
        The command name
    description : :class:`str`
        The command description (it'll be displayed by disnake)
    options : List[:class:`Option`]
        The options of the command
    default_permission : :class:`bool`
        Whether the command is enabled by default when the app is added to a guild
    """

    def __init__(
        self,
        name: str,
        description: str,
        options: list = None,
        default_permission: bool = True,
        **kwargs,
    ):
        assert (
            re.match(r"^[\w-]{1,32}$", name) is not None and name.islower()
        ), f"Slash command name {name!r} should consist of these symbols: a-z, 0-9, -, _"

        super().__init__(
            type=ApplicationCommandType.chat_input,
            name=name,
            default_permission=default_permission,
            **kwargs,
        )
        self.description: str = description
        self.options: List[Option] = options or []

    def __repr__(self) -> str:
        return (
            f"<SlashCommand name={self.name!r} description={self.description!r} "
            f"default_permission={self.default_permission!r} options={self.options!r}>"
        )

    def __str__(self) -> str:
        return f"<SlashCommand name={self.name!r}>"

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.description == other.description
            and self.options == other.options
        )

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]):
        if payload.pop("type", 1) != ApplicationCommandType.chat_input.value:
            return None
        if "options" in payload:
            payload["options"] = [Option.from_dict(p) for p in payload["options"]]
        return SlashCommand(**payload)

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
        """
        Adds an option to the current list of options
        Parameters are the same as for :class:`Option`
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

    def to_dict(self) -> Dict[str, Any]:
        res = super().to_dict()
        res["description"] = self.description
        res["options"] = [o.to_dict() for o in self.options]
        return res


class ApplicationCommandPermissions:
    """
    Represents application command permissions for a role or a user.

    Attributes
    ----------
    id : :class:`int`
        ID of a target
    type : :class:`int`
        1 if target is a role; 2 if target is a user
    permission : :class:`bool`
        Allow or deny the access to the command
    """

    __slots__ = ("id", "type", "permission")

    def __init__(self, *, data: Dict[str, Any]):
        self.id: int = int(data["id"])
        self.type: int = data["type"]
        self.permission: bool = data["permission"]

    def __repr__(self):
        return f"<ApplicationCommandPermissions id={self.id!r} type={self.type!r} permission={self.permission!r}>"

    def __eq__(self, other):
        return (
            self.id == other.id and self.type == other.type and self.permission == other.permission
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "type": self.type, "permission": self.permission}


class GuildApplicationCommandPermissions:
    """
    Represents application command permissions in a guild.

    Attributes
    ----------
    id: :class:`int`
        The ID of the corresponding command.
    application_id: :class:`int`
        The ID of your application.
    guild_id: :class:`int`
        The ID of the guild where these permissions are applied.
    permissions: List[:class:`ApplicationCommandPermissions`]
        A list of :class:`ApplicationCommandPermissions`.
    """

    __slots__ = ("_state", "id", "application_id", "guild_id", "permissions")

    def __init__(self, *, state: ConnectionState, data: Mapping[str, Any]):
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

    def to_dict(self) -> Any:
        return {
            "id": self.id,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "permissions": [perm.to_dict() for perm in self.permissions],
        }

    async def edit(
        self,
        *,
        permissions: Dict[Union[Role, Member], bool] = None,
        role_ids: Dict[int, bool] = None,
        user_ids: Dict[int, bool] = None,
    ) -> GuildApplicationCommandPermissions:
        """
        Replaces current permissions with specified ones.

        Parameters
        ----------
        permissions: Mapping[Union[:class:`Role`, :class:`Member`], :class:`bool`]
            Roles or users to booleans. ``True`` means "allow", ``False`` means "deny".
        role_ids: Mapping[:class:`int`, :class:`bool`]
            Role IDs to booleans.
        user_ids: Mapping[:class:`int`, :class:`bool`]
            User IDs to booleans.
        """

        data = []

        if permissions is not None:
            for obj, value in permissions.items():
                if isinstance(obj, Role):
                    target_type = 1
                elif isinstance(obj, Member):
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
    """
    Creates an object representing permissions of the application command.

    Parameters
    ----------
    command_id: :class:`int`
        The ID of the app command you want to apply these permissions to.
    permissions: Mapping[Union[:class:`Role`, :class:`Member`], :class:`bool`]
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
        permissions: Mapping[Union[Role, Member], bool] = None,
        role_ids: Mapping[int, bool] = None,
        user_ids: Mapping[int, bool] = None,
    ):
        self.id: int = command_id
        self.permissions: List[ApplicationCommandPermissions] = []

        if permissions is not None:
            for obj, value in permissions.items():
                if isinstance(obj, Role):
                    target_type = 1
                elif isinstance(obj, Member):
                    target_type = 2
                else:
                    raise ValueError("Permission target should be an instance of Role or abc.User")
                data = {"id": obj.id, "type": target_type, "permission": value}
                self.permissions.append(ApplicationCommandPermissions(data=data))

        if role_ids is not None:
            for role_id, value in role_ids.items():
                data = {"id": role_id, "type": 1, "permission": value}
                self.permissions.append(ApplicationCommandPermissions(data=data))

        if user_ids is not None:
            for user_id, value in user_ids.items():
                data = {"id": user_id, "type": 2, "permission": value}
                self.permissions.append(ApplicationCommandPermissions(data=data))

    def to_dict(self) -> Any:
        return {
            "id": self.id,
            "permissions": [perm.to_dict() for perm in self.permissions],
        }


PartialGuildAppCmdPerms = PartialGuildApplicationCommandPermissions


class UnresolvedGuildApplicationCommandPermissions:
    """
    Creates an object representing permissions of an application command,
    without a specific command ID.

    Parameters
    ----------
    permissions: Mapping[Union[:class:`Role`, :class:`Member`], :class:`bool`]
        Roles or users to booleans. ``True`` means "allow", ``False`` means "deny".
    roles: Mapping[:class:`int`, :class:`bool`]
        Role IDs to booleans.
    users: Mapping[:class:`int`, :class:`bool`]
        User IDs to booleans.
    owner: :class:`bool`
        Allow/deny the bot owner(s).
    """

    def __init__(
        self,
        *,
        permissions: Mapping[Union[Role, Member], bool] = None,
        role_ids: Mapping[int, bool] = None,
        user_ids: Mapping[int, bool] = None,
        owner: bool = None,
    ):
        self.permissions: Optional[Mapping[Union[Role, Member], bool]] = permissions
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
            the command ID to be used
        owners: Iterable[:class:`int`]
            the owner IDs, used for extending the user ID mapping
            based on the previously set ``owner`` permission if applicable

        Returns
        --------
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
                print("[WARNING] Conflicting permissions for owner(s) provided in users")

            resolved_users = {**users, **owner_ids}
        else:
            resolved_users = self.user_ids

        return PartialGuildApplicationCommandPermissions(
            command_id=command_id,
            permissions=self.permissions,
            role_ids=self.role_ids,
            user_ids=resolved_users,
        )
