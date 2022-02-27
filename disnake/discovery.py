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

from typing import TYPE_CHECKING, List, Optional, Sequence, Set, overload

from .utils import parse_time

if TYPE_CHECKING:
    from datetime import datetime

    from .guild import Guild
    from .state import ConnectionState
    from .types.discovery import (
        DiscoveryCategory as DiscoveryCategoryPayload,
        DiscoveryMetadata as DiscoveryMetadataPayload,
    )
__all__ = (
    "DiscoveryMetadata",
    "DiscoveryCategory",
)


class DiscoveryMetadata:
    """Represents Discord Guild Discovery Metadata.

    .. versionadded:: 2.5

    Attributes
    ----------
    primary_category_id: int
        The ID of the guild's primary category.
    keywords: List[:class:`int`]
        The list of keywords
    emoji_discoverability_enabled: bool
        Whether or not the guild is discoverable by emojis and stickers
    partner_application_timestamp: Optional[:class:`~datetime.datetime`]
        When the partner application was made, if ever.
    partner_actioned_timestamp: Optional[:class:`~datetime.datetime`]
        When the partner application was acted upon, if ever.
    category_ids: Set[str]
        The subcategory IDs this guild is part of.
    """

    def __init__(self, *, state: ConnectionState, guild: Guild, data: DiscoveryMetadataPayload):
        self._state: ConnectionState = state
        self.guild: Guild = guild

        self.primary_category_id: int = data["primary_category_id"]
        self.keywords: List[str] = data["keywords"]
        self.emoji_discoverability_enabled: bool = data["emoji_discoverability_enabled"]
        self.category_ids: Set[int] = set(data["category_ids"])
        self.partner_actioned_timestamp: Optional[datetime] = parse_time(
            data["partner_actioned_timestamp"]
        )
        self.partner_application_timestamp: Optional[datetime] = parse_time(
            data["partner_application_timestamp"]
        )

    def __repr__(self):
        return (
            f"<DiscoveryMetadata primary_category_id={self.primary_category_id!r} "
            f"keywords={self.keywords!r} category_ids={self.category_ids!r} guild={self.guild!r}>"
        )

    @overload
    async def edit(
        self,
        *,
        primary_category: DiscoveryCategory = ...,
        keywords: List[str] = ...,
        emoji_discoverability_enabled: bool = ...,
    ) -> DiscoveryMetadata:
        ...

    @overload
    async def edit(
        self,
        *,
        primary_category_id: int,
        keywords: List[str] = ...,
        emoji_discoverability_enabled: bool = ...,
    ) -> DiscoveryMetadata:
        ...

    async def edit(
        self,
        primary_category: Optional[DiscoveryCategory] = None,
        primary_category_id: Optional[int] = None,
        keywords: Optional[List[str]] = None,
        emoji_discoverability_enabled: Optional[bool] = None,
    ) -> DiscoveryMetadata:
        """|coro|

        Edits the discovery metadata. All parameters are optional.

        .. note::

            You must have :attr:`~Permissions.manage_guild` permission to
            use this.

        Parameters
        ----------
        primary_category: Optional[:class:`.DiscoveryCategory`]
            The new primary category. May not be provided with ``primary_category_id``.
        primary_category_id: Optional[:class:`int`]
            The new primary category ID. May not be provided with ``primary_category``.
        keywords: Optional[List[:class:`str`]]
            The new keywords.
        emoji_discoverability_enabled: Optional[:class:`bool`]
            Whether or not the guild is discoverable by emojis and stickers.


        Raises
        ------
        Forbidden
            You do not have permission to edit the discovery metadata.
        HTTPException
            Editing the discovery metadata failed.

        Returns
        -------
        DiscoveryMetadata
            The updated metadata instance.
        """
        if primary_category is not None and primary_category_id is not None:
            raise TypeError("only one of primary_category and primary_category_id may be provided.")

        if primary_category is not None:
            primary_category_id = primary_category.id
        elif primary_category_id is not None:
            pass
        else:
            primary_category_id = self.primary_category_id

        if keywords is not None and not isinstance(keywords, Sequence):
            raise TypeError("keywords must be a sequence of strings")
        else:
            keywords = self.keywords

        if emoji_discoverability_enabled is not None:
            if not isinstance(emoji_discoverability_enabled, bool):
                raise TypeError("emoji_discoverability_enabled must be a bool")
        else:
            emoji_discoverability_enabled = self.emoji_discoverability_enabled

        data = await self._state.http.modify_guild_discovery_metadata(
            self.guild.id,
            primary_category_id=primary_category_id,
            keywords=keywords,
            emoji_discoverability_enabled=emoji_discoverability_enabled,
        )
        return DiscoveryMetadata(data=data, state=self._state, guild=self.guild)

    @overload
    async def add_subcategory(self, *, category: DiscoveryCategory = ...) -> None:
        ...

    @overload
    async def add_subcategory(self, *, category_id: int = ...) -> None:
        ...

    async def add_subcategory(
        self,
        *,
        category: Optional[DiscoveryCategory] = None,
        category_id: Optional[int] = None,
    ) -> None:
        if category is not None and category_id is not None:
            raise TypeError("only one of category and category_id may be provided.")
        if category is not None:
            category_id = category.id
        elif category_id is None:
            raise TypeError("category_id or category must be provided")
        await self._state.http.add_guild_discovery_subcategory(self.guild.id, category_id)
        self.category_ids.add(category_id)

    @overload
    async def remove_subcategory(self, *, category: DiscoveryCategory = ...) -> None:
        ...

    @overload
    async def remove_subcategory(self, *, category_id: int = ...) -> None:
        ...

    async def remove_subcategory(
        self,
        *,
        category: Optional[DiscoveryCategory] = None,
        category_id: Optional[int] = None,
    ) -> None:
        if category is not None and category_id is not None:
            raise TypeError("only one of category and category_id may be provided.")
        if category is not None:
            category_id = category.id
        elif category_id is None:
            raise TypeError("category_id or category must be provided")
        await self._state.http.remove_guild_discovery_subcategory(self.guild.id, category_id)
        try:
            self.category_ids.remove(category_id)
        except KeyError:
            pass


class DiscoveryCategory:
    """Represents a Discord Guild Discovery Category.

    .. versionadded:: 2.5

    Attributes
    ----------
    id: int
        The id of this category.
    name: str
        The name of this category.
    primary: bool
        Whether this category is allowed to be set as a guild primary category.
    """

    __slots__ = (
        "id",
        "name",
        "primary",
    )

    def __init__(self, *, data: DiscoveryCategoryPayload):
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.primary: bool = data["is_primary"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<DiscoveryCategory id={self.id!r} name={self.name!r} primary={self.primary!r}>"
