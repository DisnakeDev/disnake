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

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple, TypeVar, Union

from ..channel import _threaded_channel_factory
from ..enums import ApplicationCommandType, OptionType, try_enum
from ..guild import Guild
from ..member import Member
from ..message import Message
from ..role import Role
from ..user import User
from ..utils import MISSING
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

if TYPE_CHECKING:
    from ..channel import (
        CategoryChannel,
        PartialMessageable,
        StageChannel,
        StoreChannel,
        TextChannel,
        VoiceChannel,
    )
    from ..ext.commands import AutoShardedBot, Bot, InvokableApplicationCommand
    from ..state import ConnectionState
    from ..threads import Thread
    from ..types.interactions import (
        ApplicationCommandInteractionData as ApplicationCommandInteractionDataPayload,
        ApplicationCommandInteractionDataResolved as ApplicationCommandInteractionDataResolvedPayload,
        Interaction as InteractionPayload,
    )

    BotBase = Union[Bot, AutoShardedBot]

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
    bot: Optional[:class:`.Bot`]
        The interaction's bot. There is an alias for this named ``client``.
    author: Optional[Union[:class:`User`, :class:`Member`]]
        The user or member that sent the interaction.
    locale: :class:`str`
        The selected language of the interaction's author.

        .. versionadded:: 2.4
    guild: Optional[:class:`Guild`]
        The guild the interaction was sent from.
    guild_locale: Optional[:class:`str`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionadded:: 2.4
    channel: Optional[Union[:class:`abc.GuildChannel`, :class:`PartialMessageable`, :class:`Thread`]]
        The channel the interaction was sent from.
    me: Union[:class:`.Member`, :class:`.ClientUser`]
        Similar to :attr:`.Guild.me`
    permissions: :class:`Permissions`
        The resolved permissions of the member in the channel, including overwrites.
    response: :class:`InteractionResponse`
        Returns an object responsible for handling responding to the interaction.
    followup: :class:`Webhook`
        Returns the follow up webhook for follow up interactions.
    token: :class:`str`
        The token to continue the interaction. These are valid
        for 15 minutes.
    data: :class:`ApplicationCommandInteractionData`
        The wrapped interaction data.
    """

    bot: BotBase

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        super().__init__(data=data, state=state)
        self.data = ApplicationCommandInteractionData(
            data=data["data"], state=state, guild=self.guild  # type: ignore
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
    """An ApplicationCommandInteraction Context subclass meant for annotation


    No runtime behavior is changed but annotations are modified
    to seem like the interaction can only ever be invoked in guilds.
    """

    guild: Guild
    me: Member
    guild_locale: str


class UserCommandInteraction(ApplicationCommandInteraction):
    """An ApplicationCommandInteraction Context subclass meant for annotation

    No runtime behavior is changed but annotations are modified
    to seem like the interaction is specifically a user command.
    """

    target: Union[User, Member]


class MessageCommandInteraction(ApplicationCommandInteraction):
    """An ApplicationCommandInteraction Context subclass meant for annotation

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
        guild: Optional[Guild],
    ):
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.type: ApplicationCommandType = try_enum(ApplicationCommandType, data.get("type"))
        self.resolved = ApplicationCommandInteractionDataResolved(
            data=data.get("resolved", {}), state=state, guild=guild
        )
        target_id = data.get("target_id")
        self.target_id: Optional[int] = None if target_id is None else int(target_id)
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
    """
    This class represents the structure of an interaction data option from the API.

    Attributes
    ----------
    name: :class:`str`
        The name of the option.
    type: :class:`OptionType`
        The type of the option.
    value: :class:`Any`
        The value of the option.
    options: List[:class:`ApplicationCommandInteractionDataOption`]
        The list of options of this option. Only exists for subcommands and groups.
    focused: :class:`bool`
        Whether this option is focused by the user. May be ``True`` in
        case of :class:`ApplicationCommandAutocompleteInteraction`.
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
    """Represents the resolved data related to
    an interaction with an application command.

    .. versionadded:: 2.1

    Attributes
    ----------
    members: Dict[:class:`int`, :class:`Member`]
        IDs and partial members (missing ``deaf`` and ``mute``)
    users: Dict[:class:`int`, :class:`User`]
        IDs and users
    roles: Dict[:class:`int`, :class:`Role`]
        IDs and roles
    channels: Dict[:class:`int`, :class:`Channel`]
        IDs and partial channels (only ``id``, ``name`` and ``permissions`` are included,
        threads also have ``thread_metadata`` and ``parent_id``).
    messages: Dict[:class:`int`, :class:`Message`]
        IDs and messages
    """

    __slots__ = ("members", "users", "roles", "channels", "messages")

    def __init__(
        self,
        *,
        data: ApplicationCommandInteractionDataResolvedPayload,
        state: ConnectionState,
        guild: Optional[Guild],
    ):
        data = data or {}

        self.members: Dict[int, Member] = {}
        self.users: Dict[int, User] = {}
        self.roles: Dict[int, Role] = {}
        self.channels: Dict[int, InteractionChannel] = {}
        self.messages: Dict[int, Message] = {}

        users = data.get("users", {})
        members = data.get("members", {})
        roles = data.get("roles", {})
        channels = data.get("channels", {})
        messages = data.get("messages", {})

        for str_id, user in users.items():
            user_id = int(str_id)
            member = members.get(str_id)
            if member is not None:
                self.members[user_id] = (
                    guild
                    and guild.get_member(user_id)
                    or Member(
                        data={**member, "user": user},  # type: ignore
                        guild=guild,  # type: ignore
                        state=state,
                    )
                )
            else:
                self.users[user_id] = User(state=state, data=user)

        for str_id, role in roles.items():
            self.roles[int(str_id)] = Role(guild=guild, state=state, data=role)  # type: ignore

        for str_id, channel in channels.items():
            factory, ch_type = _threaded_channel_factory(channel["type"])
            if factory:
                channel["position"] = 0  # type: ignore
                self.channels[int(str_id)] = (  # type: ignore
                    guild
                    and guild.get_channel(int(str_id))
                    or factory(guild=guild, state=state, data=channel)  # type: ignore
                )

        for str_id, message in messages.items():
            channel_id = int(message["channel_id"])
            channel = guild.get_channel(channel_id) if guild else None
            if channel is None:
                channel = state.get_channel(channel_id)
            self.messages[int(str_id)] = Message(state=state, channel=channel, data=message)  # type: ignore

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


# People asked about shorter aliases, let's see which one catches on the most
CommandInteraction = ApplicationCommandInteraction
CmdInteraction = ApplicationCommandInteraction
CommandInter = ApplicationCommandInteraction
CmdInter = ApplicationCommandInteraction
AppCommandInteraction = ApplicationCommandInteraction
AppCommandInter = ApplicationCommandInteraction
AppCmdInter = ApplicationCommandInteraction
