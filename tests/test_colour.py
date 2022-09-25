# SPDX-License-Identifier: MIT

import math
from typing import Tuple

import pytest

from disnake import Color, Colour


def test_init():
    with pytest.raises(TypeError, match=r"Expected int parameter, received str instead."):
        Colour("0")  # type: ignore


@pytest.mark.parametrize(
    ("value", "string"), [(0, "#000000"), (0x123, "#000123"), (0x12AB34, "#12ab34")]
)
def test_str(value: int, string: str):
    assert str(Colour(value)) == string


def test_compare():
    assert Colour(123) == Colour(123)


@pytest.mark.parametrize(
    ("value", "parts"),
    [(0, (0, 0, 0)), (0xA00233, (0xA0, 0x02, 0x33)), (0x123456, (0x12, 0x34, 0x56))],
)
def test_to_rgb(value: int, parts: Tuple[int, int, int]):
    c = Colour(value)
    assert c.to_rgb() == parts
    assert (c.r, c.g, c.b) == parts


@pytest.mark.parametrize(
    ("value", "parts"),
    [(0, (0, 0, 0)), (0xA00233, (0xA0, 0x02, 0x33)), (0x123456, (0x12, 0x34, 0x56))],
)
def test_from_rgb(value: int, parts: Tuple[int, int, int]):
    assert Colour.from_rgb(*parts).value == value


@pytest.mark.parametrize(
    ("value", "parts"),
    [
        (0xFFFFFF, (123 / 360, 0, 1)),
        (0xF4A8B8, (348 / 360, 31 / 100, 96 / 100)),
        (0x5CCFF9, (196 / 360, 63 / 100, 98 / 100)),
    ],
)
def test_from_hsv(value: int, parts: Tuple[float, float, float]):
    expected = Colour(value)
    col = Colour.from_hsv(*parts)
    assert all(math.isclose(a, b, abs_tol=1) for a, b in zip(expected.to_rgb(), col.to_rgb()))


def test_alias():
    assert Color is Colour
