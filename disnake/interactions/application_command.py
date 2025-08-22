# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple, Union

from .. import utils
from ..enums import ApplicationCommandType, Locale, OptionType, try_enum
from ..guild import Guild
from ..member import Member
from ..message import Message
from ..user import User
from .base import ClientT, Interaction, InteractionDataResolved

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
    from ..ext.commands import InvokableApplicationCommand
    from ..state import ConnectionState
    from ..types.interactions import (
        ApplicationCommandInteraction as ApplicationCommandInteractionPayload,
        ApplicationCommandInteractionData as ApplicationCommandInteractionDataPayload,
    )


class ApplicationCommandInteraction(Interaction[ClientT]):
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
    channel: Union[:class:`abc.GuildChannel`, :class:`Thread`, :class:`abc.PrivateChannel`, :class:`PartialMessageable`]
        The channel the interaction was sent from.

        Note that due to a Discord limitation, DM channels
        may not contain recipient information.
        Unknown channel types will be :class:`PartialMessageable`.

        .. versionchanged:: 2.10
            If the interaction was sent from a thread and the bot cannot normally access the thread,
            this is now a proper :class:`Thread` object.
            Private channels are now proper :class:`DMChannel`/:class:`GroupChannel`
            objects instead of :class:`PartialMessageable`.

        .. note::
            If you want to compute the interaction author's or bot's permissions in the channel,
            consider using :attr:`permissions` or :attr:`app_permissions`.

    author: Union[:class:`User`, :class:`Member`]
        The user or member that sent the interaction.

        .. note::
            In scenarios where an interaction occurs in a guild but :attr:`.guild` is unavailable,
            such as with user-installed applications in guilds, some attributes of :class:`Member`\\s
            that depend on the guild/role cache will not work due to an API limitation.
            This includes :attr:`~Member.roles`, :attr:`~Member.top_role`, :attr:`~Member.role_icon`,
            and :attr:`~Member.guild_permissions`.
    locale: :class:`Locale`
        The selected language of the interaction's author.

        .. versionadded:: 2.4

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    guild_locale: Optional[:class:`Locale`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionadded:: 2.4

        .. versionchanged:: 2.5
            Changed to :class:`Locale` instead of :class:`str`.

    token: :class:`str`
        The token to continue the interaction. These are valid for 15 minutes.
    client: :class:`Client`
        The interaction client.
    entitlements: List[:class:`Entitlement`]
        The entitlements for the invoking user and guild,
        representing access to an application subscription.

        .. versionadded:: 2.10

    authorizing_integration_owners: :class:`AuthorizingIntegrationOwners`
        Details about the authorizing user/guild for the application installation
        related to the interaction.

        .. versionadded:: 2.10

    context: :class:`InteractionContextTypes`
        The context where the interaction was triggered from.

        This is a flag object, with exactly one of the flags set to ``True``.
        To check whether an interaction originated from e.g. a :attr:`~InteractionContextTypes.guild`
        context, you can use ``if interaction.context.guild:``.

        .. versionadded:: 2.10

    data: :class:`ApplicationCommandInteractionData`
        The wrapped interaction data.
    application_command: :class:`.InvokableApplicationCommand`
        The command invoked by the interaction.
    command_failed: :class:`bool`
        Whether the command failed to be checked or invoked.
    """

    def __init__(
        self, *, data: ApplicationCommandInteractionPayload, state: ConnectionState
    ) -> None:
        super().__init__(data=data, state=state)
        self.data: ApplicationCommandInteractionData = ApplicationCommandInteractionData(
            data=data["data"], parent=self
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


# TODO(3.0): consider making these classes @type_check_only and not affect runtime behavior, or even remove entirely
class GuildCommandInteraction(ApplicationCommandInteraction[ClientT]):
    """An :class:`ApplicationCommandInteraction` subclass, primarily meant for annotations.

    This restricts the command to only be usable in guilds and only as a guild-installed command,
    by automatically setting :attr:`ApplicationCommand.contexts` to :attr:`~InteractionContextTypes.guild` only
    and :attr:`ApplicationCommand.install_types` to :attr:`~ApplicationInstallTypes.guild` only.
    Note that this does not apply to slash subcommands, subcommand groups, or autocomplete callbacks.

    Additionally, the type annotations of :attr:`~Interaction.author`, :attr:`~Interaction.guild`,
    :attr:`~Interaction.guild_id`, :attr:`~Interaction.guild_locale`, and :attr:`~Interaction.me`
    are modified to match the expected types in guilds.
    """

    author: Member
    guild: Guild
    guild_id: int
    guild_locale: Locale
    me: Member


class UserCommandInteraction(ApplicationCommandInteraction[ClientT]):
    """An :class:`ApplicationCommandInteraction` subclass meant for annotations
    in user context menu commands.

    No runtime behavior is changed, but the type annotations of :attr:`~ApplicationCommandInteraction.target`
    are modified to match the expected type with user commands.
    """

    target: Union[User, Member]


class MessageCommandInteraction(ApplicationCommandInteraction[ClientT]):
    """An :class:`ApplicationCommandInteraction` subclass meant for annotations
    in message context menu commands.

    No runtime behavior is changed, but the type annotations of :attr:`~ApplicationCommandInteraction.target`
    are modified to match the expected type with message commands.
    """

    target: Message


class ApplicationCommandInteractionData(Dict[str, Any]):
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
    resolved: :class:`InteractionDataResolved`
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
        parent: ApplicationCommandInteraction[ClientT],
    ) -> None:
        super().__init__(data)
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.type: ApplicationCommandType = try_enum(ApplicationCommandType, data["type"])

        self.resolved = InteractionDataResolved(data=data.get("resolved", {}), parent=parent)
        self.target_id: Optional[int] = utils._get_as_snowflake(data, "target_id")
        target = self.resolved.get_by_id(self.target_id)
        self.target: Optional[Union[User, Member, Message]] = target  # type: ignore

        self.options: List[ApplicationCommandInteractionDataOption] = [
            ApplicationCommandInteractionDataOption(data=d, resolved=self.resolved)
            for d in data.get("options", [])
        ]

    def __repr__(self) -> str:
        return (
            f"<ApplicationCommandInteractionData id={self.id!r} name={self.name!r} type={self.type!r} "
            f"target_id={self.target_id!r} target={self.target!r} resolved={self.resolved!r} options={self.options!r}>"
        )

    def _get_chain_and_kwargs(
        self, chain: Optional[Tuple[str, ...]] = None
    ) -> Tuple[Tuple[str, ...], Dict[str, Any]]:
        """Returns a chain of sub-command names and a dict of filled options."""
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


class ApplicationCommandInteractionDataOption(Dict[str, Any]):
    """Represents the structure of an interaction data option from the API.

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

    def __init__(self, *, data: Mapping[str, Any], resolved: InteractionDataResolved) -> None:
        super().__init__(data)
        self.name: str = data["name"]
        self.type: OptionType = try_enum(OptionType, data["type"])

        self.value: Any = None
        if (value := data.get("value")) is not None:
            self.value: Any = resolved.get_with_type(value, self.type, value)

        self.options: List[ApplicationCommandInteractionDataOption] = [
            ApplicationCommandInteractionDataOption(data=d, resolved=resolved)
            for d in data.get("options", [])
        ]
        self.focused: bool = data.get("focused", False)

    def __repr__(self) -> str:
        return (
            f"<ApplicationCommandInteractionDataOption name={self.name!r} type={self.type!r}>"
            f"value={self.value!r} focused={self.focused!r} options={self.options!r}>"
        )

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
        self, chain: Optional[Tuple[str, ...]] = None
    ) -> Tuple[Tuple[str, ...], Dict[str, Any]]:
        if chain is None:
            chain = ()
        for option in self.options:
            if option.value is None:
                # Extend the chain and collect kwargs in the nesting
                return option._get_chain_and_kwargs(chain + (option.name,))
            return chain, {o.name: o.value for o in self.options}
        return chain, {}


# backwards compatibility
ApplicationCommandInteractionDataResolved = InteractionDataResolved


# People asked about shorter aliases, let's see which one catches on the most
CommandInteraction = ApplicationCommandInteraction
CmdInteraction = ApplicationCommandInteraction
CommandInter = ApplicationCommandInteraction
CmdInter = ApplicationCommandInteraction
AppCommandInteraction = ApplicationCommandInteraction
AppCommandInter = ApplicationCommandInteraction
AppCmdInter = ApplicationCommandInteraction
