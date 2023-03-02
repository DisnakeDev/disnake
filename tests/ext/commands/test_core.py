# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING

from disnake.ext import commands
from tests.helpers import reveal_type

if TYPE_CHECKING:
    from typing_extensions import assert_type

    # NOTE: using undocumented `expected_text` parameter of pyright instead of `assert_type`,
    # as `assert_type` can't handle bound ParamSpecs
    reveal_type(
        42,  # type: ignore
        expected_text="str",  # type: ignore
    )


class CustomContext(commands.Context):
    ...


class CustomCog(commands.Cog):
    ...


class TestDecorators:
    def _test_typing_defaults(self) -> None:
        base = commands.GroupMixin[None]()

        # no cog

        async def f1(ctx: CustomContext, a: int, b: str) -> bool:
            ...

        for cd in (commands.command(), base.command()):
            reveal_type(
                cd(f1),  # type: ignore
                expected_text="Command[None, (a: int, b: str), bool]",
            )

        for gd in (commands.group(), base.group()):
            reveal_type(
                gd(f1),  # type: ignore
                expected_text="Group[None, (a: int, b: str), bool]",
            )

        # custom cog
        base = commands.GroupMixin[CustomCog]()

        async def f2(_self: CustomCog, ctx: CustomContext, a: int, b: str) -> bool:
            ...

        for cd in (commands.command(), base.command()):
            reveal_type(
                cd(f2),  # type: ignore
                expected_text="Command[CustomCog, (a: int, b: str), bool]",
            )

        for gd in (commands.group(), base.group()):
            reveal_type(
                gd(f2),  # type: ignore
                expected_text="Group[CustomCog, (a: int, b: str), bool]",
            )

    def _test_typing_cls(self) -> None:
        class CustomCommand(commands.Command):
            ...

        class CustomGroup(commands.Group):
            ...

        base = commands.GroupMixin[None]()

        command_decorators = (commands.command(cls=CustomCommand), base.command(cls=CustomCommand))
        group_decorators = (commands.group(cls=CustomGroup), base.group(cls=CustomGroup))

        async def f(ctx: CustomContext, a: int, b: str) -> bool:
            ...

        for cd in command_decorators:
            assert_type(cd(f), CustomCommand)

        for gd in group_decorators:
            assert_type(gd(f), CustomGroup)
