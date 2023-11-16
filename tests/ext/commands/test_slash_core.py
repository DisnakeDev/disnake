# SPDX-License-Identifier: MIT

from disnake.ext import commands


class TestParents:
    # not using a fixture for typing reasons
    def _create_cog(self):
        class Cog(commands.Cog):
            @commands.slash_command()
            async def a(self, _) -> None:
                ...

            @a.sub_command()
            async def sub(self, _) -> None:
                ...

            @a.sub_command_group()
            async def group(self, _) -> None:
                ...

            @group.sub_command()
            async def subsub(self, _) -> None:
                ...

        return Cog()

    def test_parent(self) -> None:
        cog = self._create_cog()
        assert cog.a.parent is None
        assert cog.sub.parent is cog.a
        assert cog.group.parent is cog.a
        assert cog.subsub.parent is cog.group

    def test_qualified_name(self) -> None:
        cog = self._create_cog()
        assert cog.a.qualified_name == "a"
        assert cog.sub.qualified_name == "a sub"
        assert cog.group.qualified_name == "a group"
        assert cog.subsub.qualified_name == "a group subsub"

    def test_root_parent(self) -> None:
        cog = self._create_cog()
        assert cog.a.root_parent is None
        assert cog.sub.root_parent is cog.a
        assert cog.group.root_parent is cog.a
        assert cog.subsub.root_parent is cog.a

    def test_parents(self) -> None:
        cog = self._create_cog()
        assert cog.a.parents == ()
        assert cog.sub.parents == (cog.a,)
        assert cog.group.parents == (cog.a,)
        assert cog.subsub.parents == (cog.group, cog.a)
