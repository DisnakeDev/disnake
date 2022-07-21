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

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple, TypeVar, Union, cast

from .. import utils
from ..channel import (
    CategoryChannel,
    PartialMessageable,
    StageChannel,
    StoreChannel,
    TextChannel,
    VoiceChannel,
    _threaded_guild_channel_factory,
)
from ..enums import ApplicationCommandType, ChannelType, OptionType, try_enum
from ..guild import Guild
from ..member import Member
from ..message import Attachment, Message
from ..object import Object
from ..role import Role
from ..user import User
from .base import Interaction

__all__ = (
    "ApplicationCommandInteraction",
    "GuildCommandInteraction",
    "UserCommandInteraction",
    "MessageCommandInteraction",
    "ApplicationCommandInteractionData",
    "ApplicationCommandInteractionDataOption",
    "ApplicationCommandInteractionDataResolved",
    # aliases (we're trying to find out which one catches on)
    "CommandInteraction",
    "CmdInteraction",
    "CommandInter",
    "CmdInter",
    "AppCommandInteraction",
    "AppCommandInter",
    "AppCmdInter",
)

MISSING = utils.MISSING

if TYPE_CHECKING:
    from ..abc import MessageableChannel
    from ..ext.commands import InvokableApplicationCommand
    from ..state import ConnectionState
    from ..threads import Thread
    from ..types.interactions import (
        ApplicationCommandInteraction as ApplicationCommandInteractionPayload,
        ApplicationCommandInteractionData as ApplicationCommandInteractionDataPayload,
        ApplicationCommandInteractionDataResolved as ApplicationCommandInteractionDataResolvedPayload,
    )

    InteractionChannel = Union[
        VoiceChannel,
        StageChannel,
        TextChannel,
        CategoryChannel,
        StoreChannel,
        Thread,
        PartialMessageable,
        VoiceChannel,
    ]


AppCmdDataOptionT = TypeVar("AppCmdDataOptionT", bound="ApplicationCommandInteractionDataOption")


class ApplicationCommandInteraction(Interaction):
    """Represents an interaction with an application command.

    Current examples are slash commands, user commands and message commands.

    .. versionadded:: 2.1

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction's type.
    application_id: :class:`int`
        The application ID that the interaction was for.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel_id: :class:`int`
        The channel ID the interaction was sent from.
    author: Union[:class:`User`, :class:`Member`]
        The user or member that sent the interaction.
    locale: :class:`str`
        The selected language of the interaction's author.

        .. versionadded:: 2.4

    guild_locale: Optional[:class:`str`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionadded:: 2.4

    token: :class:`str`
        The token to continue the interaction. These are valid for 15 minutes.
    data: :class:`ApplicationCommandInteractionData`
        The wrapped interaction data.
    client: :class:`Client`
        The interaction client.
    """

    def __init__(self, *, data: ApplicationCommandInteractionPayload, state: ConnectionState):
        super().__init__(data=data, state=state)
        self.data = ApplicationCommandInteractionData(
            data=data["data"], state=state, guild_id=self.guild_id
        )
        self.application_command: InvokableApplicationCommand = MISSING
        self.command_failed: bool = False

    @property
    def target(self) -> Optional[Union[User, Member, Message]]:
        """Optional[Union[:class:`abc.User`, :class:`Message`]]: The user or message targetted by a user or message command"""
        return self.data.target

    @property
    def options(self) -> Dict[str, Any]:
        """Dict[:class:`str`, :class:`Any`]: The full option tree, including nestings"""
        return {opt.name: opt._simplified_value() for opt in self.data.options}

    @property
    def filled_options(self) -> Dict[str, Any]:
        """Dict[:class:`str`, :class:`Any`]: The options of the command (or sub-command) being invoked"""
        _, kwargs = self.data._get_chain_and_kwargs()
        return kwargs


class GuildCommandInteraction(ApplicationCommandInteraction):
    """An ApplicationCommandInteraction Context subclass meant for annotation.

    No runtime behavior is changed but annotations are modified
    to seem like the interaction can only ever be invoked in guilds.
    """

    guild: Guild
    me: Member
    guild_locale: str


class UserCommandInteraction(ApplicationCommandInteraction):
    """An ApplicationCommandInteraction Context subclass meant for annotation.

    No runtime behavior is changed but annotations are modified
    to seem like the interaction is specifically a user command.
    """

    target: Union[User, Member]


class MessageCommandInteraction(ApplicationCommandInteraction):
    """An ApplicationCommandInteraction Context subclass meant for annotation.

    No runtime behavior is changed but annotations are modified
    to seem like the interaction is specifically a message command.
    """

    target: Message


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
    options: List[:class:`ApplicationCommandInteractionDataOption`]
        A list of options from the API.
    target_id: :class:`int`
        ID of the user or message targetted by a user or message command
    target: Union[:class:`User`, :class:`Member`, :class:`Message`]
        The user or message targetted by a user or message command
    """

    __slots__ = (
        "id",
        "name",
        "type",
        "target_id",
        "target",
        "resolved",
        "options",
    )

    def __init__(
        self,
        *,
        data: ApplicationCommandInteractionDataPayload,
        state: ConnectionState,
        guild_id: Optional[int],
    ):
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.type: ApplicationCommandType = try_enum(ApplicationCommandType, data["type"])
        self.resolved = ApplicationCommandInteractionDataResolved(
            data=data.get("resolved", {}), state=state, guild_id=guild_id
        )
        self.target_id: Optional[int] = utils._get_as_snowflake(data, "target_id")
        self.target: Optional[Union[User, Member, Message]] = self.resolved.get(self.target_id)  # type: ignore
        self.options: List[ApplicationCommandInteractionDataOption] = [
            ApplicationCommandInteractionDataOption(data=d, resolved=self.resolved)
            for d in data.get("options", [])
        ]

    def _get_chain_and_kwargs(
        self, chain: Tuple[str, ...] = None
    ) -> Tuple[Tuple[str, ...], Dict[str, Any]]:
        """
        Returns a chain of sub-command names and a dict of filled options.
        """
        if chain is None:
            chain = ()
        for option in self.options:
            if option.value is None:
                # Extend the chain and collect kwargs in the nesting
                return option._get_chain_and_kwargs(chain + (option.name,))
            return chain, {o.name: o.value for o in self.options}
        return chain, {}

    def _get_focused_option(self) -> Optional[ApplicationCommandInteractionDataOption]:
        for option in self.options:
            if option.focused:
                return option
            if option.value is None:
                # This means that we're inside a group/subcmd now
                # We can use 'return' here because user can only
                # choose one subcommand per interaction
                return option._get_focused_option()

        return None

    @property
    def focused_option(self) -> ApplicationCommandInteractionDataOption:
        """The focused option"""
        # don't annotate as None for user experience
        return self._get_focused_option()  # type: ignore


class ApplicationCommandInteractionDataOption:
    """This class represents the structure of an interaction data option from the API.

    Attributes
    ----------
    name: :class:`str`
        The option's name.
    type: :class:`OptionType`
        The option's type.
    value: :class:`Any`
        The option's value.
    options: List[:class:`ApplicationCommandInteractionDataOption`]
        The list of options of this option. Only exists for subcommands and groups.
    focused: :class:`bool`
        Whether this option is focused by the user. May be ``True`` in
        autocomplete interactions.
    """

    __slots__ = ("name", "type", "value", "options", "focused")

    def __init__(
        self, *, data: Mapping[str, Any], resolved: ApplicationCommandInteractionDataResolved
    ):
        self.name: str = data["name"]
        self.type: OptionType = try_enum(OptionType, data["type"])
        value = data.get("value")
        if value is not None:
            self.value: Any = resolved.get_with_type(value, self.type.value, value)
        else:
            self.value: Any = None
        self.options: List[ApplicationCommandInteractionDataOption] = [
            ApplicationCommandInteractionDataOption(data=d, resolved=resolved)
            for d in data.get("options", [])
        ]
        self.focused: bool = data.get("focused", False)

    def _simplified_value(self) -> Any:
        if self.value is not None:
            return self.value
        return {opt.name: opt._simplified_value() for opt in self.options}

    def _get_focused_option(self) -> Optional[ApplicationCommandInteractionDataOption]:
        for option in self.options:
            if option.focused:
                return option
            if option.value is None:
                return option._get_focused_option()
        return None

    def _get_chain_and_kwargs(
        self, chain: Tuple[str, ...] = None
    ) -> Tuple[Tuple[str, ...], Dict[str, Any]]:
        if chain is None:
            chain = ()
        for option in self.options:
            if option.value is None:
                # Extend the chain and collect kwargs in the nesting
                return option._get_chain_and_kwargs(chain + (option.name,))
            return chain, {o.name: o.value for o in self.options}
        return chain, {}


class ApplicationCommandInteractionDataResolved:
    """Represents the resolved data related to an interaction with an application command.

    .. versionadded:: 2.1

    Attributes
    ----------
    members: Dict[:class:`int`, :class:`Member`]
        A mapping of IDs to partial members (``deaf`` and ``mute`` attributes are missing).
    users: Dict[:class:`int`, :class:`User`]
        A mapping of IDs to users.
    roles: Dict[:class:`int`, :class:`Role`]
        A mapping of IDs to roles.
    channels: Dict[:class:`int`, Channel]
        A mapping of IDs to partial channels (only ``id``, ``name`` and ``permissions`` are included,
        threads also have ``thread_metadata`` and ``parent_id``).
    messages: Dict[:class:`int`, :class:`Message`]
        A mapping of IDs to messages.
    attachments: Dict[:class:`int`, :class:`Attachment`]
        A mapping of IDs to attachments.

        .. versionadded:: 2.4
    """

    __slots__ = ("members", "users", "roles", "channels", "messages", "attachments")

    def __init__(
        self,
        *,
        data: ApplicationCommandInteractionDataResolvedPayload,
        state: ConnectionState,
        guild_id: Optional[int],
    ):
        data = data or {}

        self.members: Dict[int, Member] = {}
        self.users: Dict[int, User] = {}
        self.roles: Dict[int, Role] = {}
        self.channels: Dict[int, InteractionChannel] = {}
        self.messages: Dict[int, Message] = {}
        self.attachments: Dict[int, Attachment] = {}

        users = data.get("users", {})
        members = data.get("members", {})
        roles = data.get("roles", {})
        channels = data.get("channels", {})
        messages = data.get("messages", {})
        attachments = data.get("attachments", {})

        guild: Optional[Guild] = None
        # `guild_fallback` is only used in guild contexts, so this `MISSING` value should never be used.
        # We need to define it anyway to satisfy the typechecker.
        guild_fallback: Union[Guild, Object] = MISSING
        if guild_id is not None:
            guild = state._get_guild(guild_id)
            guild_fallback = guild or Object(id=guild_id)

        for str_id, user in users.items():
            user_id = int(str_id)
            member = members.get(str_id)
            if member is not None:
                self.members[user_id] = (
                    guild
                    and guild.get_member(user_id)
                    or Member(
                        data=member,
                        user_data=user,
                        guild=guild_fallback,  # type: ignore
                        state=state,
                    )
                )
            else:
                self.users[user_id] = User(state=state, data=user)

        for str_id, role in roles.items():
            self.roles[int(str_id)] = Role(
                guild=guild_fallback,  # type: ignore
                state=state,
                data=role,
            )

        for str_id, channel in channels.items():
            channel_id = int(str_id)
            factory, ch_type = _threaded_guild_channel_factory(channel["type"])
            if factory:
                channel["position"] = 0  # type: ignore
                self.channels[channel_id] = (
                    guild
                    and guild.get_channel(channel_id)
                    or factory(
                        guild=guild_fallback,  # type: ignore
                        state=state,
                        data=channel,  # type: ignore
                    )
                )
            else:
                self.channels[channel_id] = PartialMessageable(
                    state=state, id=channel_id, type=try_enum(ChannelType, channel["type"])
                )

        for str_id, message in messages.items():
            channel_id = int(message["channel_id"])
            channel = cast(
                "Optional[MessageableChannel]",
                (guild and guild.get_channel(channel_id) or state.get_channel(channel_id)),
            )
            if channel is None:
                # The channel is not part of `resolved.channels`,
                # so we need to fall back to partials here.
                channel = PartialMessageable(state=state, id=channel_id, type=None)
            self.messages[int(str_id)] = Message(state=state, channel=channel, data=message)

        for str_id, attachment in attachments.items():
            self.attachments[int(str_id)] = Attachment(data=attachment, state=state)

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

        if option_type is OptionType.attachment:
            return self.attachments.get(int(key), default)

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
        res = self.messages.get(key)
        if res is not None:
            return res
        res = self.attachments.get(key)
        if res is not None:
            return res

        return None


# People asked about shorter aliases, let's see which one catches on the most
CommandInteraction = ApplicationCommandInteraction
CmdInteraction = ApplicationCommandInteraction
CommandInter = ApplicationCommandInteraction
CmdInter = ApplicationCommandInteraction
AppCommandInteraction = ApplicationCommandInteraction
AppCommandInter = ApplicationCommandInteraction
AppCmdInter = ApplicationCommandInteraction
