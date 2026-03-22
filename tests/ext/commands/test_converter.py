# SPDX-License-Identifier: MIT

from unittest import mock

import pytest

import disnake
from disnake.ext.commands import BadColourArgument
from disnake.ext.commands.converter import ColourConverter


@pytest.fixture
def converter() -> ColourConverter:
    return ColourConverter()


@pytest.fixture
def ctx() -> mock.Mock:
    return mock.Mock()


class TestColourConverter:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("arg", "expected_value"),
        [
            ("red", 0xE74C3C),
            ("dark_green", 0x1F8B4C),
            ("blurple", 0x5865F2),
            ("dark theme", 0x313338),
            ("og blurple", 0x7289DA),
        ],
    )
    async def test_valid_colour_names(
        self, converter: ColourConverter, ctx: mock.Mock, arg: str, expected_value: int
    ) -> None:
        result = await converter.convert(ctx, arg)
        assert isinstance(result, disnake.Colour)
        assert result.value == expected_value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arg",
        [
            "holographic_style",
            "holographic style",
            "from_rgb",
            "from_hsv",
            "from_hex",
            "to_rgb",
            "value",
            "__init__",
            "nonexistent",
        ],
    )
    async def test_invalid_colour_names(
        self, converter: ColourConverter, ctx: mock.Mock, arg: str
    ) -> None:
        with pytest.raises(BadColourArgument):
            await converter.convert(ctx, arg)

    @pytest.mark.asyncio
    async def test_hex_format(self, converter: ColourConverter, ctx: mock.Mock) -> None:
        result = await converter.convert(ctx, "#ff0000")
        assert result.value == 0xFF0000

    @pytest.mark.asyncio
    async def test_rgb_format(self, converter: ColourConverter, ctx: mock.Mock) -> None:
        result = await converter.convert(ctx, "rgb(255, 0, 0)")
        assert result.value == 0xFF0000
