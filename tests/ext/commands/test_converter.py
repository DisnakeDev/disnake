# SPDX-License-Identifier: MIT

from typing import Union
from unittest import mock

import pytest

from disnake.ext import commands


class TestGreedy:
    @pytest.mark.parametrize("param", [int, float | bool])
    def test_valid(self, param) -> None:
        # should not raise
        commands.Greedy[param]

    @pytest.mark.parametrize("param", [None, int | None, Union[None, bool]])  # noqa: UP007
    def test_invalid(self, param) -> None:
        with pytest.raises(TypeError):
            commands.Greedy[param]


class TestColourConverter:
    @pytest.mark.parametrize("colour_name", ["blurple", "dark_teal"])
    @pytest.mark.asyncio
    async def test_name_valid(self, colour_name: str) -> None:
        # should not raise
        await commands.ColourConverter().convert(mock.Mock(), colour_name)

    @pytest.mark.parametrize("colour_name", ["from_rgb", "holographic_style", "__dict__"])
    @pytest.mark.asyncio
    async def test_name_invalid(self, colour_name: str) -> None:
        with pytest.raises(commands.BadColourArgument):
            await commands.ColourConverter().convert(mock.Mock(), colour_name)
