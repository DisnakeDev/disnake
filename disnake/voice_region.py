"""
The MIT License (MIT)

Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types.voice import VoiceRegion as VoiceRegionPayload


__all__ = ("VoiceRegion",)


class VoiceRegion:
    """Represents a Discord voice region.

    .. versionadded:: 2.5

    Attributes
    ----------
    id: :class:`str`
        Unique ID for the region.
    name: :class:`str`
        The name of the region.
    optimal: :class:`bool`
        True for a single region that is closest to your client.
    deprecated: :class:`bool`
        Whether this is a deprecated voice region (avoid switching to these).
    custom: :class:`bool`
        Whether this is a custom voice region (used for events/etc)
    """

    __slots__ = (
        "id",
        "name",
        "optimal",
        "deprecated",
        "custom",
    )

    def __init__(self, *, data: VoiceRegionPayload):
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.deprecated: bool = data.get("deprecated", False)
        self.optimal: bool = data.get("optimal", False)
        self.custom: bool = data.get("custom", False)

    def __str__(self):
        return self.id

    def __repr__(self):
        return f"<VoiceRegion id={self.id!r} name={self.name!r} optimal={self.optimal!r}>"
