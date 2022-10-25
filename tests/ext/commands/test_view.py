# SPDX-License-Identifier: MIT


import pytest

from disnake.ext.commands.errors import (
    ExpectedClosingQuoteError,
    InvalidEndOfQuotedStringError,
    UnexpectedQuoteError,
)
from disnake.ext.commands.view import StringView


class TestView:
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
    def test_get_word(self, text, expected_word):

        view = StringView(text)

        word = view.get_word()

        assert word == expected_word

    @pytest.mark.parametrize(
        ("text", "expected_word"),
        [
            ("hello", "hello"),
            ("how are you", "how"),
            ("  bugs are fun", " "),
            ("''", "''"),
        ],
    )
    def test_get_quoted_word(self, text, expected_word):

        view = StringView(text)

        word = view.get_quoted_word()

        assert word == expected_word

    @pytest.mark.parametrize(
        ("text", "exception"),
        [
            ('hone"stl"y, quotes.', UnexpectedQuoteError),
            ('"""', InvalidEndOfQuotedStringError),
            ('"hello', ExpectedClosingQuoteError),
        ],
    )
    def test_get_quoted_word_raises(self, text, exception):

        view = StringView(text)

        with pytest.raises(exception):
            view.get_quoted_word()
