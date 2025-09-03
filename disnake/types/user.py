# SPDX-License-Identifier: MIT

from typing import Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake

PaletteType = Literal[
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


class Nameplate(TypedDict):
    sku_id: Snowflake
    asset: str
    label: str
    palette: PaletteType


class Collectibles(TypedDict, total=False):
    nameplate: Nameplate


# note: this is documented as not optional (always present)
# but we made it optional because on certain circumstances the API
# is not sending it (not sure if it's a bug, better safe than sorry)
class UserPrimaryGuild(TypedDict, total=False):
    identity_guild_id: Optional[Snowflake]
    identity_enabled: Optional[bool]
    tag: Optional[str]
    badge: Optional[str]


class PartialUser(TypedDict):
    id: Snowflake
    username: str
    discriminator: str  # may be removed in future API versions
    global_name: NotRequired[Optional[str]]
    avatar: Optional[str]
    collectibles: NotRequired[Optional[Collectibles]]
    primary_guild: Optional[UserPrimaryGuild]


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
