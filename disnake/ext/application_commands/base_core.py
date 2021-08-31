from __future__ import annotations
from typing import (
    List,
    Optional,
    TypeVar,
    TYPE_CHECKING
)
import asyncio
import datetime

from discord.utils import async_all

from ..commands.errors import *
from ..commands.cooldowns import BucketType, CooldownMapping, MaxConcurrency


if TYPE_CHECKING:
    from typing_extensions import ParamSpec
    from discord.interactions import ApplicationCommandInteraction
    from ..commands._types import Check, Hook, Error


__all__ = ('InvokableApplicationCommand',)


T = TypeVar('T')
AppCommandT = TypeVar('AppCommandT', bound='InvokableApplicationCommand')
CogT = TypeVar('CogT')
HookT = TypeVar('HookT', bound='Hook')
ErrorT = TypeVar('ErrorT', bound='Error')

if TYPE_CHECKING:
    P = ParamSpec('P')
else:
    P = TypeVar('P')


class InvokableApplicationCommand:
    """A base class that implements the protocol for a bot application command.

    These are not created manually, instead they are created via the
    decorator or functional interface.
    """

    def __init__(self, func, *, name: str = None, **kwargs):
        self._callback = func
        self.name: str = name or func.__name__
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

        self.cog: Optional[CogT] = None
        self.guild_ids: List[int] = None
        self.auto_sync: bool = True
    
    @property
    def callback(self):
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

    async def __call__(self, interaction: ApplicationCommandInteraction, *args, **kwargs) -> T:
        """|coro|

        Calls the internal callback that the application command holds.

        .. note::

            This bypasses all mechanisms -- including checks, converters,
            invoke hooks, cooldowns, etc. You must take care to pass
            the proper arguments and types to this function.

        """
        if self.cog is not None:
            return await self.callback(self.cog, interaction, *args, **kwargs)  # type: ignore
        else:
            return await self.callback(interaction, *args, **kwargs)  # type: ignore

    def _prepare_cooldowns(self, inter: ApplicationCommandInteraction) -> None:
        if self._buckets.valid:
            dt = inter.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(inter, current)
            if bucket is not None:
                retry_after = bucket.update_rate_limit(current)
                if retry_after:
                    raise CommandOnCooldown(bucket, retry_after, self._buckets.type)  # type: ignore

    async def prepare(self, inter: ApplicationCommandInteraction) -> None:
        inter.application_command = self

        if not await self.can_run(inter):
            raise CheckFailure(f'The check functions for command {self.qualified_name} failed.')

        if self._max_concurrency is not None:
            await self._max_concurrency.acquire(inter)  # type: ignore

        try:
            self._prepare_cooldowns(inter)
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

        bucket = self._buckets.get_bucket(inter)
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
            bucket = self._buckets.get_bucket(inter)
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
            bucket = self._buckets.get_bucket(inter)
            dt = inter.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    async def invoke(self, inter: ApplicationCommandInteraction) -> None:
        """
        This method isn't really usable in this class, but it's usable in subclasses.
        """
        await self.prepare(inter)
        try:
            await self(inter)
        except Exception as exc:
            inter.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(inter)

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

    def dispatch_error(self, inter: ApplicationCommandInteraction, error: CommandError):
        if not self.has_error_handler():
            return
        if self.cog is None:
            args = (inter, error)
        else:
            args = (self.cog, inter, error)
        asyncio.create_task(self.on_error(*args), name=f'discord-ext-app-command-error-{inter.id}')

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
            # TODO: add Interaction.bot attribute
            # if not await inter.bot.can_run(inter):
            #     raise CheckFailure(f'The global check functions for application command {self.qualified_name} failed.')

            # TODO: cog checks for application commands
            # cog = self.cog
            # if cog is not None:
            #     local_check = Cog._get_overridden_method(cog.cog_check)
            #     if local_check is not None:
            #         ret = await maybe_coroutine(local_check, inter)
            #         if not ret:
            #             return False

            predicates = self.checks
            if not predicates:
                # since we have no checks, then we just return True.
                return True

            return await async_all(predicate(ctx) for predicate in predicates)  # type: ignore
        finally:
            inter.application_command = original
