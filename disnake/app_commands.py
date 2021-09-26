from __future__ import annotations
from abc import ABC, abstractmethod

import re
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Union, cast

from .enums import ApplicationCommandType, ChannelType, OptionType, try_enum, enum_if_int, try_enum_to_int
from .errors import InvalidArgument
from .role import Role
from .user import User

__all__ = (
    "application_command_factory",
    "ApplicationCommand",
    "SlashCommand",
    "UserCommand",
    "MessageCommand",
    "OptionChoice",
    "Option",
    "ApplicationCommandPermissions",
    "RawApplicationCommandPermission",
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

    def __init__(self, name: str, value: Union[str, int]):
        self.name: str = name
        self.value: Union[str, int] = value

    def __repr__(self) -> str:
        return f'<OptionChoice name={self.name} value={self.value}>'

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name and
            self.value == other.value
        )
    
    def to_dict(self) -> Dict[str, Union[str, int]]:
        return {
            'name': self.name,
            'value': self.value
        }


Choices = Union[List[OptionChoice], Dict[str, Union[str, int]], List[Union[str, int]]]

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
    """

    __slots__ = (
        'name',
        'description',
        'type',
        'required',
        'choices',
        'options',
        'channel_types',
        'autocomplete',
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
    ):
        assert name.islower(), f"Option name {name!r} must be lowercase"

        self.name: str = name
        self.description: Optional[str] = description
        self.type: OptionType = enum_if_int(OptionType, type) or OptionType.string
        self.required: bool = required
        self.options: List[Option] = options or []

        if (
            channel_types is not None and
            not all(isinstance(t, ChannelType) for t in channel_types)
        ):
            raise InvalidArgument('channel_types must be instances of ChannelType')

        self.channel_types: List[ChannelType] = channel_types or []

        if choices is not None and autocomplete:
            raise InvalidArgument("can not specify both choices and autocomplete args")

        if choices is None:
            choices = []
        elif isinstance(choices, Mapping):
            choices = [OptionChoice(name, value) for name, value in choices.items()]
        elif isinstance(choices, Iterable) and not isinstance(choices[0], OptionChoice):
            choices = [OptionChoice(str(value), value) for value in choices] # type: ignore
        else:
            choices = cast(List[OptionChoice], choices)
        
        self.choices: List[OptionChoice] = choices
        self.autocomplete: bool = autocomplete

    def __repr__(self) -> str:
        return (
            f'<Option name={self.name!r} description={self.description!r} '
            f'type={self.type!r} required={self.required!r} choices={self.choices!r} '
            f'options={self.options!r}>'
        )

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name and
            self.description == other.description and
            self.type == other.type and
            self.required == other.required and
            self.choices == other.choices and
            self.options == other.options and
            self.channel_types == other.channel_types and
            self.autocomplete == other.autocomplete
        )

    @classmethod
    def from_dict(cls, payload: dict):
        if 'options' in payload:
            payload['options'] = [Option.from_dict(p) for p in payload['options']]
        if 'choices' in payload:
            payload['choices'] = [OptionChoice(**p) for p in payload['choices']]
        if 'channel_types' in payload:
            payload['channel_types'] = [try_enum(ChannelType, v) for v in payload['channel_types']]
        return Option(**payload)

    def add_choice(self, name: str, value: Union[str, int]) -> None:
        """
        Adds an OptionChoice to the list of current choices
        Parameters are the same as for :class:`OptionChoice`
        """
        # Wrap the value
        # true_value = value
        # if self.type == OptionType.string:
        #     if not isinstance(value, str):
        #         true_value = f"option_choice_{len(self._choice_connectors)}"
        #         self._choice_connectors[true_value] = value
        # elif self.type == OptionType.integer:
        #     if not isinstance(value, int):
        #         true_value = len(self._choice_connectors)
        #         self._choice_connectors[true_value] = value
        # Add an option choice
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
    ) -> None:
        """
        Adds an option to the current list of options
        Parameters are the same as for :class:`Option`
        """
        type = type or OptionType.string
        if self.type == 1:
            if type in [1, 2]:
                raise ValueError('sub_command can only be nested in a sub_command_group')
        elif self.type == 2:
            if type != 1:
                raise ValueError('Expected sub_command in this sub_command_group')
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
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            'name': self.name,
            'description': self.description,
            'type': try_enum_to_int(self.type)
        }
        if self.required:
            payload['required'] = True
        if self.autocomplete:
            payload['autocomplete'] = True
        if len(self.choices) > 0:
            payload['choices'] = [c.to_dict() for c in self.choices]
        if len(self.options) > 0:
            payload['options'] = [o.to_dict() for o in self.options]
        if len(self.channel_types) > 0:
            payload['channel_types'] = [v.value for v in self.channel_types]
        return payload


class ApplicationCommand(ABC):
    """
    The base class for application commands
    """
    name: str
    
    def __init__(self, type: ApplicationCommandType, **kwargs):
        self.type: ApplicationCommandType = enum_if_int(ApplicationCommandType, type)
        self.id: Optional[int] = kwargs.pop('id', None)
        if self.id:
            self.id = int(self.id)
        self.application_id: Optional[int] = kwargs.pop('application_id', None)
        if self.application_id:
            self.application_id = int(self.application_id)
        self._always_synced: bool = False
    
    def __repr__(self) -> str:
        return f'<ApplicationCommand id={self.id!r} type={self.type!r}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, ApplicationCommand)
    
    @abstractmethod
    def to_dict(self) -> Any:
        raise NotImplementedError


class UserCommand(ApplicationCommand):
    def __init__(self, name: str, **kwargs):
        super().__init__(ApplicationCommandType.user, **kwargs)
        self.name: str = name
    
    def __repr__(self) -> str:
        return f"<UserCommand name={self.name!r}>"
    
    def __eq__(self, other) -> bool:
        return (
            self.type == other.type and
            self.name == other.name
        )

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        return {
            "type": try_enum_to_int(self.type),
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if data.pop("type", 0) == ApplicationCommandType.user.value:
            return UserCommand(**data)


class MessageCommand(ApplicationCommand):
    def __init__(self, name: str, **kwargs):
        super().__init__(ApplicationCommandType.message, **kwargs)
        self.name: str = name
    
    def __repr__(self) -> str:
        return f"<MessageCommand name={self.name!r}>"
    
    def __eq__(self, other) -> bool:
        return (
            self.type == other.type and
            self.name == other.name
        )

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        return {
            "type": try_enum_to_int(self.type),
            "name": self.name
        }
    
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
        The options of the command. See :ref:`option`
    default_permission : :class:`bool`
        Whether the command is enabled by default when the app is added to a guild
    """

    def __init__(
        self,
        name: str,
        description: str,
        options: list = None,
        default_permission: bool = True,
        **kwargs
    ):
        super().__init__(ApplicationCommandType.chat_input, **kwargs)

        assert re.match(r"^[\w-]{1,32}$", name) is not None and name.islower(),\
            f"Slash command name {name!r} should consist of these symbols: a-z, 0-9, -, _"

        self.name: str = name
        self.description: str = description
        self.options: List[Option] = options or []
        self.default_permission: bool = default_permission
        self.permissions = ApplicationCommandPermissions()

    def __repr__(self) -> str:
        return (
            f'<SlashCommand name={self.name!r} description={self.description!r} '
            f'default_permission={self.default_permission!r} options={self.options!r}>'
        )

    def __str__(self) -> str:
        return f'<SlashCommand name={self.name!r}>'

    def __eq__(self, other) -> bool:
        return (
            self.type == other.type and
            self.name == other.name and
            self.description == other.description and
            self.options == other.options
        )

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]):
        if payload.pop("type", 1) != ApplicationCommandType.chat_input.value:
            return None
        if 'options' in payload:
            payload['options'] = [Option.from_dict(p) for p in payload['options']]
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
            )
        )

    def to_dict(self, *, hide_name: bool = False) -> Dict[str, Any]:
        res = {
            "type": try_enum_to_int(self.type),
            "description": self.description,
            "options": [o.to_dict() for o in self.options]
        }
        if not self.default_permission:
            res["default_permission"] = False
        if not hide_name:
            res["name"] = self.name
        return res


class RawApplicationCommandPermission:
    """
    Represents command permissions for a role or a user.
    Attributes
    ----------
    id : :class:`int`
        ID of a target
    type : :class:`int`
        1 if target is a role; 2 if target is a user
    permission : :class:`bool`
        allow or deny the access to the command
    """

    __slots__ = ("id", "type", "permission")

    def __init__(self, id: int, type: int, permission: bool):
        self.id: int = id
        self.type: int = type
        self.permission: bool = permission

    def __repr__(self):
        return "<RawCommandPermission id={0.id} type={0.type} permission={0.permission}>".format(self)

    @classmethod
    def from_pair(cls, target: Union[Role, User], permission: bool):
        if not isinstance(target, (Role, User)):
            raise InvalidArgument("target should be Role or User")
        if not isinstance(permission, bool):
            raise InvalidArgument("permission should be bool")
        return RawApplicationCommandPermission(
            id=target.id,
            type=1 if isinstance(target, Role) else 2,
            permission=permission
        )

    @classmethod
    def from_dict(cls, data: dict):
        return RawApplicationCommandPermission(
            id=data["id"],
            type=data["type"],
            permission=data["permission"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "permission": self.permission
        }


class ApplicationCommandPermissions:
    """
    Represents application command permissions.
    Roughly equivalent to a list of :class:`RawApplicationCommandPermission`
    Application command permissions are checked on the server side.
    Only guild application commands can have this type of permissions.

    Parameters
    ----------
    raw_permissions : List[:class:`RawApplicationCommandPermission`]
        a list of :class:`RawApplicationCommandPermission`.
        However, :meth:`from_pairs` or :meth:`from_ids`
        might be more convenient.
    """

    def __init__(self, raw_permissions: List[RawApplicationCommandPermission] = None):
        self.permissions: List[RawApplicationCommandPermission] = raw_permissions or []

    def __repr__(self):
        return "<ApplicationCommandPermissions permissions={0.permissions!r}>".format(self)

    @classmethod
    def from_pairs(cls, permissions: Dict[Union[Role, User], bool]):
        """
        Creates :class:`ApplicationCommandPermissions` using
        instances of :class:`disnake.Role` and :class:`disnake.User`

        Parameters
        ----------
        permissions: Dict[Union[:class:`Role`, :class:`User`], :class:`bool`]
            a dictionary with permissions for users and roles.
        """
        raw_perms = [
            RawApplicationCommandPermission.from_pair(target, perm)
            for target, perm in permissions.items()
        ]

        return ApplicationCommandPermissions(raw_perms)

    @classmethod
    def from_ids(cls, role_perms: Dict[int, bool] = None, user_perms: Dict[int, bool] = None):
        """
        Creates :class:`ApplicationCommandPermissions` from
        2 dictionaries of IDs and permissions.

        Parameters
        ----------
        role_perms: Dict[:class:`int`, :class:`bool`]
            a dictionary of {``role_id``: :class:`bool`}
        user_perms: Dict[:class:`int`, :class:`bool`]
            a dictionary of {``user_id``: :class:`bool`}
        """
        role_perms = role_perms or {}
        user_perms = user_perms or {}
        raw_perms = [
            RawApplicationCommandPermission(role_id, 1, perm)
            for role_id, perm in role_perms.items()
        ]

        for user_id, perm in user_perms.items():
            raw_perms.append(RawApplicationCommandPermission(user_id, 2, perm))
        return ApplicationCommandPermissions(raw_perms)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]):
        return ApplicationCommandPermissions([
            RawApplicationCommandPermission.from_dict(perm)
            for perm in data["permissions"]
        ])

    def to_dict(self) -> Any:
        return {
            "permissions": [perm.to_dict() for perm in self.permissions]
        }
