# SPDX-License-Identifier: MIT

from typing import Union

import pytest

from disnake.ext import commands


class TestGreedy:
    @pytest.mark.parametrize("param", [int, float | bool])
    @pytest.mark.asyncio
    async def test_valid(self, param) -> None:
        # should not raise
        commands.Greedy[param]

    @pytest.mark.parametrize("param", [None, int | None, Union[None, bool]])  # noqa: UP007
    @pytest.mark.asyncio
    async def test_invalid(self, param) -> None:
        with pytest.raises(TypeError):
            commands.Greedy[param]
