# SPDX-License-Identifier: MIT

import pytest

from disnake.ext.commands.errors import (
    ExpectedClosingQuoteError,
    InvalidEndOfQuotedStringError,
    UnexpectedQuoteError,
)
from disnake.ext.commands.view import StringView


class TestStringView:
    @pytest.mark.parametrize(
        ("text", "expected_word"),
        [
            ("hello", "hello"),
            ("how are you", "how"),
            ("  bugs are fun", ""),
            ('"""', '"""'),
            ("''", "''"),
            ('hone"stl"y, quotes.', 'hone"stl"y,'),
        ],
    )
    def test_get_word(self, text: str, expected_word) -> None:
        view = StringView(text)

        word = view.get_word()

        assert word == expected_word

    @pytest.mark.parametrize(
        ("text", "expected_word"),
        [
            ("hello", "hello"),
            ("how are you", "how"),
            ('"some quotes" here', "some quotes"),
            ("  bugs are fun", " "),
            ("''", "''"),
        ],
    )
    def test_get_quoted_word(self, text: str, expected_word) -> None:
        view = StringView(text)

        word = view.get_quoted_word()

        assert word == expected_word

    @pytest.mark.parametrize(
        ("text", "exception"),
        [
            ('hone"stl"y, quotes.', UnexpectedQuoteError),
            ('"""', InvalidEndOfQuotedStringError),
            ('"hello', ExpectedClosingQuoteError),
            ('"test\\', ExpectedClosingQuoteError),
        ],
    )
    def test_get_quoted_word_raises(self, text: str, exception) -> None:
        view = StringView(text)

        with pytest.raises(exception):
            view.get_quoted_word()
