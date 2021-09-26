from __future__ import annotations
from abc import ABC
from typing import (
    Any,
    Callable,
    List,
    Optional,
    TypeVar,
    TYPE_CHECKING
)
import asyncio
import datetime

from disnake.app_commands import ApplicationCommand
from disnake.enums import ApplicationCommandType
from disnake.utils import async_all

from .cooldowns import BucketType, CooldownMapping, MaxConcurrency
from .errors import *

if TYPE_CHECKING:
    from typing_extensions import ParamSpec
    from disnake.interactions import ApplicationCommandInteraction
    from ._types import Check, Hook, Error
    from .cog import Cog


__all__ = ('InvokableApplicationCommand',)


T = TypeVar('T')
AppCommandT = TypeVar('AppCommandT', bound='InvokableApplicationCommand')
CogT = TypeVar('CogT', bound='Cog')
HookT = TypeVar('HookT', bound='Hook')
ErrorT = TypeVar('ErrorT', bound='Error')

if TYPE_CHECKING:
    P = ParamSpec('P')
else:
    P = TypeVar('P')


def _get_overridden_method(method):
    return getattr(method.__func__, '__cog_special_method__', method)


class InvokableApplicationCommand(ABC):
    """A base class that implements the protocol for a bot application command.

    These are not created manually, instead they are created via the
    decorator or functional interface.
    """
    body: ApplicationCommand

    def __init__(self, func, *, name: str = None, **kwargs):
        self.__command_flag__ = None
        self._callback: Callable[..., Any] = func
        self.name: str = name or func.__name__
        self.qualified_name: str = self.name
        if not isinstance(self.name, str):
            raise TypeError('Name of a command must be a string.')

        try:
            checks = func.__commands_checks__
            checks.reverse()
        except AttributeError:
            checks = kwargs.get('checks', [])

        self.checks: List[Check] = checks

        try:
            cooldown = func.__commands_cooldown__
        except AttributeError:
            cooldown = kwargs.get('cooldown')
        
        # TODO: Figure out how cooldowns even work with interactions
        if cooldown is None:
            buckets = CooldownMapping(cooldown, BucketType.default)
        elif isinstance(cooldown, CooldownMapping):
            buckets = cooldown
        else:
            raise TypeError("Cooldown must be a an instance of CooldownMapping or None.")
        self._buckets: CooldownMapping = buckets

        try:
            max_concurrency = func.__commands_max_concurrency__
        except AttributeError:
            max_concurrency = kwargs.get('max_concurrency')
        self._max_concurrency: Optional[MaxConcurrency] = max_concurrency

        self.cog: Optional[Cog] = None
        self.guild_ids: Optional[List[int]] = None
        self.auto_sync: bool = True

        self._before_invoke: Optional[Hook] = None
        self._after_invoke: Optional[Hook] = None
    
    @property
    def callback(self) -> Callable[..., Any]:
        return self._callback

    def add_check(self, func: Check) -> None:
        """Adds a check to the application command.

        This is the non-decorator interface to :func:`.check`.

        Parameters
        -----------
        func
            The function that will be used as a check.
        """

        self.checks.append(func)

    def remove_check(self, func: Check) -> None:
        """Removes a check from the application command.

        This function is idempotent and will not raise an exception
        if the function is not in the command's checks.

        Parameters
        -----------
        func
            The function to remove from the checks.
        """

        try:
            self.checks.remove(func)
        except ValueError:
            pass

    async def __call__(self, interaction: ApplicationCommandInteraction, *args, **kwargs) -> Any:
        """|coro|

        Calls the internal callback that the application command holds.

        .. note::

            This bypasses all mechanisms -- including checks, converters,
            invoke hooks, cooldowns, etc. You must take care to pass
            the proper arguments and types to this function.

        """
        if self.cog is not None:
            return await self.callback(self.cog, interaction, *args, **kwargs)
        else:
            return await self.callback(interaction, *args, **kwargs)

    def _prepare_cooldowns(self, inter: ApplicationCommandInteraction) -> None:
        if self._buckets.valid:
            dt = inter.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(inter, current) # type: ignore
            if bucket is not None:
                retry_after = bucket.update_rate_limit(current)
                if retry_after:
                    raise CommandOnCooldown(bucket, retry_after, self._buckets.type)  # type: ignore

    async def prepare(self, inter: ApplicationCommandInteraction) -> None:
        inter.application_command = self
        
        if not await self.can_run(inter):
            raise CheckFailure(f'The check functions for command {self.qualified_name!r} failed.')

        if self._max_concurrency is not None:
            await self._max_concurrency.acquire(inter)  # type: ignore

        try:
            self._prepare_cooldowns(inter)
            await self.call_before_hooks(inter) # type: ignore
        except:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter)  # type: ignore
            raise
    
    def is_on_cooldown(self, inter: ApplicationCommandInteraction) -> bool:
        """Checks whether the application command is currently on cooldown.

        Parameters
        -----------
        inter: :class:`.ApplicationCommandInteraction`
            The interaction with the application command currently being invoked.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the application command is on cooldown.
        """
        if not self._buckets.valid:
            return False

        bucket = self._buckets.get_bucket(inter) # type: ignore
        dt = inter.created_at
        current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        return bucket.get_tokens(current) == 0

    def reset_cooldown(self, inter: ApplicationCommandInteraction) -> None:
        """Resets the cooldown on this application command.

        Parameters
        -----------
        inter: :class:`.ApplicationCommandInteraction`
            The interaction with this application command
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(inter) # type: ignore
            bucket.reset()

    def get_cooldown_retry_after(self, inter: ApplicationCommandInteraction) -> float:
        """Retrieves the amount of seconds before this application command can be tried again.

        Parameters
        -----------
        inter: :class:`.ApplicationCommandInteraction`
            The interaction with this application command.

        Returns
        --------
        :class:`float`
            The amount of time left on this command's cooldown in seconds.
            If this is ``0.0`` then the command isn't on cooldown.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(inter) # type: ignore
            dt = inter.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    async def invoke(self, inter: ApplicationCommandInteraction, *args, **kwargs) -> None:
        """
        This method isn't really usable in this class, but it's usable in subclasses.
        """
        await self.prepare(inter)

        try:
            await self(inter, *args, **kwargs)
        except CommandError:
            inter.command_failed = True
            raise
        except asyncio.CancelledError:
            inter.command_failed = True
            return
        except Exception as exc:
            inter.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter) # type: ignore

            await self.call_after_hooks(inter)

    def error(self, coro: ErrorT) -> ErrorT:
        """A decorator that registers a coroutine as a local error handler.

        A local error handler is an error event limited to a single application command.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the local error handler.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The error handler must be a coroutine.')

        self.on_error: Error = coro
        return coro

    def has_error_handler(self) -> bool:
        """
        Checks whether the application command has an error handler registered.
        """
        return hasattr(self, 'on_error')

    async def _call_local_error_handler(self, inter: ApplicationCommandInteraction, error: CommandError) -> None:
        if not self.has_error_handler():
            return
        # TODO: you shouldn't need to pass in cogs in the first place
        if self.cog is None:
            await self.on_error(inter, error) # type: ignore
        else:
            await self.on_error(self.cog, inter, error) # type: ignore

    async def _call_external_error_handlers(self, inter: ApplicationCommandInteraction, error: CommandError) -> None:
        """Overwritten in subclasses"""
        raise error

    async def dispatch_error(self, inter: ApplicationCommandInteraction, error: CommandError):
        await self._call_local_error_handler(inter, error)
        await self._call_external_error_handlers(inter, error)

    async def call_before_hooks(self, inter: ApplicationCommandInteraction) -> None:
        # now that we're done preparing we can call the pre-command hooks
        # first, call the command local hook:
        cog = self.cog
        if self._before_invoke is not None:
            # should be cog if @commands.before_invoke is used
            instance = getattr(self._before_invoke, '__self__', cog)
            # __self__ only exists for methods, not functions
            # however, if @command.before_invoke is used, it will be a function
            if instance:
                await self._before_invoke(instance, inter)  # type: ignore
            else:
                await self._before_invoke(inter)  # type: ignore

        if inter.data.type is ApplicationCommandType.chat_input:
            partial_attr_name = 'slash_command'
        elif inter.data.type is ApplicationCommandType.user:
            partial_attr_name = 'user_command'
        elif inter.data.type is ApplicationCommandType.message:
            partial_attr_name = 'message_command'
        else:
            return

        # call the cog local hook if applicable:
        if cog is not None:
            meth = getattr(cog, f'cog_before_{partial_attr_name}_invoke', None)
            hook = _get_overridden_method(meth)
            if hook is not None:
                await hook(inter)

        # call the bot global hook if necessary
        hook = getattr(inter.bot, f'_before_{partial_attr_name}_invoke', None)
        if hook is not None:
            await hook(inter)

    async def call_after_hooks(self, inter: ApplicationCommandInteraction) -> None:
        cog = self.cog
        if self._after_invoke is not None:
            instance = getattr(self._after_invoke, '__self__', cog)
            if instance:
                await self._after_invoke(instance, inter)  # type: ignore
            else:
                await self._after_invoke(inter)  # type: ignore

        if inter.data.type is ApplicationCommandType.chat_input:
            partial_attr_name = 'slash_command'
        elif inter.data.type is ApplicationCommandType.user:
            partial_attr_name = 'user_command'
        elif inter.data.type is ApplicationCommandType.message:
            partial_attr_name = 'message_command'
        else:
            return

        # call the cog local hook if applicable:
        if cog is not None:
            meth = getattr(cog, f'cog_after_{partial_attr_name}_invoke', None)
            hook = _get_overridden_method(meth)
            if hook is not None:
                await hook(inter)

        # call the bot global hook if necessary
        hook = getattr(inter.bot, f'_after_{partial_attr_name}_invoke', None)
        if hook is not None:
            await hook(inter)

    def before_invoke(self, coro: HookT) -> HookT:
        """A decorator that registers a coroutine as a pre-invoke hook.

        A pre-invoke hook is called directly before the command is called.

        This pre-invoke hook takes a sole parameter, a :class:`.ApplicationCommandInteraction`.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the pre-invoke hook.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_invoke = coro
        return coro

    def after_invoke(self, coro: HookT) -> HookT:
        """A decorator that registers a coroutine as a post-invoke hook.

        A post-invoke hook is called directly after the command is called.

        This post-invoke hook takes a sole parameter, a :class:`.ApplicationCommandInteraction`.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the post-invoke hook.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_invoke = coro
        return coro

    @property
    def cog_name(self) -> Optional[str]:
        """Optional[:class:`str`]: The name of the cog this application command belongs to, if any."""
        return type(self.cog).__cog_name__ if self.cog is not None else None

    async def can_run(self, inter: ApplicationCommandInteraction) -> bool:
        """|coro|

        Checks if the command can be executed by checking all the predicates
        inside the :attr:`~Command.checks` attribute.

        Parameters
        -----------
        inter: :class:`.ApplicationCommandInteraction`
            The interaction with the application command currently being invoked.

        Raises
        -------
        :class:`CommandError`
            Any application command error that was raised during a check call will be propagated
            by this function.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the application command can be invoked.
        """

        original = inter.application_command
        inter.application_command = self

        try:
            # TODO: cog checks for application commands

            predicates = self.checks
            if not predicates:
                # since we have no checks, then we just return True.
                return True
            
            return await async_all(predicate(inter) for predicate in predicates)  # type: ignore
        finally:
            inter.application_command = original
