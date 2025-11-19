# SPDX-License-Identifier: MIT

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

if TYPE_CHECKING:
    from disnake import ApplicationCommandInteraction

    from .cog import Cog
    from .context import Context
    from .errors import CommandError

T = TypeVar("T")

FuncT = TypeVar("FuncT", bound=Callable[..., Any])

Coro: TypeAlias = Coroutine[Any, Any, T]
MaybeCoro: TypeAlias = T | Coro[T]
CoroFunc: TypeAlias = Callable[..., Coro[Any]]

Check: TypeAlias = (
    Callable[["Cog", "Context[Any]"], MaybeCoro[bool]] | Callable[["Context[Any]"], MaybeCoro[bool]]
)
AppCheck: TypeAlias = (
    Callable[["Cog", "ApplicationCommandInteraction"], MaybeCoro[bool]]
    | Callable[["ApplicationCommandInteraction"], MaybeCoro[bool]]
)
Hook: TypeAlias = (
    Callable[["Cog", "Context[Any]"], Coro[Any]] | Callable[["Context[Any]"], Coro[Any]]
)
Error: TypeAlias = (
    Callable[["Cog", "Context[Any]", "CommandError"], Coro[Any]]
    | Callable[["Context[Any]", "CommandError"], Coro[Any]]
)


# This is merely a tag type to avoid circular import issues.
# Yes, this is a terrible solution but ultimately it is the only solution.
class _BaseCommand:
    __slots__ = ()
