# SPDX-License-Identifier: MIT

import pytest

import disnake
from disnake.http import HTTPClient


@pytest.mark.parametrize(
    ("url", "params", "expected"),
    [
        (
            "wss://gateway.discord.com",
            disnake.GatewayParams(encoding="json", compress=None),
            "wss://gateway.discord.com/?v=10&encoding=json",
        ),
        (
            "wss://gateway.discord.com",
            disnake.GatewayParams(encoding="json", compress="zlib-stream"),
            "wss://gateway.discord.com/?v=10&encoding=json&compress=zlib-stream",
        ),
        # should overwrite existing args if needed
        (
            "wss://gateway.discord.com/?v=42&encoding=etf&v=1111",
            disnake.GatewayParams(encoding="json", compress="zlib-stream"),
            "wss://gateway.discord.com/?v=10&encoding=json&compress=zlib-stream",
        ),
        # should keep other args intact
        (
            "wss://gateway.discord.com/?v=42&stuff=things&a=b",
            disnake.GatewayParams(encoding="json", compress="zlib-stream"),
            "wss://gateway.discord.com/?v=10&stuff=things&a=b&encoding=json&compress=zlib-stream",
        ),
        # should remove compression if set to false
        (
            "wss://gateway.discord.com/?v=10&compress=zlib-stream",
            disnake.GatewayParams(encoding="json", compress=None),
            "wss://gateway.discord.com/?v=10&encoding=json",
        ),
    ],
)
def test_format_gateway_url(url: str, params: disnake.GatewayParams, expected: str) -> None:
    assert HTTPClient._format_gateway_url(url, params=params) == expected
