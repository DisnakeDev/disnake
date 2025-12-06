# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
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
    identity_guild_id: Snowflake | None
    identity_enabled: bool | None
    tag: str | None
    badge: str | None


class PartialUser(TypedDict):
    id: Snowflake
    username: str
    discriminator: str  # may be removed in future API versions
    global_name: NotRequired[str | None]
    avatar: str | None
    avatar_decoration_data: NotRequired[AvatarDecorationData | None]
    collectibles: NotRequired[Collectibles | None]
    primary_guild: NotRequired[UserPrimaryGuild | None]


PremiumType = Literal[0, 1, 2]


class User(PartialUser, total=False):
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: str | None
    accent_color: int | None
    locale: str
    verified: bool
    email: str | None
    flags: int
    premium_type: PremiumType
    public_flags: int
