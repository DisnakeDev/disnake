# SPDX-License-Identifier: MIT

import pytest

import disnake
from disnake import Permissions
from disnake.ext import commands


class TestDefaultPermissions:
    def test_decorator(self) -> None:
        class Cog(commands.Cog):
            @commands.slash_command(default_member_permissions=64)
            async def cmd(self, _) -> None:
                ...

            @commands.default_member_permissions(64)
            @commands.slash_command()
            async def above(self, _) -> None:
                ...

            @commands.slash_command()
            @commands.default_member_permissions(64)
            async def below(self, _) -> None:
                ...

        for c in (Cog, Cog()):
            assert c.cmd.default_member_permissions == Permissions(64)
            assert c.above.default_member_permissions == Permissions(64)
            assert c.below.default_member_permissions == Permissions(64)

    def test_decorator_overwrite(self) -> None:
        # putting the decorator above should fail
        with pytest.raises(ValueError, match="Cannot set `default_member_permissions`"):

            class Cog(commands.Cog):
                @commands.default_member_permissions(32)
                @commands.slash_command(default_member_permissions=64)
                async def above(self, _) -> None:
                    ...

        # putting the decorator below shouldn't fail
        # (this is a side effect of how command copying works,
        # and while this *should* probably fail, we're just testing
        # for regressions for now)
        class Cog2(commands.Cog):
            @commands.slash_command(default_member_permissions=64)
            @commands.default_member_permissions(32)
            async def below(self, _) -> None:
                ...

        for c in (Cog2, Cog2()):
            assert c.below.default_member_permissions == Permissions(32)

    def test_attrs(self) -> None:
        class Cog(commands.Cog, slash_command_attrs={"default_member_permissions": 32}):
            @commands.slash_command()
            async def no_overwrite(self, _) -> None:
                ...

            @commands.slash_command(default_member_permissions=64)
            async def overwrite(self, _) -> None:
                ...

            @commands.default_member_permissions(64)
            @commands.slash_command()
            async def overwrite_decorator_above(self, _) -> None:
                ...

            @commands.slash_command()
            @commands.default_member_permissions(64)
            async def overwrite_decorator_below(self, _) -> None:
                ...

        assert Cog.no_overwrite.default_member_permissions is None
        assert Cog().no_overwrite.default_member_permissions == Permissions(32)

        assert Cog.overwrite.default_member_permissions == Permissions(64)
        assert Cog().overwrite.default_member_permissions == Permissions(64)

        assert Cog.overwrite_decorator_above.default_member_permissions == Permissions(64)
        assert Cog().overwrite_decorator_above.default_member_permissions == Permissions(64)

        assert Cog.overwrite_decorator_below.default_member_permissions == Permissions(64)
        assert Cog().overwrite_decorator_below.default_member_permissions == Permissions(64)


def test_localization_copy() -> None:
    class Cog(commands.Cog):
        @commands.slash_command()
        async def cmd(
            self,
            inter,
            param: int = commands.Param(name=disnake.Localized("param", key="PARAM")),
        ) -> None:
            ...

    # Ensure the command copy that happens on cog init doesn't raise a LocalizationWarning for the options.
    cog = Cog()

    with pytest.warns(disnake.LocalizationWarning):
        assert cog.get_slash_commands()[0].options[0].name_localizations.data is None
