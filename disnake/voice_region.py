# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types.voice import VoiceRegion as VoiceRegionPayload


__all__ = ("VoiceRegion",)


class VoiceRegion:
    """Represents a Discord voice region.

    .. container:: operations

        .. describe:: x == y

            Checks if two :class:`VoiceRegion`\\s are equal.

            .. versionadded:: 2.9

        .. describe:: x != y

            Checks if two :class:`VoiceRegion`\\s are not equal.

            .. versionadded:: 2.9

        .. describe:: str(x)

            Returns the voice region's ID.

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
        Whether this is a custom voice region (used for events/etc).
    """

    __slots__ = (
        "id",
        "name",
        "optimal",
        "deprecated",
        "custom",
    )

    def __init__(self, *, data: VoiceRegionPayload) -> None:
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.deprecated: bool = data.get("deprecated", False)
        self.optimal: bool = data.get("optimal", False)
        self.custom: bool = data.get("custom", False)

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"<VoiceRegion id={self.id!r} name={self.name!r} optimal={self.optimal!r}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, VoiceRegion) and self.id == other.id
