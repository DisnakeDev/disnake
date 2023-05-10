# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict, Union

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .user import User

StickerFormatType = Literal[1, 2, 3, 4]


class StickerItem(TypedDict):
    id: Snowflake
    name: str
    format_type: StickerFormatType


class BaseSticker(TypedDict):
    id: Snowflake
    name: str
    description: Optional[str]
    tags: str
    format_type: StickerFormatType


class StandardSticker(BaseSticker):
    type: Literal[1]
    pack_id: Snowflake
    sort_value: int


class GuildSticker(BaseSticker):
    type: Literal[2]
    available: NotRequired[bool]
    guild_id: Snowflake
    user: NotRequired[User]


Sticker = Union[BaseSticker, StandardSticker, GuildSticker]


class StickerPack(TypedDict):
    id: Snowflake
    stickers: List[StandardSticker]
    name: str
    sku_id: Snowflake
    cover_sticker_id: NotRequired[Snowflake]
    description: str
    banner_asset_id: NotRequired[Snowflake]


class CreateGuildSticker(TypedDict):
    name: str
    tags: str
    description: str


class EditGuildSticker(TypedDict, total=False):
    name: str
    tags: str
    description: Optional[str]


class ListPremiumStickerPacks(TypedDict):
    sticker_packs: List[StickerPack]
