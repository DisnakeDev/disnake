# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Any, Callable, Coroutine, TypeVar, Union

if TYPE_CHECKING:
    from .cog import Cog
    from .context import Context
    from .errors import CommandError

T = TypeVar("T")
test = TypeVar("test", bound=Cog)

Coro = Coroutine[Any, Any, T]
MaybeCoro = Union[T, Coro[T]]
CoroFunc = Callable[..., Coro[Any]]

Check = Union[
    Callable[["Cog"], test],
    Callable[["Context[Any]"], MaybeCoro[bool]],
]
Hook = Union[Callable[["Cog", "Context[Any]"], Coro[Any]], Callable[["Context[Any]"], Coro[Any]]]
Error = Union[
    Callable[["Cog", "Context[Any]", "CommandError"], Coro[Any]],
    Callable[["Context[Any]", "CommandError"], Coro[Any]],
]


# This is merely a tag type to avoid circular import issues.
# Yes, this is a terrible solution but ultimately it is the only solution.
class _BaseCommand:
    __slots__ = ()
