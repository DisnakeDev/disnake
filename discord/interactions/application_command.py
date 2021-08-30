from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING, Union

from .base import Interaction

from ..channel import _threaded_channel_factory
from ..enums import OptionType, ApplicationCommandType, try_enum, enum_if_int
from ..guild import Guild
from ..role import Role
from ..user import User
from ..member import Member
from ..message import Message

__all__ = (
    'ApplicationCommandInteraction',
    'ApplicationCommandInteractionData',
    'ApplicationCommandInteractionDataResolved'
)

if TYPE_CHECKING:
    from ..types.interactions import (
        Interaction as InteractionPayload,
        ApplicationCommandInteractionData as ApplicationCommandInteractionDataPayload,
        ApplicationCommandInteractionDataResolved as ApplicationCommandInteractionDataResolvedPayload
    )
    from ..state import ConnectionState
    from ..channel import VoiceChannel, StageChannel, TextChannel, CategoryChannel, StoreChannel, PartialMessageable
    from ..threads import Thread

    InteractionChannel = Union[
        VoiceChannel, StageChannel, TextChannel, CategoryChannel, StoreChannel, Thread, PartialMessageable
    ]


class ApplicationCommandInteraction(Interaction):
    """Represents an interaction with an application command.

    Current examples are slash commands, user commands and message commands.

    .. versionadded:: 2.1

    Attributes
    -----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel_id: Optional[:class:`int`]
        The channel ID the interaction was sent from.
    application_id: :class:`int`
        The application ID that the interaction was for.
    author: Optional[Union[:class:`User`, :class:`Member`]]
        The user or member that sent the interaction.
    token: :class:`str`
        The token to continue the interaction. These are valid
        for 15 minutes.
    data: :class:`ApplicationCommandInteractionData`
        The wrapped interaction data.
    """
    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        super().__init__(data=data, state=state)
        self.data = ApplicationCommandInteractionData(
            data=data.get('data'),
            state=state,
            guild=self.guild
        )
        self.application_command = None
        self.command_failed = False

    @property
    def target(self):
        return self.data.target
    
    @property
    def options(self):
        return self.data.options


class ApplicationCommandInteractionData:
    """Represents the data of an interaction with an application command.

    .. versionadded:: 2.1

    Attributes
    ----------
    id: :class:`int`
        The application command ID.
    name: :class:`str`
        The application command name.
    type: :class:`ApplicationCommandType`
        The application command type.
    resolved: :class:`ApplicationCommandInteractionDataResolved`
        All resolved objects related to this interaction.
    options: Dict[:class:`str`, :class:`Any`]
        Slash command option names and values entered by a user.
    target_id: :class:`int`
        ID of the user or message targetted by a user or message command
    target: Union[:class:`User`, :class:`Member`, :class:`Message`]
        The user or message targetted by a user or message command
    """

    __slots__ = (
        'id',
        'name',
        'type',
        'target_id',
        'target',
        'resolved',
        'options'
    )

    def __init__(self, *, data: ApplicationCommandInteractionDataPayload, state: ConnectionState, guild: Guild):
        data = {} if data is None else data
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.type: ApplicationCommandType = try_enum(ApplicationCommandType, data['type'])
        self.resolved = ApplicationCommandInteractionDataResolved(
            data=data.get('resolved'),
            state=state,
            guild=guild
        )
        target_id = data.get('target_id')
        self.target_id: Optional[int] = None if target_id is None else int(target_id)
        self.target: Optional[Union[User, Member, Message]] = self.resolved.get(self.target_id)
        def option_payload_to_value(payload):
            value = payload.get('value')
            if value is not None:
                return self.resolved.get_with_type(value, payload['type'], value)
            return {
                option['name']: option_payload_to_value(option)
                for option in payload.get('options', [])
            }
        self.options: Dict[str, Any] = {
            option['name']: option_payload_to_value(option)
            for option in data.get('options', [])
        }


class ApplicationCommandInteractionDataResolved:
    """Represents the resolved data related to
    an interaction with an application command.

    .. versionadded:: 2.1

    Attributes
    ----------
    members: :class:`Dict[int, Member]`
        IDs and prtial members (missing 'deaf' and 'mute')
    users: :class:`Dict[int, User]`
        IDs and users
    roles: :class:`Dict[int, Role]`
        IDs and roles
    channels: :class:`Dict[int, Channel]`
        IDs and partial channels (only 'id', 'name' and 'permissions' are included)
    messages: :class:`Dict[int, Message]`
        IDs and messages
    """

    __slots__ = (
        'members',
        'users',
        'roles',
        'channels',
        'messages'
    )

    def __init__(self, *, data: ApplicationCommandInteractionDataResolvedPayload, state: ConnectionState, guild: Guild):
        data = data or {}

        self.members: Dict[int, Member] = {}
        self.users: Dict[int, User] = {}
        self.roles: Dict[int, Role] = {}
        self.channels: Dict[int, InteractionChannel] = {}
        self.messages: Dict[int, Message] = {}

        users = data.get('users', {})
        members = data.get('members', {})
        roles = data.get('roles', {})
        channels = data.get('channels', {})
        messages = data.get('messages', {})

        for str_id, user in users.items():
            user_id = int(str_id)
            member = members.get(str_id)
            if member is not None:
                self.members[user_id] = Member(
                    data={**member, 'user': user},
                    guild=guild,
                    state=state
                )
            else:
                self.users[user_id] = User(state=state, data=user)
        
        for str_id, role in roles.items():
            self.roles[int(str_id)] = Role(guild=guild, state=state, data=role)
        
        for str_id, channel in channels.items():
            factory, ch_type = _threaded_channel_factory(channel['type'])
            if factory:
                channel['position'] = 0
                self.channels[int(str_id)] = factory(guild=guild, state=state, data=channel)
        
        for str_id, message in messages.items():
            channel_id = int(message['channel_id'])
            channel = guild.get_channel(channel_id) if guild else None
            if channel is None:
                channel = state.get_channel(channel_id)
            self.messages[int(str_id)] = Message(state=state, channel=channel, data=message)
    
    def get_with_type(self, key: Any, option_type: OptionType, default: Any = None):
        if isinstance(option_type, int):
            option_type = try_enum(OptionType, option_type)
        if option_type is OptionType.mentionable:
            key = int(key)
            result = self.members.get(key)
            if result is not None:
                return result
            result = self.users.get(key)
            if result is not None:
                return result
            return self.roles.get(key, default)
        
        if option_type is OptionType.user:
            key = int(key)
            member = self.members.get(key)
            if member is not None:
                return member
            return self.users.get(key, default)

        if option_type is OptionType.channel:
            return self.channels.get(int(key), default)
        
        if option_type is OptionType.role:
            return self.roles.get(int(key), default)
        
        return default

    def get(self, key: int):
        if key is None:
            return None
        res = self.members.get(key)
        if res is not None:
            return res
        res = self.users.get(key)
        if res is not None:
            return res
        res = self.roles.get(key)
        if res is not None:
            return res
        res = self.channels.get(key)
        if res is not None:
            return res
        return self.messages.get(key)
