import re
from typing import Dict, List, Optional, Union
from .enums import ApplicationCommandType, OptionType, try_enum, enum_if_int, try_enum_to_int
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


def application_command_factory(data: dict):
    cmd_type = try_enum(ApplicationCommandType, data.get("type", 1))
    if cmd_type is ApplicationCommandType.chat_input:
        return SlashCommand.from_dict(data)
    if cmd_type is ApplicationCommandType.user:
        return UserCommand.from_dict(data)
    if cmd_type is ApplicationCommandType.message:
        return MessageCommand.from_dict(data)


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

    def __repr__(self):
        return "<OptionChoice name='{0.name}' value={0.value}>".format(self)

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.value == other.value
        )
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value
        }


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
        the option type, e.g. ``OptionType.USER``
    required: :class:`bool`
        whether this option is required or not
    choices: List[:class:`OptionChoice`]
        the list of option choices
    options: List[:class:`Option`]
        the list of sub options. You can only specify this parameter if
        the ``type`` is :class:`OptionType.SUB_COMMAND` or :class:`OptionType.SUB_COMMAND_GROUP`
    """

    __slots__ = ("name", "description", "type", "required", "choices", "options", "_choice_connectors")

    def __init__(
        self,
        name: str,
        description: str = None,
        type: OptionType = None,
        required: bool = False,
        choices: List[OptionChoice] = None,
        options: list = None
    ):
        assert name.islower(), f"Option name {name!r} must be lowercase"
        self.name: str = name
        self.description: str = description
        self.type: OptionType = enum_if_int(OptionType, type) or OptionType.string
        self.required: bool = required
        self.choices: List[OptionChoice] = choices or []
        self.options: List[Option] = options or []
        # self._choice_connectors = {}
        
        # for i, choice in enumerate(self.choices):
        #     if self.type == Type.INTEGER:
        #         if not isinstance(choice.value, int):
        #             self._choice_connectors[i] = choice.value
        #             choice.value = i
        #     elif self.type == Type.STRING:
        #         if not isinstance(choice.value, str):
        #             valid_value = f"option_choice_{i}"
        #             self._choice_connectors[valid_value] = choice.value
        #             choice.value = valid_value

    def __repr__(self):
        return (
            f'<Option name={self.name!r} description={self.description!r} '
            f'type={self.type!r} required={self.required!r} choices={self.choices!r} '
            f'options={self.options!r}>'
        )

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.description == other.description and
            self.type == other.type and
            self.required == other.required and
            self.choices == other.choices and
            self.options == other.options
        )

    @classmethod
    def from_dict(cls, payload: dict):
        if 'options' in payload:
            payload['options'] = [Option.from_dict(p) for p in payload['options']]
        if 'choices' in payload:
            payload['choices'] = [OptionChoice(**p) for p in payload['choices']]
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
        options: list = None
    ) -> None:
        """
        Adds an option to the current list of options
        Parameters are the same as for :class:`Option`
        """
        if self.type == 1:
            if type < 3:
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
                options=options
            )
        )

    def to_dict(self) -> dict:
        payload = {
            'name': self.name,
            'description': self.description,
            'type': try_enum_to_int(self.type)
        }
        if self.required:
            payload['required'] = True
        if len(self.choices) > 0:
            payload['choices'] = [c.to_dict() for c in self.choices]
        if len(self.options) > 0:
            payload['options'] = [o.to_dict() for o in self.options]
        return payload


class ApplicationCommand:
    """
    Base class for application commands
    """
    def __init__(self, type: ApplicationCommandType, **kwargs):
        self.type: ApplicationCommandType = enum_if_int(ApplicationCommandType, type)
        self.id: Optional[int] = kwargs.pop('id', None)
        if self.id:
            self.id = int(self.id)
        self.application_id: Optional[int] = kwargs.pop('application_id', None)
        if self.application_id:
            self.application_id = int(self.application_id)
        self._always_synced: bool = False
    
    def __eq__(self, other):
        return self._always_synced


class UserCommand(ApplicationCommand):
    def __init__(self, name: str, **kwargs):
        super().__init__(ApplicationCommandType.user, **kwargs)
        self.name: str = name
    
    def __repr__(self):
        return f"<UserCommand name={self.name!r}>"
    
    def __eq__(self, other):
        return self._always_synced or (
            self.type == other.type and
            self.name == other.name
        )

    def to_dict(self, **kwargs) -> dict:
        return {
            "type": try_enum_to_int(self.type),
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        if data.pop("type", 0) == ApplicationCommandType.user.value:
            return UserCommand(**data)


class MessageCommand(ApplicationCommand):
    def __init__(self, name: str, **kwargs):
        super().__init__(ApplicationCommandType.message, **kwargs)
        self.name: str = name
    
    def __repr__(self):
        return f"<MessageCommand name={self.name!r}>"
    
    def __eq__(self, other):
        return self._always_synced or (
            self.type == other.type and
            self.name == other.name
        )

    def to_dict(self, **kwargs) -> dict:
        return {
            "type": try_enum_to_int(self.type),
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: dict):
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
        The command description (it'll be displayed by discord)
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

    def __repr__(self):
        return (
            f'<SlashCommand name={self.name!r} description={self.description!r}'
            f'options={self.options!r} default_permission={self.default_permission!r}>'
        )

    def __eq__(self, other):
        return self._always_synced or (
            self.type == other.type and
            self.name == other.name and
            self.description == other.description and
            self.options == other.options
        )

    @classmethod
    def from_dict(cls, payload: dict):
        if payload.pop("type", 1) != ApplicationCommandType.chat_input.value:
            return None
        if 'options' in payload:
            payload['options'] = [Option.from_dict(p) for p in payload['options']]
        return SlashCommand(**payload)

    def add_option(
        self,
        name: str,
        description: str = None,
        type: int = None,
        required: bool = False,
        choices: List[OptionChoice] = None,
        options: list = None
    ) -> None:
        """
        Adds an option to the current list of options
        Parameters are the same as for :class:`Option`
        """
        self.options.append(
            Option(
                name=name,
                description=description,
                type=type,
                required=required,
                choices=choices,
                options=options
            )
        )

    def to_dict(self, *, hide_name=False) -> dict:
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

    def to_dict(self) -> dict:
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
        instances of :class:`discord.Role` and :class:`discord.User`

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
    def from_dict(cls, data: dict):
        return ApplicationCommandPermissions([
            RawApplicationCommandPermission.from_dict(perm)
            for perm in data["permissions"]
        ])

    def to_dict(self) -> dict:
        return {
            "permissions": [perm.to_dict() for perm in self.permissions]
        }
