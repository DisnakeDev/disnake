# SPDX-License-Identifier: MIT

from typing import Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake

PaletteTypes = Literal[
    "crimson",
    "berry",
    "sky",
    "teal",
    "forest",
    "bubble_gum",
    "violet",
    "cobalt",
    "clover",
    "lemon",
    "white",
]


class AvatarDecorationData(TypedDict):
    asset: str
    sku_id: Snowflake


class NameplateData(TypedDict):
    sku_id: Snowflake
    asset: str
    label: str
    palette: PaletteTypes


class CollectiblesData(TypedDict, total=False):
    nameplate: NameplateData


class PartialUser(TypedDict):
    id: Snowflake
    username: str
    discriminator: str  # may be removed in future API versions
    global_name: NotRequired[Optional[str]]
    avatar: Optional[str]


PremiumType = Literal[0, 1, 2]


class User(PartialUser, total=False):
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[int]
    locale: str
    verified: bool
    email: Optional[str]
    flags: int
    premium_type: PremiumType
    public_flags: int
    avatar_decoration_data: Optional[AvatarDecorationData]
    collectibles: Optional[CollectiblesData]
