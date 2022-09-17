import datetime
from typing import Any
import pytest

from disnake.ext import commands

from disnake.ext.tasks import Coro, CoroP, Loop, loop


class TestLoops:
    def test_decorator(self):
        class Cog(commands.Cog):
            @loop(seconds=30, minutes=0, hours=0)
            async def task(self) -> None:
                ...

        for c in (Cog, Cog()):
            assert c.task.seconds == 30

        with pytest.raises(TypeError, match="must be a coroutine"):
            @loop()  # type: ignore
            def task() -> None:
                ...

    def test_mixing_time(self):
        with pytest.raises(TypeError):

            async def callback():
                pass

            Loop(callback, seconds=30, time=datetime.time())

        with pytest.raises(TypeError):

            class Cog(commands.Cog):
                @loop(seconds=30, time=datetime.time())
                async def task(self) -> None:
                    ...

    def test_inheritance(self):
        class HyperLoop(Loop[CoroP]):
            def __init__(self, coro: Coro[CoroP], time_tup: tuple[float, float, float]) -> None:
                super().__init__(coro, *time_tup)

            def clone(self):
                instance = type(self)(self.coro, (self._seconds, self._minutes, self._hours))
                instance._time = self._time
                instance.count = self.count
                instance.reconnect = self.reconnect
                instance.loop = self.loop
                instance._before_loop = self._before_loop
                instance._after_loop = self._after_loop
                instance._error = self._error
                instance._injected = self._injected
                return instance

        class WhileTrueLoop:
            def __init__(self, coro: Coro[CoroP]) -> None:
                ...

        async def callback():
            pass

        HyperLoop(callback, (1, 2, 3))

        class Cog(commands.Cog):
            @loop(cls=HyperLoop[Any], time_tup=(1, 2, 3))
            async def task(self) -> None:
                ...

        for c in (Cog, Cog()):
            assert (c.task.seconds, c.task.minutes, c.task.hours) == (1, 2, 3)

        with pytest.raises(TypeError, match="subclass of Loop"):
            @loop(cls=WhileTrueLoop)  # type: ignore
            async def task() -> None:
                ...
