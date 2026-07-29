# SPDX-License-Identifier: MIT

import asyncio
from typing import ClassVar

import pytest
from typing_extensions import Self

import disnake
from disnake.http import HTTPClient, Route


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
        (
            "wss://gateway.discord.com",
            disnake.GatewayParams(encoding="json", compress="zstd-stream"),
            "wss://gateway.discord.com/?v=10&encoding=json&compress=zstd-stream",
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
        # should remove compression if set to None
        (
            "wss://gateway.discord.com/?v=10&compress=zlib-stream",
            disnake.GatewayParams(encoding="json", compress=None),
            "wss://gateway.discord.com/?v=10&encoding=json",
        ),
    ],
)
def test_format_gateway_url(url: str, params: disnake.GatewayParams, expected: str) -> None:
    assert HTTPClient._format_gateway_url(url, params=params) == expected


class _GlobalRateLimitResponse:
    """A ``429`` carrying ``global: true``, as sent by Discord."""

    status = 429
    headers: ClassVar[dict[str, str]] = {
        "content-type": "application/json",
        "Via": "1.1 google",
    }

    async def text(self, encoding: str = "utf-8") -> str:
        return '{"global": true, "retry_after": 60.0}'

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> bool:
        return False


class _GlobalRateLimitSession:
    def request(self, method: str, url: str, **kwargs: object) -> _GlobalRateLimitResponse:
        return _GlobalRateLimitResponse()


@pytest.mark.asyncio
async def test_global_rate_limit_released_on_cancellation() -> None:
    # a request cancelled while sleeping off a global rate limit must still
    # re-set `_global_over`, otherwise every later request blocks on it forever
    http = HTTPClient(loop=asyncio.get_running_loop())
    http._HTTPClient__session = _GlobalRateLimitSession()  # pyright: ignore[reportAttributeAccessIssue]

    task = asyncio.create_task(http.request(Route("GET", "/users/@me")))

    # let the request reach the sleep, with the global event now cleared
    for _ in range(10):
        await asyncio.sleep(0)
        if not http._global_over.is_set():
            break
    assert not http._global_over.is_set()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert http._global_over.is_set()
