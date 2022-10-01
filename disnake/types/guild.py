# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict

from .activity import PartialPresenceUpdate
from .channel import GuildChannel, StageInstance
from .emoji import Emoji
from .guild_scheduled_event import GuildScheduledEvent
from .member import Member
from .role import Role
from .snowflake import Snowflake
from .sticker import GuildSticker
from .threads import Thread
from .user import User
from .voice import GuildVoiceState
from .welcome_screen import WelcomeScreen


class Ban(TypedDict):
    reason: Optional[str]
    user: User


class _UnavailableGuildOptional(TypedDict, total=False):
    unavailable: bool


class UnavailableGuild(_UnavailableGuildOptional):
    id: Snowflake


class _GuildOptional(TypedDict, total=False):
    icon_hash: Optional[str]
    owner: bool
    permissions: str
    widget_enabled: bool
    widget_channel_id: Optional[Snowflake]
    joined_at: Optional[str]
    large: bool
    member_count: int
    voice_states: List[GuildVoiceState]
    members: List[Member]
    channels: List[GuildChannel]
    presences: List[PartialPresenceUpdate]
    threads: List[Thread]
    max_presences: Optional[int]
    max_members: int
    premium_subscription_count: int
    max_video_channel_users: int
    approximate_member_count: int
    approximate_presence_count: int
    stage_instances: List[StageInstance]
    stickers: List[GuildSticker]
    guild_scheduled_events: List[GuildScheduledEvent]


DefaultMessageNotificationLevel = Literal[0, 1]
ExplicitContentFilterLevel = Literal[0, 1, 2]
MFALevel = Literal[0, 1]
VerificationLevel = Literal[0, 1, 2, 3, 4]
NSFWLevel = Literal[0, 1, 2, 3]
PremiumTier = Literal[0, 1, 2, 3]
GuildFeature = Literal[
    "ANIMATED_BANNER",
    "ANIMATED_ICON",
    "AUTO_MODERATION",
    "BANNER",
    "COMMUNITY",
    "CREATOR_MONETIZABLE",  # not yet documented/finalised
    "DISCOVERABLE",
    "ENABLED_DISCOVERABLE_BEFORE",
    "FEATURABLE",
    "GUILD_HOME_TEST",  # not yet documented/finalised
    "HAS_DIRECTORY_ENTRY",
    "HUB",
    "INVITE_SPLASH",
    "INVITES_DISABLED",
    "LINKED_TO_HUB",
    "MEMBER_PROFILES",  # not sure what this does, if anything
    "MEMBER_VERIFICATION_GATE_ENABLED",
    "MONETIZATION_ENABLED",
    "MORE_EMOJI",
    "MORE_STICKERS",
    "NEWS",
    "NEW_THREAD_PERMISSIONS",  # deprecated
    "PARTNERED",
    "PREVIEW_ENABLED",
    "PRIVATE_THREADS",
    "RELAY_ENABLED",
    "ROLE_ICONS",
    "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE",  # not yet documented/finalised
    "ROLE_SUBSCRIPTIONS_ENABLED",  # not yet documented/finalised
    "SEVEN_DAY_THREAD_ARCHIVE",  # deprecated
    "TEXT_IN_VOICE_ENABLED",  # deprecated
    "THREADS_ENABLED",  # deprecated
    "THREE_DAY_THREAD_ARCHIVE",  # deprecated
    "TICKETED_EVENTS_ENABLED",  # deprecated
    "VANITY_URL",
    "VERIFIED",
    "VIP_REGIONS",
    "WELCOME_SCREEN_ENABLED",
]


class _BaseGuildPreview(UnavailableGuild):
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    emojis: List[Emoji]
    features: List[GuildFeature]
    description: Optional[str]
    stickers: List[GuildSticker]


class GuildPreview(_BaseGuildPreview):
    approximate_member_count: int
    approximate_presence_count: int


class Guild(_BaseGuildPreview, _GuildOptional):
    owner_id: Snowflake
    region: str
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    verification_level: VerificationLevel
    default_message_notifications: DefaultMessageNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel
    roles: List[Role]
    mfa_level: MFALevel
    nsfw_level: NSFWLevel
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    vanity_url_code: Optional[str]
    banner: Optional[str]
    premium_progress_bar_enabled: bool
    premium_tier: PremiumTier
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]


class InviteGuild(Guild, total=False):
    welcome_screen: WelcomeScreen


class GuildPrune(TypedDict):
    pruned: int


class ChannelPositionUpdate(TypedDict):
    id: Snowflake
    position: Optional[int]
    lock_permissions: Optional[bool]
    parent_id: Optional[Snowflake]


class _RolePositionRequired(TypedDict):
    id: Snowflake


class RolePositionUpdate(_RolePositionRequired, total=False):
    position: Optional[Snowflake]


class MFALevelUpdate(TypedDict):
    level: MFALevel
