# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .snowflake import Snowflake
from .user import User

StatusType = Literal["idle", "dnd", "online", "offline"]
StatusDisplayType = Literal[0, 1, 2]


class PresenceData(TypedDict):
    user: User
    status: StatusType
    activities: list[Activity]
    client_status: ClientStatus


class PartialPresenceUpdate(PresenceData):
    guild_id: Snowflake


class ClientStatus(TypedDict, total=False):
    desktop: str
    mobile: str
    web: str


class ActivityTimestamps(TypedDict, total=False):
    start: int
    end: int


class ActivityParty(TypedDict, total=False):
    id: str
    size: list[int]  # (current size, max size)


class ActivityAssets(TypedDict, total=False):
    # large_image/small_image may be a snowflake or prefixed media proxy ID, see:
    # https://discord.com/developers/docs/topics/gateway-events#activity-object-activity-asset-image
    large_image: str
    large_text: str
    large_url: str
    small_image: str
    small_text: str
    small_url: str


class ActivitySecrets(TypedDict, total=False):
    join: str
    spectate: str
    match: str


class ActivityEmoji(TypedDict):
    name: str
    id: NotRequired[Snowflake]
    animated: NotRequired[bool]


ActivityType = Literal[0, 1, 2, 3, 4, 5]


class SendableActivity(TypedDict):
    name: str
    type: ActivityType
    url: NotRequired[str | None]


class Activity(SendableActivity, total=False):
    # `created_at` is required according to docs, but we treat it as optional for easier serialization
    created_at: int
    timestamps: ActivityTimestamps
    application_id: Snowflake
    details: str | None
    details_url: str | None
    state: str | None
    state_url: str | None
    emoji: ActivityEmoji | None
    party: ActivityParty
    assets: ActivityAssets
    secrets: ActivitySecrets
    instance: bool
    flags: int
    # `buttons` is a list of strings when received over gw,
    # bots cannot access the full button data (like urls)
    buttons: list[str]
    # all of these are undocumented, but still useful in some cases:
    id: str | None
    platform: str | None
    sync_id: str | None
    session_id: str | None
    status_display_type: StatusDisplayType | None
