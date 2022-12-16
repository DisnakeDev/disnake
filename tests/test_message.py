# SPDX-License-Identifier: MIT

import pytest

import disnake
from disnake import message
from disnake.utils import MISSING


@pytest.mark.parametrize(
    "emoji",
    [
        # single char
        "💯",
        "🔥",
        # with combining characters
        "👩‍👩‍👧‍👦",
    ],
)
def test_convert_emoji_reaction__standard(emoji):
    assert message.convert_emoji_reaction(emoji) == emoji


@pytest.mark.parametrize(
    "emoji",
    [
        "test:1234",
        ":test:1234",
        "<:test:1234>",
        "a:test:1234",
        "<a:test:1234>",
    ],
)
def test_convert_emoji_reaction__custom(emoji):
    assert message.convert_emoji_reaction(emoji) == "test:1234"


def _create_emoji(animated: bool) -> disnake.Emoji:
    return disnake.Emoji(
        guild=disnake.Object(1),  # type: ignore
        state=MISSING,
        data={"name": "test", "id": 1234, "animated": animated},
    )


@pytest.mark.parametrize(
    ("emoji", "expected"),
    [
        (disnake.PartialEmoji(name="🔥"), "🔥"),
        (_create_emoji(False), "test:1234"),
        (_create_emoji(True), "test:1234"),
        (_create_emoji(False)._to_partial(), "test:1234"),
        (_create_emoji(True)._to_partial(), "test:1234"),
    ],
)
def test_convert_emoji_reaction__object(emoji, expected):
    assert message.convert_emoji_reaction(emoji) == expected
