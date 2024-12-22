# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence, Tuple, Union

from disnake.app_commands import MessageCommand, UserCommand
from disnake.flags import ApplicationInstallTypes, InteractionContextTypes
from disnake.i18n import Localized
from disnake.permissions import Permissions

from .base_core import InvokableApplicationCommand, _get_overridden_method
from .errors import CommandError
from .params import safe_call

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from disnake.i18n import LocalizedOptional
    from disnake.interactions import (
        ApplicationCommandInteraction,
        MessageCommandInteraction,
        UserCommandInteraction,
    )

    from .base_core import CogT, InteractionCommandCallback

    P = ParamSpec("P")

__all__ = ("InvokableUserCommand", "InvokableMessageCommand", "user_command", "message_command")


class InvokableUserCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot user command (context menu).

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    ----------
    name: :class:`str`
        The name of the user command.
    qualified_name: :class:`str`
        The full command name, equivalent to :attr:`.name` for this type of command.
    body: :class:`.UserCommand`
        An object being registered in the API.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the user command is called.
    cog: Optional[:class:`Cog`]
        The cog that this user command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_user_command_error`
        event.
    guild_ids: Optional[Tuple[:class:`int`, ...]]
        The list of IDs of the guilds where the command is synced. ``None`` if this command is global.
    auto_sync: :class:`bool`
        Whether to automatically register the command.
    extras: Dict[:class:`str`, Any]
        A dict of user provided extras to attach to the command.

        .. note::
            This object may be copied by the library.

        .. versionadded:: 2.5
    """

    def __init__(
        self,
        func: InteractionCommandCallback[CogT, UserCommandInteraction, P],
        *,
        name: LocalizedOptional = None,
        dm_permission: Optional[bool] = None,  # deprecated
        default_member_permissions: Optional[Union[Permissions, int]] = None,
        nsfw: Optional[bool] = None,
        install_types: Optional[ApplicationInstallTypes] = None,
        contexts: Optional[InteractionContextTypes] = None,
        guild_ids: Optional[Sequence[int]] = None,
        auto_sync: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        name_loc = Localized._cast(name, False)
        super().__init__(func, name=name_loc.string, **kwargs)
        self.guild_ids: Optional[Tuple[int, ...]] = None if guild_ids is None else tuple(guild_ids)
        self.auto_sync: bool = True if auto_sync is None else auto_sync

        try:
            default_member_permissions = func.__default_member_permissions__
        except AttributeError:
            pass
        try:
            install_types = func.__install_types__
        except AttributeError:
            pass
        try:
            contexts = func.__contexts__
        except AttributeError:
            pass

        self.body = UserCommand(
            name=name_loc._upgrade(self.name),
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
            nsfw=nsfw,
            install_types=install_types,
            contexts=contexts,
        )

        self._apply_guild_only()

    async def _call_external_error_handlers(
        self, inter: ApplicationCommandInteraction, error: CommandError
    ) -> None:
        stop_propagation = False
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_user_command_error)
                if local is not None:
                    stop_propagation = await local(inter, error)
                    # User has an option to cancel the global error handler by returning True
        finally:
            if stop_propagation:
                return  # noqa: B012
            inter.bot.dispatch("user_command_error", inter, error)

    async def __call__(
        self,
        interaction: ApplicationCommandInteraction,
        target: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # the target may just not be passed in
        args = (target or interaction.target,) + args
        if self.cog is not None:
            await safe_call(self.callback, self.cog, interaction, *args, **kwargs)
        else:
            await safe_call(self.callback, interaction, *args, **kwargs)


class InvokableMessageCommand(InvokableApplicationCommand):
    """A class that implements the protocol for a bot message command (context menu).

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    ----------
    name: :class:`str`
        The name of the message command.
    qualified_name: :class:`str`
        The full command name, equivalent to :attr:`.name` for this type of command.
    body: :class:`.MessageCommand`
        An object being registered in the API.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the message command is called.
    cog: Optional[:class:`Cog`]
        The cog that this message command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationCommandInteraction`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationCommandInteraction` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_message_command_error`
        event.
    guild_ids: Optional[Tuple[:class:`int`, ...]]
        The list of IDs of the guilds where the command is synced. ``None`` if this command is global.
    auto_sync: :class:`bool`
        Whether to automatically register the command.
    extras: Dict[:class:`str`, Any]
        A dict of user provided extras to attach to the command.

        .. note::
            This object may be copied by the library.

        .. versionadded:: 2.5
    """

    def __init__(
        self,
        func: InteractionCommandCallback[CogT, MessageCommandInteraction, P],
        *,
        name: LocalizedOptional = None,
        dm_permission: Optional[bool] = None,  # deprecated
        default_member_permissions: Optional[Union[Permissions, int]] = None,
        nsfw: Optional[bool] = None,
        install_types: Optional[ApplicationInstallTypes] = None,
        contexts: Optional[InteractionContextTypes] = None,
        guild_ids: Optional[Sequence[int]] = None,
        auto_sync: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        name_loc = Localized._cast(name, False)
        super().__init__(func, name=name_loc.string, **kwargs)
        self.guild_ids: Optional[Tuple[int, ...]] = None if guild_ids is None else tuple(guild_ids)
        self.auto_sync: bool = True if auto_sync is None else auto_sync

        try:
            default_member_permissions = func.__default_member_permissions__
        except AttributeError:
            pass
        try:
            install_types = func.__install_types__
        except AttributeError:
            pass
        try:
            contexts = func.__contexts__
        except AttributeError:
            pass

        self.body = MessageCommand(
            name=name_loc._upgrade(self.name),
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
            nsfw=nsfw,
            install_types=install_types,
            contexts=contexts,
        )

        self._apply_guild_only()

    async def _call_external_error_handlers(
        self, inter: ApplicationCommandInteraction, error: CommandError
    ) -> None:
        stop_propagation = False
        cog = self.cog
        try:
            if cog is not None:
                local = _get_overridden_method(cog.cog_message_command_error)
                if local is not None:
                    stop_propagation = await local(inter, error)
                    # User has an option to cancel the global error handler by returning True
        finally:
            if stop_propagation:
                return  # noqa: B012
            inter.bot.dispatch("message_command_error", inter, error)

    async def __call__(
        self,
        interaction: ApplicationCommandInteraction,
        target: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # the target may just not be passed in
        args = (target or interaction.target,) + args
        if self.cog is not None:
            await safe_call(self.callback, self.cog, interaction, *args, **kwargs)
        else:
            await safe_call(self.callback, interaction, *args, **kwargs)


def user_command(
    *,
    name: LocalizedOptional = None,
    dm_permission: Optional[bool] = None,  # deprecated
    default_member_permissions: Optional[Union[Permissions, int]] = None,
    nsfw: Optional[bool] = None,
    install_types: Optional[ApplicationInstallTypes] = None,
    contexts: Optional[InteractionContextTypes] = None,
    guild_ids: Optional[Sequence[int]] = None,
    auto_sync: Optional[bool] = None,
    extras: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Callable[[InteractionCommandCallback[CogT, UserCommandInteraction, P]], InvokableUserCommand]:
    """A shortcut decorator that builds a user command.

    Parameters
    ----------
    name: Optional[Union[:class:`str`, :class:`.Localized`]]
        The name of the user command (defaults to the function name).

        .. versionchanged:: 2.5
            Added support for localizations.

    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
        Defaults to ``True``.

        .. deprecated:: 2.10
            Use ``contexts`` instead.
            This is equivalent to the :attr:`.InteractionContextTypes.bot_dm` flag.

    default_member_permissions: Optional[Union[:class:`.Permissions`, :class:`int`]]
        The default required permissions for this command.
        See :attr:`.ApplicationCommand.default_member_permissions` for details.

        .. versionadded:: 2.5

    nsfw: :class:`bool`
        Whether this command is :ddocs:`age-restricted <interactions/application-commands#agerestricted-commands>`.
        Defaults to ``False``.

        .. versionadded:: 2.8

    install_types: Optional[:class:`.ApplicationInstallTypes`]
        The installation types where the command is available.
        Defaults to :attr:`.ApplicationInstallTypes.guild` only.
        Only available for global commands.

        See :ref:`app_command_contexts` for details.

        .. versionadded:: 2.10

    contexts: Optional[:class:`.InteractionContextTypes`]
        The interaction contexts where the command can be used.
        Only available for global commands.

        See :ref:`app_command_contexts` for details.

        .. versionadded:: 2.10

    auto_sync: :class:`bool`
        Whether to automatically register the command. Defaults to ``True``.
    guild_ids: Sequence[:class:`int`]
        If specified, the client will register the command in these guilds.
        Otherwise, this command will be registered globally.
    extras: Dict[:class:`str`, Any]
        A dict of user provided extras to attach to the command.

        .. note::
            This object may be copied by the library.

        .. versionadded:: 2.5

    Returns
    -------
    Callable[..., :class:`InvokableUserCommand`]
        A decorator that converts the provided method into an InvokableUserCommand and returns it.
    """

    def decorator(
        func: InteractionCommandCallback[CogT, UserCommandInteraction, P]
    ) -> InvokableUserCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"<{func.__qualname__}> must be a coroutine function")
        if hasattr(func, "__command_flag__"):
            raise TypeError("Callback is already a command.")
        if guild_ids and not all(isinstance(guild_id, int) for guild_id in guild_ids):
            raise ValueError("guild_ids must be a sequence of int.")
        return InvokableUserCommand(
            func,
            name=name,
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
            nsfw=nsfw,
            install_types=install_types,
            contexts=contexts,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            extras=extras,
            **kwargs,
        )

    return decorator


def message_command(
    *,
    name: LocalizedOptional = None,
    dm_permission: Optional[bool] = None,  # deprecated
    default_member_permissions: Optional[Union[Permissions, int]] = None,
    nsfw: Optional[bool] = None,
    install_types: Optional[ApplicationInstallTypes] = None,
    contexts: Optional[InteractionContextTypes] = None,
    guild_ids: Optional[Sequence[int]] = None,
    auto_sync: Optional[bool] = None,
    extras: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Callable[
    [InteractionCommandCallback[CogT, MessageCommandInteraction, P]],
    InvokableMessageCommand,
]:
    """A shortcut decorator that builds a message command.

    Parameters
    ----------
    name: Optional[Union[:class:`str`, :class:`.Localized`]]
        The name of the message command (defaults to the function name).

        .. versionchanged:: 2.5
            Added support for localizations.

    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
        Defaults to ``True``.

        .. deprecated:: 2.10
            Use ``contexts`` instead.
            This is equivalent to the :attr:`.InteractionContextTypes.bot_dm` flag.

    default_member_permissions: Optional[Union[:class:`.Permissions`, :class:`int`]]
        The default required permissions for this command.
        See :attr:`.ApplicationCommand.default_member_permissions` for details.

        .. versionadded:: 2.5

    nsfw: :class:`bool`
        Whether this command is :ddocs:`age-restricted <interactions/application-commands#agerestricted-commands>`.
        Defaults to ``False``.

        .. versionadded:: 2.8

    install_types: Optional[:class:`.ApplicationInstallTypes`]
        The installation types where the command is available.
        Defaults to :attr:`.ApplicationInstallTypes.guild` only.
        Only available for global commands.

        See :ref:`app_command_contexts` for details.

        .. versionadded:: 2.10

    contexts: Optional[:class:`.InteractionContextTypes`]
        The interaction contexts where the command can be used.
        Only available for global commands.

        See :ref:`app_command_contexts` for details.

        .. versionadded:: 2.10

    auto_sync: :class:`bool`
        Whether to automatically register the command. Defaults to ``True``.
    guild_ids: Sequence[:class:`int`]
        If specified, the client will register the command in these guilds.
        Otherwise, this command will be registered globally.
    extras: Dict[:class:`str`, Any]
        A dict of user provided extras to attach to the command.

        .. note::
            This object may be copied by the library.

        .. versionadded:: 2.5

    Returns
    -------
    Callable[..., :class:`InvokableMessageCommand`]
        A decorator that converts the provided method into an InvokableMessageCommand and then returns it.
    """

    def decorator(
        func: InteractionCommandCallback[CogT, MessageCommandInteraction, P]
    ) -> InvokableMessageCommand:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"<{func.__qualname__}> must be a coroutine function")
        if hasattr(func, "__command_flag__"):
            raise TypeError("Callback is already a command.")
        if guild_ids and not all(isinstance(guild_id, int) for guild_id in guild_ids):
            raise ValueError("guild_ids must be a sequence of int.")
        return InvokableMessageCommand(
            func,
            name=name,
            dm_permission=dm_permission,
            default_member_permissions=default_member_permissions,
            nsfw=nsfw,
            install_types=install_types,
            contexts=contexts,
            guild_ids=guild_ids,
            auto_sync=auto_sync,
            extras=extras,
            **kwargs,
        )

    return decorator
