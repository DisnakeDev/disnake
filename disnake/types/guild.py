# SPDX-License-Identifier: MIT

from typing import Literal, Optional, TypedDict

from typing_extensions import NotRequired

from disnake.types.activity import PartialPresenceUpdate
from disnake.types.channel import CreateGuildChannel, GuildChannel, StageInstance
from disnake.types.emoji import Emoji
from disnake.types.guild_scheduled_event import GuildScheduledEvent
from disnake.types.member import Member
from disnake.types.role import CreateRole, Role
from disnake.types.snowflake import Snowflake
from disnake.types.soundboard import GuildSoundboardSound
from disnake.types.sticker import GuildSticker
from disnake.types.threads import Thread
from disnake.types.user import User
from disnake.types.voice import GuildVoiceState
from disnake.types.welcome_screen import WelcomeScreen


class Ban(TypedDict):
    reason: Optional[str]
    user: User


class BulkBanResult(TypedDict):
    banned_users: list[Snowflake]
    failed_users: list[Snowflake]


class UnavailableGuild(TypedDict):
    id: Snowflake
    unavailable: NotRequired[bool]


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
    "CREATOR_MONETIZABLE_PROVISIONAL",
    "CREATOR_STORE_PAGE",
    "DEVELOPER_SUPPORT_SERVER",
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
    "MORE_EMOJI",
    "MORE_SOUNDBOARD",
    "MORE_STICKERS",
    "NEWS",
    "NEW_THREAD_PERMISSIONS",  # deprecated
    "PARTNERED",
    "PREVIEW_ENABLED",
    "PRIVATE_THREADS",  # deprecated
    "RAID_ALERTS_DISABLED",
    "RELAY_ENABLED",
    "ROLE_ICONS",
    "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE",
    "ROLE_SUBSCRIPTIONS_ENABLED",
    "SEVEN_DAY_THREAD_ARCHIVE",  # deprecated
    "SOUNDBOARD",
    "TEXT_IN_VOICE_ENABLED",  # deprecated
    "THREADS_ENABLED",  # deprecated
    "THREE_DAY_THREAD_ARCHIVE",  # deprecated
    "TICKETED_EVENTS_ENABLED",  # deprecated
    "VANITY_URL",
    "VERIFIED",
    "VIP_REGIONS",
    "WELCOME_SCREEN_ENABLED",
]


class IncidentsData(TypedDict, total=False):
    invites_disabled_until: Optional[str]
    dms_disabled_until: Optional[str]
    dm_spam_detected_at: Optional[str]
    raid_detected_at: Optional[str]


class _BaseGuildPreview(UnavailableGuild):
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    emojis: list[Emoji]
    features: list[GuildFeature]
    description: Optional[str]
    stickers: list[GuildSticker]


class GuildPreview(_BaseGuildPreview):
    approximate_member_count: int
    approximate_presence_count: int


class Guild(_BaseGuildPreview):
    icon_hash: NotRequired[Optional[str]]
    owner: NotRequired[bool]
    owner_id: Snowflake
    permissions: NotRequired[str]
    region: str
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    widget_enabled: NotRequired[bool]
    widget_channel_id: NotRequired[Optional[Snowflake]]
    verification_level: VerificationLevel
    default_message_notifications: DefaultMessageNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel
    roles: list[Role]
    mfa_level: MFALevel
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    max_presences: NotRequired[Optional[int]]
    max_members: NotRequired[int]
    vanity_url_code: Optional[str]
    banner: Optional[str]
    premium_tier: PremiumTier
    premium_subscription_count: NotRequired[int]
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]
    max_video_channel_users: NotRequired[int]
    max_stage_video_channel_users: NotRequired[int]
    approximate_member_count: NotRequired[int]
    approximate_presence_count: NotRequired[int]
    nsfw_level: NSFWLevel
    stickers: NotRequired[list[GuildSticker]]
    premium_progress_bar_enabled: bool
    safety_alerts_channel_id: Optional[Snowflake]
    incidents_data: Optional[IncidentsData]

    # specific to GUILD_CREATE event
    joined_at: NotRequired[Optional[str]]
    large: NotRequired[bool]
    member_count: NotRequired[int]
    voice_states: NotRequired[list[GuildVoiceState]]
    members: NotRequired[list[Member]]
    channels: NotRequired[list[GuildChannel]]
    threads: NotRequired[list[Thread]]
    presences: NotRequired[list[PartialPresenceUpdate]]
    stage_instances: NotRequired[list[StageInstance]]
    guild_scheduled_events: NotRequired[list[GuildScheduledEvent]]
    soundboard_sounds: NotRequired[list[GuildSoundboardSound]]


class InviteGuild(Guild, total=False):
    welcome_screen: WelcomeScreen


class GuildPrune(TypedDict):
    pruned: int


class ChannelPositionUpdate(TypedDict):
    id: Snowflake
    position: Optional[int]
    lock_permissions: NotRequired[Optional[bool]]
    parent_id: NotRequired[Optional[Snowflake]]


class RolePositionUpdate(TypedDict):
    id: Snowflake
    position: NotRequired[Optional[Snowflake]]


class MFALevelUpdate(TypedDict):
    level: MFALevel


class CreateGuildPlaceholderRole(CreateRole):
    id: Snowflake


class CreateGuildPlaceholderChannel(CreateGuildChannel):
    id: NotRequired[Snowflake]


class CreateGuild(TypedDict):
    name: str
    icon: NotRequired[str]
    verification_level: NotRequired[VerificationLevel]
    default_message_notifications: NotRequired[DefaultMessageNotificationLevel]
    explicit_content_filter: NotRequired[ExplicitContentFilterLevel]
    roles: NotRequired[list[CreateGuildPlaceholderRole]]
    channels: NotRequired[list[CreateGuildPlaceholderChannel]]
    afk_channel_id: NotRequired[Snowflake]
    afk_timeout: NotRequired[int]
    system_channel_id: NotRequired[Snowflake]
    system_channel_flags: NotRequired[int]
