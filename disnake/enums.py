# SPDX-License-Identifier: MIT
from __future__ import annotations

import types
from functools import total_ordering
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    NamedTuple,
    NoReturn,
    Optional,
    Type,
    TypeVar,
)

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    "Enum",
    "ChannelType",
    "MessageType",
    "SpeakingState",
    "VerificationLevel",
    "ContentFilter",
    "Status",
    "DefaultAvatar",
    "AuditLogAction",
    "AuditLogActionCategory",
    "UserFlags",
    "ActivityType",
    "NotificationLevel",
    "TeamMembershipState",
    "TeamMemberRole",
    "WebhookType",
    "ExpireBehaviour",
    "ExpireBehavior",
    "StickerType",
    "StickerFormatType",
    "InviteType",
    "InviteTarget",
    "VideoQualityMode",
    "ComponentType",
    "ButtonStyle",
    "TextInputStyle",
    "SelectDefaultValueType",
    "StagePrivacyLevel",
    "InteractionType",
    "InteractionResponseType",
    "NSFWLevel",
    "OptionType",
    "ApplicationCommandType",
    "ApplicationCommandPermissionType",
    "PartyType",
    "GuildScheduledEventEntityType",
    "GuildScheduledEventStatus",
    "GuildScheduledEventPrivacyLevel",
    "ThreadArchiveDuration",
    "WidgetStyle",
    "Locale",
    "AutoModTriggerType",
    "AutoModEventType",
    "AutoModActionType",
    "ThreadSortOrder",
    "ThreadLayout",
    "Event",
    "ApplicationRoleConnectionMetadataType",
    "OnboardingPromptType",
    "SKUType",
    "EntitlementType",
    "SubscriptionStatus",
    "PollLayoutType",
    "VoiceChannelEffectAnimationType",
    "MessageReferenceType",
)


class _EnumValueBase(NamedTuple):
    if TYPE_CHECKING:
        _cls_name: ClassVar[str]

    name: str
    value: Any

    def __repr__(self) -> str:
        return f"<{self._cls_name}.{self.name}: {self.value!r}>"

    def __str__(self) -> str:
        return f"{self._cls_name}.{self.name}"


@total_ordering
class _EnumValueComparable(_EnumValueBase):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __lt__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value < other.value


def _create_value_cls(name: str, comparable: bool) -> Type[_EnumValueBase]:
    parent = _EnumValueComparable if comparable else _EnumValueBase
    return type(f"{parent.__name__}_{name}", (parent,), {"_cls_name": name})  # type: ignore


def _is_descriptor(obj):
    return hasattr(obj, "__get__") or hasattr(obj, "__set__") or hasattr(obj, "__delete__")


class EnumMeta(type):
    if TYPE_CHECKING:
        __name__: ClassVar[str]
        _enum_member_names_: ClassVar[List[str]]
        _enum_member_map_: ClassVar[Dict[str, Any]]
        _enum_value_map_: ClassVar[Dict[Any, Any]]
        _enum_value_cls_: ClassVar[Type[_EnumValueBase]]

    def __new__(cls, name: str, bases, attrs, *, comparable: bool = False):
        value_mapping = {}
        member_mapping = {}
        member_names = []

        value_cls = _create_value_cls(name, comparable)
        for key, value in list(attrs.items()):
            is_descriptor = _is_descriptor(value)
            if key[0] == "_" and not is_descriptor:
                continue

            # Special case classmethod to just pass through
            if isinstance(value, classmethod):
                continue

            if is_descriptor:
                setattr(value_cls, key, value)
                del attrs[key]
                continue

            try:
                new_value = value_mapping[value]
            except KeyError:
                new_value = value_cls(name=key, value=value)
                value_mapping[value] = new_value
                member_names.append(key)

            member_mapping[key] = new_value
            attrs[key] = new_value

        attrs["_enum_value_map_"] = value_mapping
        attrs["_enum_member_map_"] = member_mapping
        attrs["_enum_member_names_"] = member_names
        attrs["_enum_value_cls_"] = value_cls
        actual_cls = super().__new__(cls, name, bases, attrs)
        value_cls._actual_enum_cls_ = actual_cls  # type: ignore
        return actual_cls

    def __iter__(cls) -> Iterator[Self]:
        return (cls._enum_member_map_[name] for name in cls._enum_member_names_)

    def __reversed__(cls) -> Iterator[Self]:
        return (cls._enum_member_map_[name] for name in reversed(cls._enum_member_names_))

    def __len__(cls) -> int:
        return len(cls._enum_member_names_)

    def __repr__(cls) -> str:
        return f"<enum {cls.__name__}>"

    @property
    def __members__(cls):
        return types.MappingProxyType(cls._enum_member_map_)

    def __call__(cls, value):
        try:
            return cls._enum_value_map_[value]
        except (KeyError, TypeError):
            raise ValueError(f"{value!r} is not a valid {cls.__name__}") from None

    def __getitem__(cls, key):
        return cls._enum_member_map_[key]

    def __setattr__(cls, name: str, value) -> NoReturn:
        raise TypeError("Enums are immutable.")

    def __delattr__(cls, attr) -> NoReturn:
        raise TypeError("Enums are immutable")

    def __instancecheck__(self, instance) -> bool:
        # isinstance(x, Y)
        # -> __instancecheck__(Y, x)
        try:
            return instance._actual_enum_cls_ is self
        except AttributeError:
            return False


if TYPE_CHECKING:
    from enum import Enum
else:

    class Enum(metaclass=EnumMeta):
        @classmethod
        def try_value(cls, value):
            try:
                return cls._enum_value_map_[value]
            except (KeyError, TypeError):
                return value


class ChannelType(Enum):
    """Specifies the type of channel."""

    text = 0
    """A text channel."""
    private = 1
    """A private text channel. Also called a direct message."""
    voice = 2
    """A voice channel."""
    group = 3
    """A private group text channel."""
    category = 4
    """A category channel."""
    news = 5
    """A guild news channel."""
    news_thread = 10
    """A news thread.

    .. versionadded:: 2.0
    """
    public_thread = 11
    """A public thread.

    .. versionadded:: 2.0
    """
    private_thread = 12
    """A private thread.

    .. versionadded:: 2.0
    """
    stage_voice = 13
    """A guild stage voice channel.

    .. versionadded:: 1.7
    """
    guild_directory = 14
    """A student hub channel.

    .. versionadded:: 2.1
    """
    forum = 15
    """A channel of only threads.

    .. versionadded:: 2.5
    """
    media = 16
    """A channel of only threads but with a focus on media, similar to forum channels.

    .. versionadded:: 2.10
    """

    def __str__(self) -> str:
        return self.name


class MessageType(Enum):
    """Specifies the type of :class:`Message`. This is used to denote if a message
    is to be interpreted as a system message or a regular message.
    """

    default = 0
    """The default message type. This is the same as regular messages."""
    recipient_add = 1
    """The system message when a user is added to a group private message or a thread."""
    recipient_remove = 2
    """The system message when a user is removed from a group private message or a thread."""
    call = 3
    """The system message denoting call state, e.g. missed call, started call, etc."""
    channel_name_change = 4
    """The system message denoting that a channel's name has been changed."""
    channel_icon_change = 5
    """The system message denoting that a channel's icon has been changed."""
    pins_add = 6
    """The system message denoting that a pinned message has been added to a channel."""
    new_member = 7
    """The system message denoting that a new member has joined a Guild."""
    premium_guild_subscription = 8
    """The system message denoting that a member has "nitro boosted" a guild."""
    premium_guild_tier_1 = 9
    """The system message denoting that a member has "nitro boosted" a guild and it achieved level 1."""
    premium_guild_tier_2 = 10
    """The system message denoting that a member has "nitro boosted" a guild and it achieved level 2."""
    premium_guild_tier_3 = 11
    """The system message denoting that a member has "nitro boosted" a guild and it achieved level 3."""
    channel_follow_add = 12
    """The system message denoting that an announcement channel has been followed.

    .. versionadded:: 1.3
    """
    guild_stream = 13
    """The system message denoting that a member is streaming in the guild.

    .. versionadded:: 1.7
    """
    guild_discovery_disqualified = 14
    """The system message denoting that the guild is no longer eligible for Server Discovery.

    .. versionadded:: 1.7
    """
    guild_discovery_requalified = 15
    """The system message denoting that the guild has become eligible again for Server Discovery.

    .. versionadded:: 1.7
    """
    guild_discovery_grace_period_initial_warning = 16
    """The system message denoting that the guild has failed to meet the Server
    Discovery requirements for one week.

    .. versionadded:: 1.7
    """
    guild_discovery_grace_period_final_warning = 17
    """The system message denoting that the guild has failed to meet the Server
    Discovery requirements for 3 weeks in a row.

    .. versionadded:: 1.7
    """
    thread_created = 18
    """The system message denoting that a thread has been created. This is only
    sent if the thread has been created from an older message. The period of time
    required for a message to be considered old cannot be relied upon and is up to
    Discord.

    .. versionadded:: 2.0
    """
    reply = 19
    """The system message denoting that the author is replying to a message.

    .. versionadded:: 2.0
    """
    application_command = 20
    """The system message denoting that an application (or "slash") command was executed.

    .. versionadded:: 2.0
    """
    thread_starter_message = 21
    """The system message denoting the message in the thread that is the one that started the
    thread's conversation topic.

    .. versionadded:: 2.0
    """
    guild_invite_reminder = 22
    """The system message sent as a reminder to invite people to the guild.

    .. versionadded:: 2.0
    """
    context_menu_command = 23
    """The system message denoting that a context menu command was executed.

    .. versionadded:: 2.3
    """
    auto_moderation_action = 24
    """The system message denoting that an auto moderation action was executed.

    .. versionadded:: 2.5
    """
    role_subscription_purchase = 25
    """The system message denoting that a role subscription was purchased.

    .. versionadded:: 2.9
    """
    interaction_premium_upsell = 26
    """The system message for an application premium subscription upsell.

    .. versionadded:: 2.8
    """
    stage_start = 27
    """The system message denoting the stage has been started.

    .. versionadded:: 2.9
    """
    stage_end = 28
    """The system message denoting the stage has ended.

    .. versionadded:: 2.9
    """
    stage_speaker = 29
    """The system message denoting a user has become a speaker.

    .. versionadded:: 2.9
    """
    stage_topic = 31
    """The system message denoting the stage topic has been changed.

    .. versionadded:: 2.9
    """
    guild_application_premium_subscription = 32
    """The system message denoting that a guild member has subscribed to an application.

    .. versionadded:: 2.8
    """
    guild_incident_alert_mode_enabled = 36
    """The system message denoting that an admin enabled security actions.

    .. versionadded:: 2.10
    """
    guild_incident_alert_mode_disabled = 37
    """The system message denoting that an admin disabled security actions.

    .. versionadded:: 2.10
    """
    guild_incident_report_raid = 38
    """The system message denoting that an admin reported a raid.

    .. versionadded:: 2.10
    """
    guild_incident_report_false_alarm = 39
    """The system message denoting that a raid report was a false alarm.

    .. versionadded:: 2.10
    """
    poll_result = 46
    """The system message denoting that a poll expired, announcing the most voted answer.

    .. versionadded:: 2.10
    """


class PartyType(Enum):
    """Represents the type of a voice channel activity/application.

    .. deprecated:: 2.9
    """

    poker = 755827207812677713
    """The "Poker Night" activity."""
    betrayal = 773336526917861400
    """The "Betrayal.io" activity."""
    fishing = 814288819477020702
    """The "Fishington.io" activity."""
    chess = 832012774040141894
    """The "Chess In The Park" activity."""
    letter_tile = 879863686565621790
    """The "Letter Tile" activity."""
    word_snack = 879863976006127627
    """The "Word Snacks" activity."""
    doodle_crew = 878067389634314250
    """The "Doodle Crew" activity."""
    checkers = 832013003968348200
    """The "Checkers In The Park" activity.

    .. versionadded:: 2.3
    """
    spellcast = 852509694341283871
    """The "SpellCast" activity.

    .. versionadded:: 2.3
    """
    watch_together = 880218394199220334
    """The "Watch Together" activity, a Youtube application.

    .. versionadded:: 2.3
    """
    sketch_heads = 902271654783242291
    """The "Sketch Heads" activity.

    .. versionadded:: 2.4
    """
    ocho = 832025144389533716
    """The "Ocho" activity.

    .. versionadded:: 2.4
    """
    gartic_phone = 1007373802981822582
    """The "Gartic Phone" activity.

    .. versionadded:: 2.9
    """


# undocumented/internal
class SpeakingState(Enum):
    none = 0
    voice = 1 << 0
    soundshare = 1 << 1
    priority = 1 << 2

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.value


class VerificationLevel(Enum, comparable=True):
    """Specifies a :class:`Guild`\\'s verification level, which is the criteria in
    which a member must meet before being able to send messages to the guild.

    .. collapse:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two verification levels are equal.
        .. describe:: x != y

            Checks if two verification levels are not equal.
        .. describe:: x > y

            Checks if a verification level is higher than another.
        .. describe:: x < y

            Checks if a verification level is lower than another.
        .. describe:: x >= y

            Checks if a verification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a verification level is lower or equal to another.
    """

    none = 0
    """No criteria set."""
    low = 1
    """Member must have a verified email on their Discord account."""
    medium = 2
    """Member must have a verified email and be registered on Discord for more than five minutes."""
    high = 3
    """Member must have a verified email, be registered on Discord for more
    than five minutes, and be a member of the guild itself for more than ten minutes.
    """
    highest = 4
    """Member must have a verified phone on their Discord account."""

    def __str__(self) -> str:
        return self.name


class ContentFilter(Enum, comparable=True):
    """Specifies a :class:`Guild`\\'s explicit content filter, which is the machine
    learning algorithms that Discord uses to detect if an image contains NSFW content.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two content filter levels are equal.
        .. describe:: x != y

            Checks if two content filter levels are not equal.
        .. describe:: x > y

            Checks if a content filter level is higher than another.
        .. describe:: x < y

            Checks if a content filter level is lower than another.
        .. describe:: x >= y

            Checks if a content filter level is higher or equal to another.
        .. describe:: x <= y

            Checks if a content filter level is lower or equal to another.
    """

    disabled = 0
    """The guild does not have the content filter enabled."""
    no_role = 1
    """The guild has the content filter enabled for members without a role."""
    all_members = 2
    """The guild has the content filter enabled for every member."""

    def __str__(self) -> str:
        return self.name


class Status(Enum):
    """Specifies a :class:`Member`\\'s status."""

    online = "online"
    """The member is online."""
    offline = "offline"
    """The member is offline."""
    idle = "idle"
    """The member is idle."""
    dnd = "dnd"
    """The member is "Do Not Disturb"."""
    do_not_disturb = "dnd"
    """An alias for :attr:`dnd`."""
    invisible = "invisible"
    """The member is "invisible". In reality, this is only used in sending
    a presence a la :meth:`Client.change_presence`. When you receive a
    user's presence this will be :attr:`offline` instead.
    """
    streaming = "streaming"
    """The member is live streaming to Twitch or YouTube.

    .. versionadded:: 2.3
    """

    def __str__(self) -> str:
        return self.value


class DefaultAvatar(Enum):
    """Represents the default avatar of a Discord :class:`User`."""

    blurple = 0
    """Represents the default avatar with the color blurple. See also :attr:`Colour.blurple`."""
    grey = 1
    """Represents the default avatar with the color grey. See also :attr:`Colour.greyple`."""
    gray = 1
    """An alias for :attr:`grey`."""
    green = 2
    """Represents the default avatar with the color green. See also :attr:`Colour.green`."""
    orange = 3
    """Represents the default avatar with the color orange. See also :attr:`Colour.orange`."""
    red = 4
    """Represents the default avatar with the color red. See also :attr:`Colour.red`."""
    fuchsia = 5
    """Represents the default avatar with the color fuchsia. See also :attr:`Colour.fuchsia`.

    .. versionadded:: 2.9
    """

    def __str__(self) -> str:
        return self.name


class NotificationLevel(Enum, comparable=True):
    """Specifies whether a :class:`Guild` has notifications on for all messages or mentions only by default.

    .. collapse:: operations

        .. describe:: x == y

            Checks if two notification levels are equal.
        .. describe:: x != y

            Checks if two notification levels are not equal.
        .. describe:: x > y

            Checks if a notification level is higher than another.
        .. describe:: x < y

            Checks if a notification level is lower than another.
        .. describe:: x >= y

            Checks if a notification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a notification level is lower or equal to another.
    """

    all_messages = 0
    """Members receive notifications for every message regardless of them being mentioned."""
    only_mentions = 1
    """Members receive notifications for messages they are mentioned in."""


class AuditLogActionCategory(Enum):
    """Represents the category that the :class:`AuditLogAction` belongs to.

    This can be retrieved via :attr:`AuditLogEntry.category`.
    """

    create = 1
    """The action is the creation of something."""
    delete = 2
    """The action is the deletion of something."""
    update = 3
    """The action is the update of something."""


# NOTE: these fields are only fully documented in audit_logs.rst,
# as the docstrings alone would be ~1000-1500 additional lines
class AuditLogAction(Enum):
    """Represents the type of action being done for a :class:`AuditLogEntry`\\,
    which is retrievable via :meth:`Guild.audit_logs` or via the :func:`on_audit_log_entry_create` event.
    """

    # fmt: off
    guild_update                          = 1
    channel_create                        = 10
    channel_update                        = 11
    channel_delete                        = 12
    overwrite_create                      = 13
    overwrite_update                      = 14
    overwrite_delete                      = 15
    kick                                  = 20
    member_prune                          = 21
    ban                                   = 22
    unban                                 = 23
    member_update                         = 24
    member_role_update                    = 25
    member_move                           = 26
    member_disconnect                     = 27
    bot_add                               = 28
    role_create                           = 30
    role_update                           = 31
    role_delete                           = 32
    invite_create                         = 40
    invite_update                         = 41
    invite_delete                         = 42
    webhook_create                        = 50
    webhook_update                        = 51
    webhook_delete                        = 52
    emoji_create                          = 60
    emoji_update                          = 61
    emoji_delete                          = 62
    message_delete                        = 72
    message_bulk_delete                   = 73
    message_pin                           = 74
    message_unpin                         = 75
    integration_create                    = 80
    integration_update                    = 81
    integration_delete                    = 82
    stage_instance_create                 = 83
    stage_instance_update                 = 84
    stage_instance_delete                 = 85
    sticker_create                        = 90
    sticker_update                        = 91
    sticker_delete                        = 92
    guild_scheduled_event_create          = 100
    guild_scheduled_event_update          = 101
    guild_scheduled_event_delete          = 102
    thread_create                         = 110
    thread_update                         = 111
    thread_delete                         = 112
    application_command_permission_update = 121
    soundboard_sound_create               = 130
    soundboard_sound_update               = 131
    soundboard_sound_delete               = 132
    automod_rule_create                   = 140
    automod_rule_update                   = 141
    automod_rule_delete                   = 142
    automod_block_message                 = 143
    automod_send_alert_message            = 144
    automod_timeout                       = 145
    creator_monetization_request_created  = 150
    creator_monetization_terms_accepted   = 151
    # fmt: on

    @property
    def category(self) -> Optional[AuditLogActionCategory]:
        # fmt: off
        lookup: Dict[AuditLogAction, Optional[AuditLogActionCategory]] = {
            AuditLogAction.guild_update:                          AuditLogActionCategory.update,
            AuditLogAction.channel_create:                        AuditLogActionCategory.create,
            AuditLogAction.channel_update:                        AuditLogActionCategory.update,
            AuditLogAction.channel_delete:                        AuditLogActionCategory.delete,
            AuditLogAction.overwrite_create:                      AuditLogActionCategory.create,
            AuditLogAction.overwrite_update:                      AuditLogActionCategory.update,
            AuditLogAction.overwrite_delete:                      AuditLogActionCategory.delete,
            AuditLogAction.kick:                                  None,
            AuditLogAction.member_prune:                          None,
            AuditLogAction.ban:                                   None,
            AuditLogAction.unban:                                 None,
            AuditLogAction.member_update:                         AuditLogActionCategory.update,
            AuditLogAction.member_role_update:                    AuditLogActionCategory.update,
            AuditLogAction.member_move:                           None,
            AuditLogAction.member_disconnect:                     None,
            AuditLogAction.bot_add:                               None,
            AuditLogAction.role_create:                           AuditLogActionCategory.create,
            AuditLogAction.role_update:                           AuditLogActionCategory.update,
            AuditLogAction.role_delete:                           AuditLogActionCategory.delete,
            AuditLogAction.invite_create:                         AuditLogActionCategory.create,
            AuditLogAction.invite_update:                         AuditLogActionCategory.update,
            AuditLogAction.invite_delete:                         AuditLogActionCategory.delete,
            AuditLogAction.webhook_create:                        AuditLogActionCategory.create,
            AuditLogAction.webhook_update:                        AuditLogActionCategory.update,
            AuditLogAction.webhook_delete:                        AuditLogActionCategory.delete,
            AuditLogAction.emoji_create:                          AuditLogActionCategory.create,
            AuditLogAction.emoji_update:                          AuditLogActionCategory.update,
            AuditLogAction.emoji_delete:                          AuditLogActionCategory.delete,
            AuditLogAction.message_delete:                        AuditLogActionCategory.delete,
            AuditLogAction.message_bulk_delete:                   AuditLogActionCategory.delete,
            AuditLogAction.message_pin:                           None,
            AuditLogAction.message_unpin:                         None,
            AuditLogAction.integration_create:                    AuditLogActionCategory.create,
            AuditLogAction.integration_update:                    AuditLogActionCategory.update,
            AuditLogAction.integration_delete:                    AuditLogActionCategory.delete,
            AuditLogAction.stage_instance_create:                 AuditLogActionCategory.create,
            AuditLogAction.stage_instance_update:                 AuditLogActionCategory.update,
            AuditLogAction.stage_instance_delete:                 AuditLogActionCategory.delete,
            AuditLogAction.sticker_create:                        AuditLogActionCategory.create,
            AuditLogAction.sticker_update:                        AuditLogActionCategory.update,
            AuditLogAction.sticker_delete:                        AuditLogActionCategory.delete,
            AuditLogAction.thread_create:                         AuditLogActionCategory.create,
            AuditLogAction.thread_update:                         AuditLogActionCategory.update,
            AuditLogAction.thread_delete:                         AuditLogActionCategory.delete,
            AuditLogAction.guild_scheduled_event_create:          AuditLogActionCategory.create,
            AuditLogAction.guild_scheduled_event_update:          AuditLogActionCategory.update,
            AuditLogAction.guild_scheduled_event_delete:          AuditLogActionCategory.delete,
            AuditLogAction.application_command_permission_update: AuditLogActionCategory.update,
            AuditLogAction.soundboard_sound_create:               AuditLogActionCategory.create,
            AuditLogAction.soundboard_sound_update:               AuditLogActionCategory.update,
            AuditLogAction.soundboard_sound_delete:               AuditLogActionCategory.delete,
            AuditLogAction.automod_rule_create:                   AuditLogActionCategory.create,
            AuditLogAction.automod_rule_update:                   AuditLogActionCategory.update,
            AuditLogAction.automod_rule_delete:                   AuditLogActionCategory.delete,
            AuditLogAction.automod_block_message:                 None,
            AuditLogAction.automod_send_alert_message:            None,
            AuditLogAction.automod_timeout:                       None,
            AuditLogAction.creator_monetization_request_created:  None,
            AuditLogAction.creator_monetization_terms_accepted:   None,
        }
        # fmt: on
        return lookup[self]

    @property
    def target_type(self) -> Optional[str]:
        v = self.value
        if v == -1:  # pyright: ignore[reportUnnecessaryComparison]
            return "all"
        elif v < 10:
            return "guild"
        elif v < 20:
            return "channel"
        elif v < 30:
            return "user"
        elif v < 40:
            return "role"
        elif v < 50:
            return "invite"
        elif v < 60:
            return "webhook"
        elif v < 70:
            return "emoji"
        elif v == 73:
            return "channel"
        elif v < 80:
            return "message"
        elif v < 83:
            return "integration"
        elif v < 90:
            return "stage_instance"
        elif v < 93:
            return "sticker"
        elif v < 103:
            return "guild_scheduled_event"
        elif v < 113:
            return "thread"
        elif v < 122:
            return "application_command_or_integration"
        elif v < 140:
            return None
        elif v < 143:
            return "automod_rule"
        elif v < 146:
            return "user"
        elif v < 152:
            return None
        else:
            return None


class UserFlags(Enum):
    """Represents Discord user flags."""

    staff = 1 << 0
    """The user is a Discord Employee."""
    partner = 1 << 1
    """The user is a Discord Partner."""
    hypesquad = 1 << 2
    """The user is a HypeSquad Events member."""
    bug_hunter = 1 << 3
    """The user is a Bug Hunter."""
    mfa_sms = 1 << 4
    """The user has SMS recovery for Multi Factor Authentication enabled."""
    premium_promo_dismissed = 1 << 5
    """The user has dismissed the Discord Nitro promotion."""
    hypesquad_bravery = 1 << 6
    """The user is a HypeSquad Bravery member."""
    hypesquad_brilliance = 1 << 7
    """The user is a HypeSquad Brilliance member."""
    hypesquad_balance = 1 << 8
    """The user is a HypeSquad Balance member."""
    early_supporter = 1 << 9
    """The user is an Early Supporter."""
    team_user = 1 << 10
    """The user is a Team User."""
    system = 1 << 12
    """The user is a system user (i.e. represents Discord officially)."""
    has_unread_urgent_messages = 1 << 13
    """The user has an unread system message."""
    bug_hunter_level_2 = 1 << 14
    """The user is a Bug Hunter Level 2."""
    verified_bot = 1 << 16
    """The user is a Verified Bot."""
    verified_bot_developer = 1 << 17
    """The user is an Early Verified Bot Developer."""
    discord_certified_moderator = 1 << 18
    """The user is a Discord Certified Moderator."""
    http_interactions_bot = 1 << 19
    """The user is a bot that only uses HTTP interactions.

    .. versionadded:: 2.3
    """
    spammer = 1 << 20
    """The user is marked as a spammer.

    .. versionadded:: 2.3
    """
    active_developer = 1 << 22
    """The user is an Active Developer.

    .. versionadded:: 2.8
    """


class ActivityType(Enum):
    """Specifies the type of :class:`Activity`. This is used to check how to
    interpret the activity itself.
    """

    unknown = -1
    """An unknown activity type. This should generally not happen."""
    playing = 0
    """A "Playing" activity type."""
    streaming = 1
    """A "Streaming" activity type."""
    listening = 2
    """A "Listening" activity type."""
    watching = 3
    """A "Watching" activity type."""
    custom = 4
    """A custom activity type."""
    competing = 5
    """A competing activity type.

    .. versionadded:: 1.5
    """

    def __int__(self) -> int:
        return self.value


class TeamMembershipState(Enum):
    """Represents the membership state of a team member retrieved through :func:`Client.application_info`.

    .. versionadded:: 1.3
    """

    invited = 1
    """Represents an invited member."""
    accepted = 2
    """Represents a member currently in the team."""


class TeamMemberRole(Enum):
    """Represents the role of a team member retrieved through :func:`Client.application_info`.

    .. versionadded:: 2.10
    """

    admin = "admin"
    """Admins have the most permissions. An admin can only take destructive actions
    on the team or team-owned apps if they are the team owner.
    """
    developer = "developer"
    """Developers can access information about a team and team-owned applications,
    and take limited actions on them, like configuring interaction
    endpoints or resetting the bot token.
    """
    read_only = "read_only"
    """Read-only members can access information about a team and team-owned applications."""

    def __str__(self) -> str:
        return self.name


class WebhookType(Enum):
    """Represents the type of webhook that can be received.

    .. versionadded:: 1.3
    """

    incoming = 1
    """Represents a webhook that can post messages to channels with a token."""
    channel_follower = 2
    """Represents a webhook that is internally managed by Discord, used for following channels."""
    application = 3
    """Represents a webhook that is used for interactions or applications.

    .. versionadded:: 2.0
    """


class ExpireBehaviour(Enum):
    """Represents the behaviour the :class:`Integration` should perform
    when a user's subscription has finished.

    There is an alias for this called ``ExpireBehavior``.

    .. versionadded:: 1.4
    """

    remove_role = 0
    """This will remove the :attr:`StreamIntegration.role` from the user
    when their subscription is finished.
    """
    kick = 1
    """This will kick the user when their subscription is finished."""


ExpireBehavior = ExpireBehaviour


class StickerType(Enum):
    """Represents the type of sticker.

    .. versionadded:: 2.0
    """

    standard = 1
    """Represents a standard sticker that all users can use."""
    guild = 2
    """Represents a custom sticker created in a guild."""


class StickerFormatType(Enum):
    """Represents the type of sticker images.

    .. versionadded:: 1.6
    """

    png = 1
    """Represents a sticker with a png image."""
    apng = 2
    """Represents a sticker with an apng image."""
    lottie = 3
    """Represents a sticker with a lottie image."""
    gif = 4
    """Represents a sticker with a gif image.

    .. versionadded:: 2.8
    """

    @property
    def file_extension(self) -> str:
        return STICKER_FORMAT_LOOKUP[self]


STICKER_FORMAT_LOOKUP: Dict[StickerFormatType, str] = {
    StickerFormatType.png: "png",
    StickerFormatType.apng: "png",
    StickerFormatType.lottie: "json",
    StickerFormatType.gif: "gif",
}


class InviteType(Enum):
    """Represents the type of an invite.

    .. versionadded:: 2.10
    """

    guild = 0
    """Represents an invite to a guild."""
    group_dm = 1
    """Represents an invite to a group channel."""
    friend = 2
    """Represents a friend invite."""


class InviteTarget(Enum):
    """Represents the invite type for voice channel invites.

    .. versionadded:: 2.0
    """

    unknown = 0
    """The invite doesn't target anyone or anything."""
    stream = 1
    """A stream invite that targets a user."""
    embedded_application = 2
    """A stream invite that targets an embedded application."""


class InteractionType(Enum):
    """Specifies the type of :class:`Interaction`.

    .. versionadded:: 2.0
    """

    ping = 1
    """Represents Discord pinging to see if the interaction response server is alive."""
    application_command = 2
    """Represents an application command interaction."""
    component = 3
    """Represents a component based interaction, i.e. using the Discord Bot UI Kit."""
    application_command_autocomplete = 4
    """Represents an application command autocomplete interaction."""
    modal_submit = 5
    """Represents a modal submit interaction."""


class InteractionResponseType(Enum):
    """Specifies the response type for the interaction.

    .. versionadded:: 2.0
    """

    pong = 1
    """Pongs the interaction when given a ping.

    See also :meth:`InteractionResponse.pong`.
    """
    channel_message = 4
    """Responds to the interaction with a message.

    See also :meth:`InteractionResponse.send_message`.
    """
    deferred_channel_message = 5
    """Responds to the interaction with a message at a later time.

    See also :meth:`InteractionResponse.defer`.
    """
    deferred_message_update = 6
    """Acknowledges the component interaction with a promise that
    the message will update later (though there is no need to actually update the message).

    See also :meth:`InteractionResponse.defer`.
    """
    message_update = 7
    """Responds to the interaction by editing the message.

    See also :meth:`InteractionResponse.edit_message`.
    """
    application_command_autocomplete_result = 8
    """Responds to the autocomplete interaction with suggested choices.

    See also :meth:`InteractionResponse.autocomplete`.
    """
    modal = 9
    """Responds to the interaction by displaying a modal.

    See also :meth:`InteractionResponse.send_modal`.

    .. versionadded:: 2.4
    """
    premium_required = 10
    """Responds to the interaction with a message containing an upgrade button.
    Only available for applications with monetization enabled.

    See also :meth:`InteractionResponse.require_premium`.

    .. versionadded:: 2.10
    """


class VideoQualityMode(Enum):
    """Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0
    """

    auto = 1
    """Represents auto camera video quality."""
    full = 2
    """Represents full camera video quality."""

    def __int__(self) -> int:
        return self.value


class ComponentType(Enum):
    """Represents the type of component.

    .. versionadded:: 2.0
    """

    action_row = 1
    """Represents the group component which holds different components in a row."""
    button = 2
    """Represents a button component."""
    string_select = 3
    """Represents a string select component.

    .. versionadded:: 2.7
    """
    select = 3  # backwards compatibility
    """An alias of :attr:`string_select`."""
    text_input = 4
    """Represents a text input component."""
    user_select = 5
    """Represents a user select component.

    .. versionadded:: 2.7
    """
    role_select = 6
    """Represents a role select component.

    .. versionadded:: 2.7
    """
    mentionable_select = 7
    """Represents a mentionable (user/member/role) select component.

    .. versionadded:: 2.7
    """
    channel_select = 8
    """Represents a channel select component.

    .. versionadded:: 2.7
    """

    def __int__(self) -> int:
        return self.value


class ButtonStyle(Enum):
    """Represents the style of the button component.

    .. versionadded:: 2.0
    """

    primary = 1
    """Represents a blurple button for the primary action."""
    secondary = 2
    """Represents a grey button for the secondary action."""
    success = 3
    """Represents a green button for a successful action."""
    danger = 4
    """Represents a red button for a dangerous action."""
    link = 5
    """Represents a link button."""

    # Aliases
    blurple = 1
    """An alias for :attr:`primary`."""
    grey = 2
    """An alias for :attr:`secondary`."""
    gray = 2
    """An alias for :attr:`secondary`."""
    green = 3
    """An alias for :attr:`success`."""
    red = 4
    """An alias for :attr:`danger`."""
    url = 5
    """An alias for :attr:`link`."""

    def __int__(self) -> int:
        return self.value


class TextInputStyle(Enum):
    """Represents a style of the text input component.

    .. versionadded:: 2.4
    """

    short = 1
    """Represents a single-line text input component."""
    paragraph = 2
    """Represents a multi-line text input component."""

    # Aliases
    single_line = 1
    """An alias for :attr:`short`."""
    multi_line = 2
    """An alias for :attr:`paragraph`."""
    long = 2
    """An alias for :attr:`paragraph`."""

    def __int__(self) -> int:
        return self.value


class SelectDefaultValueType(Enum):
    """Represents the type of a :class:`SelectDefaultValue`.

    .. versionadded:: 2.10
    """

    user = "user"
    """Represents a user/member."""
    role = "role"
    """Represents a role."""
    channel = "channel"
    """Represents a channel."""

    def __str__(self) -> str:
        return self.value


class ApplicationCommandType(Enum):
    """Represents the type of an application command.

    .. versionadded:: 2.1
    """

    chat_input = 1
    """Represents a slash command."""
    user = 2
    """Represents a user command from the context menu."""
    message = 3
    """Represents a message command from the context menu."""


class ApplicationCommandPermissionType(Enum):
    """Represents the type of a permission of an application command.

    .. versionadded:: 2.5
    """

    role = 1
    """Represents a permission that affects roles."""
    user = 2
    """Represents a permission that affects users."""
    channel = 3
    """Represents a permission that affects channels."""

    def __int__(self) -> int:
        return self.value


class OptionType(Enum):
    """Represents the type of an option.

    .. versionadded:: 2.1
    """

    sub_command = 1
    """Represents a sub command of the main command or group."""
    sub_command_group = 2
    """Represents a sub command group of the main command."""
    string = 3
    """Represents a string option."""
    integer = 4
    """Represents an integer option."""
    boolean = 5
    """Represents a boolean option."""
    user = 6
    """Represents a user option."""
    channel = 7
    """Represents a channel option."""
    role = 8
    """Represents a role option."""
    mentionable = 9
    """Represents a role + user option."""
    number = 10
    """Represents a float option."""
    attachment = 11
    """Represents an attachment option.

    .. versionadded:: 2.4
    """


class StagePrivacyLevel(Enum):
    """Represents a stage instance's privacy level.

    .. versionadded:: 2.0
    """

    public = 1
    """The stage instance can be joined by external users.

    .. deprecated:: 2.5
        Public stages are no longer supported by discord.
    """
    closed = 2
    """The stage instance can only be joined by members of the guild."""
    guild_only = 2
    """Alias for :attr:`.closed`"""


class NSFWLevel(Enum, comparable=True):
    """Represents the NSFW level of a guild.

    .. versionadded:: 2.0

    .. collapse:: operations

        .. describe:: x == y

            Checks if two NSFW levels are equal.
        .. describe:: x != y

            Checks if two NSFW levels are not equal.
        .. describe:: x > y

            Checks if an NSFW level is higher than another.
        .. describe:: x < y

            Checks if an NSFW level is lower than another.
        .. describe:: x >= y

            Checks if an NSFW level is higher or equal to another.
        .. describe:: x <= y

            Checks if an NSFW level is lower or equal to another.
    """

    default = 0
    """The guild has not been categorised yet."""
    explicit = 1
    """The guild contains NSFW content."""
    safe = 2
    """The guild does not contain any NSFW content."""
    age_restricted = 3
    """The guild may contain NSFW content."""


class GuildScheduledEventEntityType(Enum):
    """Represents the type of a guild scheduled event entity.

    .. versionadded:: 2.3
    """

    stage_instance = 1
    """The guild scheduled event will take place in a stage channel."""
    voice = 2
    """The guild scheduled event will take place in a voice channel."""
    external = 3
    """The guild scheduled event will take place in a custom location."""


class GuildScheduledEventStatus(Enum):
    """Represents the status of a guild scheduled event.

    .. versionadded:: 2.3
    """

    scheduled = 1
    """Represents a scheduled event."""
    active = 2
    """Represents an active event."""
    completed = 3
    """Represents a completed event."""
    canceled = 4
    """Represents a canceled event."""
    cancelled = 4
    """An alias for :attr:`canceled`.

    .. versionadded:: 2.6
    """


class GuildScheduledEventPrivacyLevel(Enum):
    """Represents the privacy level of a guild scheduled event.

    .. versionadded:: 2.3
    """

    guild_only = 2
    """The guild scheduled event is only for a specific guild."""


class ThreadArchiveDuration(Enum):
    """Represents the automatic archive duration of a thread in minutes.

    .. versionadded:: 2.3
    """

    hour = 60
    """The thread will archive after an hour of inactivity."""
    day = 1440
    """The thread will archive after a day of inactivity."""
    three_days = 4320
    """The thread will archive after three days of inactivity."""
    week = 10080
    """The thread will archive after a week of inactivity."""

    def __int__(self) -> int:
        return self.value


class WidgetStyle(Enum):
    """Represents the supported widget image styles.

    .. versionadded:: 2.5
    """

    shield = "shield"
    """A shield style image with a Discord icon and the online member count."""
    banner1 = "banner1"
    """A large image with guild icon, name and online member count and a footer."""
    banner2 = "banner2"
    """A small image with guild icon, name and online member count."""
    banner3 = "banner3"
    """A large image with guild icon, name and online member count and a footer,
    with a "Chat Now" label on the right.
    """
    banner4 = "banner4"
    """A large image with a large Discord logo, guild icon, name and online member count,
    with a "Join My Server" label at the bottom.
    """

    def __str__(self) -> str:
        return self.value


# reference: https://discord.com/developers/docs/reference#locales
class Locale(Enum):
    """Represents supported locales by Discord.

    .. versionadded:: 2.5
    """

    bg = "bg"
    """The ``bg`` (Bulgarian) locale."""
    cs = "cs"
    """The ``cs`` (Czech) locale."""
    da = "da"
    """The ``da`` (Danish) locale."""
    de = "de"
    """The ``de`` (German) locale."""
    el = "el"
    """The ``el`` (Greek) locale."""
    en_GB = "en-GB"
    """The ``en-GB`` (English, UK) locale."""
    en_US = "en-US"
    """The ``en-US`` (English, US) locale."""
    es_ES = "es-ES"
    """The ``es-ES`` (Spanish) locale."""
    es_LATAM = "es-419"
    """The ``es-419`` (Spanish, LATAM) locale.

    .. versionadded:: 2.10
    """
    fi = "fi"
    """The ``fi`` (Finnish) locale."""
    fr = "fr"
    """The ``fr`` (French) locale."""
    hi = "hi"
    """The ``hi`` (Hindi) locale."""
    hr = "hr"
    """The ``hr`` (Croatian) locale."""
    hu = "hu"
    """The ``hu`` (Hungarian) locale."""
    id = "id"
    """The ``id`` (Indonesian) locale.

    .. versionadded:: 2.8
    """
    it = "it"
    """The ``it`` (Italian) locale."""
    ja = "ja"
    """The ``ja`` (Japanese) locale."""
    ko = "ko"
    """The ``ko`` (Korean) locale."""
    lt = "lt"
    """The ``lt`` (Lithuanian) locale."""
    nl = "nl"
    """The ``nl`` (Dutch) locale."""
    no = "no"
    """The ``no`` (Norwegian) locale."""
    pl = "pl"
    """The ``pl`` (Polish) locale."""
    pt_BR = "pt-BR"
    """The ``pt-BR`` (Portuguese) locale."""
    ro = "ro"
    """The ``ro`` (Romanian) locale."""
    ru = "ru"
    """The ``ru`` (Russian) locale."""
    sv_SE = "sv-SE"
    """The ``sv-SE`` (Swedish) locale."""
    th = "th"
    """The ``th`` (Thai) locale."""
    tr = "tr"
    """The ``tr`` (Turkish) locale."""
    uk = "uk"
    """The ``uk`` (Ukrainian) locale."""
    vi = "vi"
    """The ``vi`` (Vietnamese) locale."""
    zh_CN = "zh-CN"
    """The ``zh-CN`` (Chinese, China) locale."""
    zh_TW = "zh-TW"
    """The ``zh-TW`` (Chinese, Taiwan) locale."""

    def __str__(self) -> str:
        return self.value


class AutoModActionType(Enum):
    """Represents the type of action an auto moderation rule will take upon execution.

    .. versionadded:: 2.6
    """

    block_message = 1
    """The rule will prevent matching messages from being posted."""
    send_alert_message = 2
    """The rule will send an alert to a specified channel."""
    timeout = 3
    """The rule will timeout the user that sent the message.

    .. note::
        This action type is only available for rules with trigger type
        :attr:`~AutoModTriggerType.keyword` or :attr:`~AutoModTriggerType.mention_spam`,
        and :attr:`~Permissions.moderate_members` permissions are required to use it.
    """


class AutoModEventType(Enum):
    """Represents the type of event/context an auto moderation rule will be checked in.

    .. versionadded:: 2.6
    """

    message_send = 1
    """The rule will apply when a member sends or edits a message in the guild."""


class AutoModTriggerType(Enum):
    """Represents the type of content that can trigger an auto moderation rule.

    .. versionadded:: 2.6

    .. versionchanged:: 2.9
        Removed obsolete ``harmful_link`` type.
    """

    keyword = 1
    """The rule will filter messages based on a custom keyword list.

    This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.
    """

    if not TYPE_CHECKING:
        harmful_link = 2  # obsolete/deprecated

    spam = 3
    """The rule will filter messages suspected of being spam."""
    keyword_preset = 4
    """The rule will filter messages based on predefined lists containing commonly flagged words.

    This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.
    """
    mention_spam = 5
    """The rule will filter messages based on the number of member/role mentions they contain.

    This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.
    """


class ThreadSortOrder(Enum):
    """Represents the sort order of threads in a :class:`ForumChannel` or :class:`MediaChannel`.

    .. versionadded:: 2.6
    """

    latest_activity = 0
    """Sort forum threads by activity."""
    creation_date = 1
    """Sort forum threads by creation date/time (from newest to oldest)."""


class ThreadLayout(Enum):
    """Represents the layout of threads in :class:`ForumChannel`\\s.

    .. versionadded:: 2.8
    """

    not_set = 0
    """No preferred layout has been set."""
    list_view = 1
    """Display forum threads in a text-focused list."""
    gallery_view = 2
    """Display forum threads in a media-focused collection of tiles."""


class Event(Enum):
    """
    Represents all the events of the library.

    These offer to register listeners/events in a more pythonic way; additionally autocompletion and documentation are both supported.

    .. versionadded:: 2.8
    """

    connect = "connect"
    """Called when the client has successfully connected to Discord.
    Represents the :func:`on_connect` event.
    """
    disconnect = "disconnect"
    """Called when the client has disconnected from Discord, or a connection attempt to Discord has failed.
    Represents the :func:`on_disconnect` event.
    """
    error = "error"
    """Called when an uncaught exception occurred.
    Represents the :func:`on_error` event.
    """
    gateway_error = "gateway_error"
    """Called when a known gateway event cannot be parsed.
    Represents the :func:`on_gateway_error` event.
    """
    ready = "ready"
    """Called when the client is done preparing the data received from Discord.
    Represents the :func:`on_ready` event.
    """
    resumed = "resumed"
    """Called when the client has resumed a session.
    Represents the :func:`on_resumed` event.
    """
    shard_connect = "shard_connect"
    """Called when a shard has successfully connected to Discord.
    Represents the :func:`on_shard_connect` event.
    """
    shard_disconnect = "shard_disconnect"
    """Called when a shard has disconnected from Discord.
    Represents the :func:`on_shard_disconnect` event.
    """
    shard_ready = "shard_ready"
    """Called when a shard has become ready.
    Represents the :func:`on_shard_ready` event.
    """
    shard_resumed = "shard_resumed"
    """Called when a shard has resumed a session.
    Represents the :func:`on_shard_resumed` event.
    """
    socket_event_type = "socket_event_type"
    """Called whenever a websocket event is received from the WebSocket.
    Represents the :func:`on_socket_event_type` event.
    """
    socket_raw_receive = "socket_raw_receive"
    """Called whenever a message is completely received from the WebSocket, before it's processed and parsed.
    Represents the :func:`on_socket_raw_receive` event.
    """
    socket_raw_send = "socket_raw_send"
    """Called whenever a send operation is done on the WebSocket before the message is sent.
    Represents the :func:`on_socket_raw_send` event.
    """
    guild_channel_create = "guild_channel_create"
    """Called whenever a guild channel is created.
    Represents the :func:`on_guild_channel_create` event.
    """
    guild_channel_update = "guild_channel_update"
    """Called whenever a guild channel is updated.
    Represents the :func:`on_guild_channel_update` event.
    """
    guild_channel_delete = "guild_channel_delete"
    """Called whenever a guild channel is deleted.
    Represents the :func:`on_guild_channel_delete` event.
    """
    guild_channel_pins_update = "guild_channel_pins_update"
    """Called whenever a message is pinned or unpinned from a guild channel.
    Represents the :func:`on_guild_channel_pins_update` event.
    """
    invite_create = "invite_create"
    """Called when an :class:`Invite` is created.
    Represents the :func:`.on_invite_create` event.
    """
    invite_delete = "invite_delete"
    """Called when an Invite is deleted.
    Represents the :func:`.on_invite_delete` event.
    """
    private_channel_update = "private_channel_update"
    """Called whenever a private group DM is updated.
    Represents the :func:`on_private_channel_update` event.
    """
    private_channel_pins_update = "private_channel_pins_update"
    """Called whenever a message is pinned or unpinned from a private channel.
    Represents the :func:`on_private_channel_pins_update` event.
    """
    webhooks_update = "webhooks_update"
    """Called whenever a webhook is created, modified, or removed from a guild channel.
    Represents the :func:`on_webhooks_update` event.
    """
    thread_create = "thread_create"
    """Called whenever a thread is created.
    Represents the :func:`on_thread_create` event.
    """
    thread_update = "thread_update"
    """Called when a thread is updated.
    Represents the :func:`on_thread_update` event.
    """
    thread_delete = "thread_delete"
    """Called when a thread is deleted.
    Represents the :func:`on_thread_delete` event.
    """
    thread_join = "thread_join"
    """Called whenever the bot joins a thread or gets access to a thread.
    Represents the :func:`on_thread_join` event.
    """
    thread_remove = "thread_remove"
    """Called whenever a thread is removed. This is different from a thread being deleted.
    Represents the :func:`on_thread_remove` event.
    """
    thread_member_join = "thread_member_join"
    """Called when a `ThreadMember` joins a `Thread`.
    Represents the :func:`on_thread_member_join` event.
    """
    thread_member_remove = "thread_member_remove"
    """Called when a `ThreadMember` leaves a `Thread`.
    Represents the :func:`on_thread_member_remove` event.
    """
    raw_thread_member_remove = "raw_thread_member_remove"
    """Called when a `ThreadMember` leaves `Thread` regardless of the thread member cache.
    Represents the :func:`on_raw_thread_member_remove` event.
    """
    raw_thread_update = "raw_thread_update"
    """Called whenever a thread is updated regardless of the state of the internal thread cache.
    Represents the :func:`on_raw_thread_update` event.
    """
    raw_thread_delete = "raw_thread_delete"
    """Called whenever a thread is deleted regardless of the state of the internal thread cache.
    Represents the :func:`on_raw_thread_delete` event.
    """
    guild_join = "guild_join"
    """Called when a `Guild` is either created by the `Client` or when the Client joins a guild.
    Represents the :func:`on_guild_join` event.
    """
    guild_remove = "guild_remove"
    """Called when a `Guild` is removed from the :class:`Client`.
    Represents the :func:`on_guild_remove` event.
    """
    guild_update = "guild_update"
    """Called when a `Guild` updates.
    Represents the :func:`on_guild_update` event.
    """
    guild_available = "guild_available"
    """Called when a guild becomes available.
    Represents the :func:`on_guild_available` event.
    """
    guild_unavailable = "guild_unavailable"
    """Called when a guild becomes unavailable.
    Represents the :func:`on_guild_unavailable` event.
    """
    guild_role_create = "guild_role_create"
    """Called when a `Guild` creates a new `Role`.
    Represents the :func:`on_guild_role_create` event.
    """
    guild_role_delete = "guild_role_delete"
    """Called when a `Guild` deletes a `Role`.
    Represents the :func:`on_guild_role_delete` event.
    """
    guild_role_update = "guild_role_update"
    """Called when a `Guild` updates a `Role`.
    Represents the :func:`on_guild_role_update` event.
    """
    guild_emojis_update = "guild_emojis_update"
    """Called when a `Guild` adds or removes `Emoji`.
    Represents the :func:`on_guild_emojis_update` event.
    """
    guild_stickers_update = "guild_stickers_update"
    """Called when a `Guild` updates its stickers.
    Represents the :func:`on_guild_stickers_update` event.
    """
    guild_soundboard_sounds_update = "guild_soundboard_sounds_update"
    """Called when a `Guild` updates its soundboard sounds.
    Represents the :func:`on_guild_soundboard_sounds_update` event.

    .. versionadded:: 2.10
    """
    guild_integrations_update = "guild_integrations_update"
    """Called whenever an integration is created, modified, or removed from a guild.
    Represents the :func:`on_guild_integrations_update` event.
    """
    guild_scheduled_event_create = "guild_scheduled_event_create"
    """Called when a guild scheduled event is created.
    Represents the :func:`on_guild_scheduled_event_create` event.
    """
    guild_scheduled_event_update = "guild_scheduled_event_update"
    """Called when a guild scheduled event is updated.
    Represents the :func:`on_guild_scheduled_event_update` event.
    """
    guild_scheduled_event_delete = "guild_scheduled_event_delete"
    """Called when a guild scheduled event is deleted.
    Represents the :func:`on_guild_scheduled_event_delete` event.
    """
    guild_scheduled_event_subscribe = "guild_scheduled_event_subscribe"
    """Called when a user subscribes from a guild scheduled event.
    Represents the :func:`on_guild_scheduled_event_subscribe` event.
    """
    guild_scheduled_event_unsubscribe = "guild_scheduled_event_unsubscribe"
    """Called when a user unsubscribes from a guild scheduled event.
    Represents the :func:`on_guild_scheduled_event_unsubscribe` event.
    """
    raw_guild_scheduled_event_subscribe = "raw_guild_scheduled_event_subscribe"
    """Called when a user subscribes from a guild scheduled event regardless of the guild scheduled event cache.
    Represents the :func:`on_raw_guild_scheduled_event_subscribe` event.
    """
    raw_guild_scheduled_event_unsubscribe = "raw_guild_scheduled_event_unsubscribe"
    """Called when a user subscribes to or unsubscribes from a guild scheduled event regardless of the guild scheduled event cache.
    Represents the :func:`on_raw_guild_scheduled_event_unsubscribe` event.
    """
    application_command_permissions_update = "application_command_permissions_update"
    """Called when the permissions of an application command or the application-wide command permissions are updated.
    Represents the :func:`on_application_command_permissions_update` event.
    """
    automod_action_execution = "automod_action_execution"
    """Called when an auto moderation action is executed due to a rule triggering for a particular event.
    Represents the :func:`on_automod_action_execution` event.
    """
    automod_rule_create = "automod_rule_create"
    """Called when an `AutoModRule` is created.
    Represents the :func:`on_automod_rule_create` event.
    """
    automod_rule_update = "automod_rule_update"
    """Called when an `AutoModRule` is updated.
    Represents the :func:`on_automod_rule_update` event.
    """
    automod_rule_delete = "automod_rule_delete"
    """Called when an `AutoModRule` is deleted.
    Represents the :func:`on_automod_rule_delete` event.
    """
    audit_log_entry_create = "audit_log_entry_create"
    """Called when an audit log entry is created.
    Represents the :func:`on_audit_log_entry_create` event.
    """
    integration_create = "integration_create"
    """Called when an integration is created.
    Represents the :func:`on_integration_create` event.
    """
    integration_update = "integration_update"
    """Called when an integration is updated.
    Represents the :func:`on_integration_update` event.
    """
    raw_integration_delete = "raw_integration_delete"
    """Called when an integration is deleted.
    Represents the :func:`on_raw_integration_delete` event.
    """
    member_join = "member_join"
    """Called when a `Member` joins a `Guild`.
    Represents the :func:`on_member_join` event.
    """
    member_remove = "member_remove"
    """Called when a `Member` leaves a `Guild`.
    Represents the :func:`on_member_remove` event.
    """
    member_update = "member_update"
    """Called when a `Member` is updated in a `Guild`.
    Represents the :func:`on_member_update` event.
    """
    raw_member_remove = "raw_member_remove"
    """Called when a member leaves a `Guild` regardless of the member cache.
    Represents the :func:`on_raw_member_remove` event.
    """
    raw_member_update = "raw_member_update"
    """Called when a `Member` is updated in a `Guild` regardless of the member cache.
    Represents the :func:`on_raw_member_update` event.
    """
    member_ban = "member_ban"
    """Called when user gets banned from a `Guild`.
    Represents the :func:`on_member_ban` event.
    """
    member_unban = "member_unban"
    """Called when a `User` gets unbanned from a `Guild`.
    Represents the :func:`on_member_unban` event.
    """
    presence_update = "presence_update"
    """Called when a `Member` updates their presence.
    Represents the :func:`on_presence_update` event.
    """
    user_update = "user_update"
    """Called when a `User` is updated.
    Represents the :func:`on_user_update` event.
    """
    voice_state_update = "voice_state_update"
    """Called when a `Member` changes their `VoiceState`.
    Represents the :func:`on_voice_state_update` event.
    """
    voice_channel_effect = "voice_channel_effect"
    """Called when a `Member` sends an effect in a voice channel the bot is connected to.
    Represents the :func:`on_voice_channel_effect` event.

    .. versionadded:: 2.10
    """
    raw_voice_channel_effect = "raw_voice_channel_effect"
    """Called when a `Member` sends an effect in a voice channel the bot is connected to,
    regardless of the member cache.
    Represents the :func:`on_raw_voice_channel_effect` event.

    .. versionadded:: 2.10
    """
    stage_instance_create = "stage_instance_create"
    """Called when a `StageInstance` is created for a `StageChannel`.
    Represents the :func:`on_stage_instance_create` event.
    """
    stage_instance_delete = "stage_instance_delete"
    """Called when a `StageInstance` is deleted for a `StageChannel`.
    Represents the :func:`on_stage_instance_delete` event.
    """
    stage_instance_update = "stage_instance_update"
    """Called when a `StageInstance` is updated.
    Represents the :func:`on_stage_instance_update` event.
    """
    application_command = "application_command"
    """Called when an application command is invoked.
    Represents the :func:`on_application_command` event.
    """
    application_command_autocomplete = "application_command_autocomplete"
    """Called when an application command autocomplete is called.
    Represents the :func:`on_application_command_autocomplete` event.
    """
    button_click = "button_click"
    """Called when a button is clicked.
    Represents the :func:`on_button_click` event.
    """
    dropdown = "dropdown"
    """Called when a select menu is clicked.
    Represents the :func:`on_dropdown` event.
    """
    interaction = "interaction"
    """Called when an interaction happened.
    Represents the :func:`on_interaction` event.
    """
    message_interaction = "message_interaction"
    """Called when a message interaction happened.
    Represents the :func:`on_message_interaction` event.
    """
    modal_submit = "modal_submit"
    """Called when a modal is submitted.
    Represents the :func:`on_modal_submit` event.
    """
    message = "message"
    """Called when a `Message` is created and sent.
    Represents the :func:`on_message` event.
    """
    message_edit = "message_edit"
    """Called when a `Message` receives an update event.
    Represents the :func:`on_message_edit` event.
    """
    message_delete = "message_delete"
    """Called when a message is deleted.
    Represents the :func:`on_message_delete` event.
    """
    bulk_message_delete = "bulk_message_delete"
    """Called when messages are bulk deleted.
    Represents the :func:`on_bulk_message_delete` event.
    """
    poll_vote_add = "poll_vote_add"
    """Called when a vote is added on a `Poll`.
    Represents the :func:`on_poll_vote_add` event.
    """
    poll_vote_remove = "poll_vote_remove"
    """Called when a vote is removed from a `Poll`.
    Represents the :func:`on_poll_vote_remove` event.
    """
    raw_message_edit = "raw_message_edit"
    """Called when a message is edited regardless of the state of the internal message cache.
    Represents the :func:`on_raw_message_edit` event.
    """
    raw_message_delete = "raw_message_delete"
    """Called when a message is deleted regardless of the message being in the internal message cache or not.
    Represents the :func:`on_raw_message_delete` event.
    """
    raw_bulk_message_delete = "raw_bulk_message_delete"
    """Called when a bulk delete is triggered regardless of the messages being in the internal message cache or not.
    Represents the :func:`on_raw_bulk_message_delete` event.
    """
    raw_poll_vote_add = "raw_poll_vote_add"
    """Called when a vote is added on a `Poll` regardless of the internal message cache.
    Represents the :func:`on_raw_poll_vote_add` event.
    """
    raw_poll_vote_remove = "raw_poll_vote_remove"
    """Called when a vote is removed from a `Poll` regardless of the internal message cache.
    Represents the :func:`on_raw_poll_vote_remove` event.
    """
    reaction_add = "reaction_add"
    """Called when a message has a reaction added to it.
    Represents the :func:`on_reaction_add` event.
    """
    reaction_remove = "reaction_remove"
    """Called when a message has a reaction removed from it.
    Represents the :func:`on_reaction_remove` event.
    """
    reaction_clear = "reaction_clear"
    """Called when a message has all its reactions removed from it.
    Represents the :func:`on_reaction_clear` event.
    """
    reaction_clear_emoji = "reaction_clear_emoji"
    """Called when a message has a specific reaction removed from it.
    Represents the :func:`on_reaction_clear_emoji` event.
    """
    raw_presence_update = "raw_presence_update"
    """Called when a user's presence changes regardless of the state of the internal member cache.
    Represents the :func:`on_raw_presence_update` event.
    """
    raw_reaction_add = "raw_reaction_add"
    """Called when a message has a reaction added regardless of the state of the internal message cache.
    Represents the :func:`on_raw_reaction_add` event.
    """
    raw_reaction_remove = "raw_reaction_remove"
    """Called when a message has a reaction removed regardless of the state of the internal message cache.
    Represents the :func:`on_raw_reaction_remove` event.
    """
    raw_reaction_clear = "raw_reaction_clear"
    """Called when a message has all its reactions removed regardless of the state of the internal message cache.
    Represents the :func:`on_raw_reaction_clear` event.
    """
    raw_reaction_clear_emoji = "raw_reaction_clear_emoji"
    """Called when a message has a specific reaction removed from it regardless of the state of the internal message cache.
    Represents the :func:`on_raw_reaction_clear_emoji` event.
    """
    typing = "typing"
    """Called when someone begins typing a message.
    Represents the :func:`on_typing` event.
    """
    raw_typing = "raw_typing"
    """Called when someone begins typing a message regardless of whether `Intents.members` and `Intents.guilds` are enabled.
    Represents the :func:`on_raw_typing` event.
    """
    entitlement_create = "entitlement_create"
    """Called when a user subscribes to an SKU, creating a new :class:`Entitlement`.
    Represents the :func:`on_entitlement_create` event.

    .. versionadded:: 2.10
    """
    entitlement_update = "entitlement_update"
    """Called when a user's subscription renews.
    Represents the :func:`on_entitlement_update` event.

    .. versionadded:: 2.10
    """
    entitlement_delete = "entitlement_delete"
    """Called when a user's entitlement is deleted.
    Represents the :func:`on_entitlement_delete` event."""
    subscription_create = "subscription_create"
    """Called when a subscription for a premium app is created.
    Represents the :func:`on_subscription_create` event.

    .. versionadded:: 2.10
    """
    subscription_update = "subscription_update"
    """Called when a subscription for a premium app is updated.
    Represents the :func:`on_subscription_update` event.

    .. versionadded:: 2.10
    """
    subscription_delete = "subscription_delete"
    """Called when a subscription for a premium app is deleted.
    Represents the :func:`on_subscription_delete` event.

    .. versionadded:: 2.10
    """
    # ext.commands events
    command = "command"
    """Called when a command is found and is about to be invoked.
    Represents the :func:`.on_command` event.
    """
    command_completion = "command_completion"
    """Called when a command has completed its invocation.
    Represents the :func:`.on_command_completion` event.
    """
    command_error = "command_error"
    """Called when an error is raised inside a command either through user input error, check failure, or an error in your own code.
    Represents the :func:`.on_command_error` event.
    """
    slash_command = "slash_command"
    """Called when a slash command is found and is about to be invoked.
    Represents the :func:`.on_slash_command` event.
    """
    slash_command_completion = "slash_command_completion"
    """Called when a slash command has completed its invocation.
    Represents the :func:`.on_slash_command_completion` event.
    """
    slash_command_error = "slash_command_error"
    """Called when an error is raised inside a slash command either through user input error, check failure, or an error in your own code.
    Represents the :func:`.on_slash_command_error` event.
    """
    user_command = "user_command"
    """Called when a user command is found and is about to be invoked.
    Represents the :func:`.on_user_command` event.
    """
    user_command_completion = "user_command_completion"
    """Called when a user command has completed its invocation.
    Represents the :func:`.on_user_command_completion` event.
    """
    user_command_error = "user_command_error"
    """Called when an error is raised inside a user command either through check failure, or an error in your own code.
    Represents the :func:`.on_user_command_error` event.
    """
    message_command = "message_command"
    """Called when a message command is found and is about to be invoked.
    Represents the :func:`.on_message_command` event.
    """
    message_command_completion = "message_command_completion"
    """Called when a message command has completed its invocation.
    Represents the :func:`.on_message_command_completion` event.
    """
    message_command_error = "message_command_error"
    """Called when an error is raised inside a message command either through check failure, or an error in your own code.
    Represents the :func:`.on_message_command_error` event.
    """


class ApplicationRoleConnectionMetadataType(Enum):
    """Represents the type of a role connection metadata value.

    These offer comparison operations, which allow guilds to configure role requirements
    based on the metadata value for each user and a guild-specified configured value.

    .. versionadded:: 2.8
    """

    integer_less_than_or_equal = 1
    """The metadata value (``integer``) is less than or equal to the guild's configured value."""
    integer_greater_than_or_equal = 2
    """The metadata value (``integer``) is greater than or equal to the guild's configured value."""
    integer_equal = 3
    """The metadata value (``integer``) is equal to the guild's configured value."""
    integer_not_equal = 4
    """The metadata value (``integer``) is not equal to the guild's configured value."""
    datetime_less_than_or_equal = 5
    """The metadata value (``ISO8601 string``) is less than or equal to the guild's configured value (``integer``; days before current date)."""
    datetime_greater_than_or_equal = 6
    """The metadata value (``ISO8601 string``) is greater than or equal to the guild's configured value (``integer``; days before current date)."""
    boolean_equal = 7
    """The metadata value (``integer``) is equal to the guild's configured value."""
    boolean_not_equal = 8
    """The metadata value (``integer``) is not equal to the guild's configured value."""


class OnboardingPromptType(Enum):
    """Represents the type of onboarding prompt.

    .. versionadded:: 2.9
    """

    multiple_choice = 0
    """The prompt is a multiple choice prompt."""
    dropdown = 1
    """The prompt is a dropdown prompt."""


class SKUType(Enum):
    """Represents the type of an SKU.

    .. versionadded:: 2.10
    """

    durable = 2
    """Represents a durable one-time purchase."""
    consumable = 3
    """Represents a consumable one-time purchase."""
    subscription = 5
    """Represents a recurring subscription."""
    subscription_group = 6
    """Represents a system-generated group for each :attr:`subscription` SKU."""


class EntitlementType(Enum):
    """Represents the type of an entitlement.

    .. versionadded:: 2.10
    """

    purchase = 1
    """Represents an entitlement purchased by a user."""
    premium_subscription = 2
    """Represents an entitlement for a Discord Nitro subscription."""
    developer_gift = 3
    """Represents an entitlement gifted by the application developer."""
    test_mode_purchase = 4
    """Represents an entitlement purchased by a developer in application test mode."""
    free_purchase = 5
    """Represents an entitlement granted when the SKU was free."""
    user_gift = 6
    """Represents an entitlement gifted by another user."""
    premium_purchase = 7
    """Represents an entitlement claimed by a user for free as a Discord Nitro subscriber."""
    application_subscription = 8
    """Represents an entitlement for an application subscription."""


class SubscriptionStatus(Enum):
    """Represents the status of a subscription.

    .. versionadded:: 2.10
    """

    active = 0
    """Represents an active Subscription which is scheduled to renew."""
    ending = 1
    """Represents an active Subscription which will not renew."""
    inactive = 2
    """Represents an inactive Subscription which is not being charged."""


class PollLayoutType(Enum):
    """Specifies the layout of a :class:`Poll`.

    .. versionadded:: 2.10
    """

    default = 1
    """The default poll layout type."""


class VoiceChannelEffectAnimationType(Enum):
    """The type of an emoji reaction effect animation in a voice channel.

    .. versionadded:: 2.10
    """

    premium = 0
    """A fun animation, sent by a Nitro subscriber."""
    basic = 1
    """A standard animation."""


class MessageReferenceType(Enum):
    """Specifies the type of :class:`MessageReference`. This can be used to determine
    if a message is e.g. a reply or a forwarded message.

    .. versionadded:: 2.10
    """

    default = 0
    """A standard message reference used in message replies."""
    forward = 1
    """Reference used to point to a message at a point in time (forward)."""


T = TypeVar("T")


def create_unknown_value(cls: Type[T], val: Any) -> T:
    value_cls = cls._enum_value_cls_  # type: ignore
    name = f"unknown_{val}"
    return value_cls(name=name, value=val)


def try_enum(cls: Type[T], val: Any) -> T:
    """A function that tries to turn the value into enum ``cls``.

    If it fails it returns a proxy invalid value instead.
    """
    try:
        return cls._enum_value_map_[val]  # type: ignore
    except (KeyError, TypeError, AttributeError):
        return create_unknown_value(cls, val)


def enum_if_int(cls: Type[T], val: Any) -> T:
    """A function that tries to turn the value into enum ``cls``.

    If it fails it returns a proxy invalid value instead.
    """
    if not isinstance(val, int):
        return val
    return try_enum(cls, val)


def try_enum_to_int(val: Any) -> Any:
    if isinstance(val, int):
        return val
    try:
        return val.value
    except Exception:
        return val
