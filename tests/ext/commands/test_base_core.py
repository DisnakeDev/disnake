# SPDX-License-Identifier: MIT

import pytest

import disnake
from disnake import Permissions
from disnake.ext import commands


class DecoratorMeta:
    def __init__(self, type: str) -> None:
        self.decorator = {
            "slash": commands.slash_command,
            "user": commands.user_command,
            "message": commands.message_command,
        }[type]
        self.attr_key = f"{type}_command_attrs"


@pytest.fixture(params=["slash", "user", "message"])
def meta(request):
    return DecoratorMeta(request.param)


class TestDefaultPermissions:
    def test_decorator(self, meta: DecoratorMeta) -> None:
        class Cog(commands.Cog):
            @meta.decorator(default_member_permissions=64)
            async def cmd(self, _) -> None:
                ...

            @commands.default_member_permissions(64)
            @meta.decorator()
            async def above(self, _) -> None:
                ...

            @meta.decorator()
            @commands.default_member_permissions(64)
            async def below(self, _) -> None:
                ...

        for c in (Cog, Cog()):
            assert c.cmd.default_member_permissions == Permissions(64)
            assert c.above.default_member_permissions == Permissions(64)
            assert c.below.default_member_permissions == Permissions(64)

    def test_decorator_overwrite(self, meta: DecoratorMeta) -> None:
        # putting the decorator above should fail
        with pytest.raises(ValueError, match="Cannot set `default_member_permissions`"):

            class Cog(commands.Cog):
                @commands.default_member_permissions(32)
                @meta.decorator(default_member_permissions=64)
                async def above(self, _) -> None:
                    ...

        # putting the decorator below shouldn't fail, for now
        # FIXME: (this is a side effect of how command copying works,
        # and while this *should* probably fail, we're just testing
        # for regressions for now)
        class Cog2(commands.Cog):
            @meta.decorator(default_member_permissions=64)
            @commands.default_member_permissions(32)
            async def below(self, _) -> None:
                ...

        for c in (Cog2, Cog2()):
            assert c.below.default_member_permissions == Permissions(32)

    def test_attrs(self, meta: DecoratorMeta) -> None:
        kwargs = {meta.attr_key: {"default_member_permissions": 32}}

        class Cog(commands.Cog, **kwargs):
            @meta.decorator()
            async def no_overwrite(self, _) -> None:
                ...

            @meta.decorator(default_member_permissions=64)
            async def overwrite(self, _) -> None:
                ...

            @commands.default_member_permissions(64)
            @meta.decorator()
            async def overwrite_decorator_above(self, _) -> None:
                ...

            @meta.decorator()
            @commands.default_member_permissions(64)
            async def overwrite_decorator_below(self, _) -> None:
                ...

        assert Cog.no_overwrite.default_member_permissions is None
        assert Cog().no_overwrite.default_member_permissions == Permissions(32)

        # all of these should overwrite the cog-level attr
        assert Cog.overwrite.default_member_permissions == Permissions(64)
        assert Cog().overwrite.default_member_permissions == Permissions(64)

        assert Cog.overwrite_decorator_above.default_member_permissions == Permissions(64)
        assert Cog().overwrite_decorator_above.default_member_permissions == Permissions(64)

        assert Cog.overwrite_decorator_below.default_member_permissions == Permissions(64)
        assert Cog().overwrite_decorator_below.default_member_permissions == Permissions(64)


def test_contexts_guildcommandinteraction(meta: DecoratorMeta) -> None:
    class Cog(commands.Cog):
        # this shouldn't raise, it should be silently ignored
        @commands.contexts(bot_dm=True)
        @commands.install_types(user=True)
        # this is a legacy parameter, essentially the same as using `GuildCommandInteraction`
        @meta.decorator(guild_only=True)
        async def cmd(self, _) -> None:
            ...

    for c in (Cog, Cog()):
        assert c.cmd.contexts == disnake.InteractionContextTypes(guild=True)
        assert c.cmd.install_types == disnake.ApplicationInstallTypes(guild=True)


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
