# SPDX-License-Identifier: MIT

import pytest

from disnake.http import HTTPClient


@pytest.mark.parametrize(
    ("url", "encoding", "zlib", "expected"),
    [
        (
            "wss://gateway.discord.com",
            "json",
            False,
            "wss://gateway.discord.com/?v=10&encoding=json",
        ),
        (
            "wss://gateway.discord.com",
            "json",
            True,
            "wss://gateway.discord.com/?v=10&encoding=json&compress=zlib-stream",
        ),
        # should overwrite existing args if needed
        (
            "wss://gateway.discord.com/?v=42&encoding=etf&v=1111",
            "json",
            True,
            "wss://gateway.discord.com/?v=10&encoding=json&compress=zlib-stream",
        ),
        # should keep other args intact
        (
            "wss://gateway.discord.com/?v=42&stuff=things&a=b",
            "json",
            True,
            "wss://gateway.discord.com/?v=10&stuff=things&a=b&encoding=json&compress=zlib-stream",
        ),
        # should remove compression if set to false
        (
            "wss://gateway.discord.com/?v=10&compress=zlib-stream",
            "json",
            False,
            "wss://gateway.discord.com/?v=10&encoding=json",
        ),
    ],
)
def test_format_gateway_url(url: str, encoding: str, zlib: bool, expected: str):
    assert HTTPClient._format_gateway_url(url, encoding=encoding, zlib=zlib) == expected
