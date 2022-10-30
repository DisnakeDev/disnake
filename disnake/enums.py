# SPDX-License-Identifier: MIT

import types
from functools import total_ordering
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, NamedTuple, Optional, Type, TypeVar

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
    "WebhookType",
    "ExpireBehaviour",
    "ExpireBehavior",
    "StickerType",
    "StickerFormatType",
    "InviteTarget",
    "VideoQualityMode",
    "ComponentType",
    "ButtonStyle",
    "TextInputStyle",
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

    def __new__(cls, name, bases, attrs, *, comparable: bool = False):
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

    def __iter__(cls):
        return (cls._enum_member_map_[name] for name in cls._enum_member_names_)

    def __reversed__(cls):
        return (cls._enum_member_map_[name] for name in reversed(cls._enum_member_names_))

    def __len__(cls):
        return len(cls._enum_member_names_)

    def __repr__(cls):
        return f"<enum {cls.__name__}>"

    @property
    def __members__(cls):
        return types.MappingProxyType(cls._enum_member_map_)

    def __call__(cls, value):
        try:
            return cls._enum_value_map_[value]
        except (KeyError, TypeError):
            raise ValueError(f"{value!r} is not a valid {cls.__name__}")

    def __getitem__(cls, key):
        return cls._enum_member_map_[key]

    def __setattr__(cls, name, value):
        raise TypeError("Enums are immutable.")

    def __delattr__(cls, attr):
        raise TypeError("Enums are immutable")

    def __instancecheck__(self, instance):
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
    text = 0
    private = 1
    voice = 2
    group = 3
    category = 4
    news = 5
    news_thread = 10
    public_thread = 11
    private_thread = 12
    stage_voice = 13
    guild_directory = 14
    forum = 15

    def __str__(self):
        return self.name


class MessageType(Enum):
    default = 0
    recipient_add = 1
    recipient_remove = 2
    call = 3
    channel_name_change = 4
    channel_icon_change = 5
    pins_add = 6
    new_member = 7
    premium_guild_subscription = 8
    premium_guild_tier_1 = 9
    premium_guild_tier_2 = 10
    premium_guild_tier_3 = 11
    channel_follow_add = 12
    guild_stream = 13
    guild_discovery_disqualified = 14
    guild_discovery_requalified = 15
    guild_discovery_grace_period_initial_warning = 16
    guild_discovery_grace_period_final_warning = 17
    thread_created = 18
    reply = 19
    application_command = 20
    thread_starter_message = 21
    guild_invite_reminder = 22
    context_menu_command = 23
    auto_moderation_action = 24


class PartyType(Enum):
    poker = 755827207812677713
    betrayal = 773336526917861400
    fishing = 814288819477020702
    chess = 832012774040141894
    letter_tile = 879863686565621790
    word_snack = 879863976006127627
    doodle_crew = 878067389634314250
    checkers = 832013003968348200
    spellcast = 852509694341283871
    watch_together = 880218394199220334
    sketch_heads = 902271654783242291
    ocho = 832025144389533716


class SpeakingState(Enum):
    none = 0
    voice = 1
    soundshare = 2
    priority = 4

    def __str__(self):
        return self.name

    def __int__(self):
        return self.value


class VerificationLevel(Enum, comparable=True):
    none = 0
    low = 1
    medium = 2
    high = 3
    highest = 4

    def __str__(self):
        return self.name


class ContentFilter(Enum, comparable=True):
    disabled = 0
    no_role = 1
    all_members = 2

    def __str__(self):
        return self.name


class Status(Enum):
    online = "online"
    offline = "offline"
    idle = "idle"
    dnd = "dnd"
    do_not_disturb = "dnd"
    invisible = "invisible"
    streaming = "streaming"

    def __str__(self):
        return self.value


class DefaultAvatar(Enum):
    blurple = 0
    grey = 1
    gray = 1
    green = 2
    orange = 3
    red = 4

    def __str__(self):
        return self.name


class NotificationLevel(Enum, comparable=True):
    all_messages = 0
    only_mentions = 1


class AuditLogActionCategory(Enum):
    create = 1
    delete = 2
    update = 3


class AuditLogAction(Enum):
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
    automod_rule_create                   = 140
    automod_rule_update                   = 141
    automod_rule_delete                   = 142
    automod_block_message                 = 143
    automod_send_alert_message            = 144
    automod_timeout                       = 145
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
            AuditLogAction.automod_rule_create:                   AuditLogActionCategory.create,
            AuditLogAction.automod_rule_update:                   AuditLogActionCategory.update,
            AuditLogAction.automod_rule_delete:                   AuditLogActionCategory.delete,
            AuditLogAction.automod_block_message:                 None,
            AuditLogAction.automod_send_alert_message:            None,
            AuditLogAction.automod_timeout:                       None,
        }
        # fmt: on
        return lookup[self]

    @property
    def target_type(self) -> Optional[str]:
        v = self.value
        if v == -1:
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
        else:
            return None


class UserFlags(Enum):
    staff = 1
    partner = 2
    hypesquad = 4
    bug_hunter = 8
    mfa_sms = 16
    premium_promo_dismissed = 32
    hypesquad_bravery = 64
    hypesquad_brilliance = 128
    hypesquad_balance = 256
    early_supporter = 512
    team_user = 1024
    system = 4096
    has_unread_urgent_messages = 8192
    bug_hunter_level_2 = 16384
    verified_bot = 65536
    verified_bot_developer = 131072
    discord_certified_moderator = 262144
    http_interactions_bot = 524288
    spammer = 1048576


class ActivityType(Enum):
    unknown = -1
    playing = 0
    streaming = 1
    listening = 2
    watching = 3
    custom = 4
    competing = 5

    def __int__(self):
        return self.value


class TeamMembershipState(Enum):
    invited = 1
    accepted = 2


class WebhookType(Enum):
    incoming = 1
    channel_follower = 2
    application = 3


class ExpireBehaviour(Enum):
    remove_role = 0
    kick = 1


ExpireBehavior = ExpireBehaviour


class StickerType(Enum):
    standard = 1
    guild = 2


class StickerFormatType(Enum):
    png = 1
    apng = 2
    lottie = 3

    @property
    def file_extension(self) -> str:
        lookup: Dict[StickerFormatType, str] = {
            StickerFormatType.png: "png",
            StickerFormatType.apng: "png",
            StickerFormatType.lottie: "json",
        }
        return lookup[self]


class InviteTarget(Enum):
    unknown = 0
    stream = 1
    embedded_application = 2


class InteractionType(Enum):
    ping = 1
    application_command = 2
    component = 3
    application_command_autocomplete = 4
    modal_submit = 5


class InteractionResponseType(Enum):
    pong = 1
    # ack = 2 (deprecated)
    # channel_message = 3 (deprecated)
    channel_message = 4  # (with source)
    deferred_channel_message = 5  # (with source)
    deferred_message_update = 6  # for components
    message_update = 7  # for components
    application_command_autocomplete_result = 8  # for autocomplete
    modal = 9  # for modals


class VideoQualityMode(Enum):
    auto = 1
    full = 2

    def __int__(self):
        return self.value


class ComponentType(Enum):
    action_row = 1
    button = 2
    string_select = 3
    select = string_select  # backwards compatibility
    text_input = 4
    user_select = 5
    role_select = 6
    mentionable_select = 7
    channel_select = 8

    def __int__(self):
        return self.value


class ButtonStyle(Enum):
    primary = 1
    secondary = 2
    success = 3
    danger = 4
    link = 5

    # Aliases
    blurple = 1
    grey = 2
    gray = 2
    green = 3
    red = 4
    url = 5

    def __int__(self):
        return self.value


class TextInputStyle(Enum):
    short = 1
    paragraph = 2
    # Aliases
    single_line = 1
    multi_line = 2
    long = 2

    def __int__(self) -> int:
        return self.value


class ApplicationCommandType(Enum):
    chat_input = 1
    user = 2
    message = 3


class ApplicationCommandPermissionType(Enum):
    role = 1
    user = 2
    channel = 3

    def __int__(self):
        return self.value


class OptionType(Enum):
    sub_command = 1
    sub_command_group = 2
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8
    mentionable = 9
    number = 10
    attachment = 11


class StagePrivacyLevel(Enum):
    public = 1
    closed = 2
    guild_only = 2


class NSFWLevel(Enum, comparable=True):
    default = 0
    explicit = 1
    safe = 2
    age_restricted = 3


class GuildScheduledEventEntityType(Enum):
    stage_instance = 1
    voice = 2
    external = 3


class GuildScheduledEventStatus(Enum):
    scheduled = 1
    active = 2
    completed = 3
    canceled = 4
    cancelled = 4


class GuildScheduledEventPrivacyLevel(Enum):
    guild_only = 2


class ThreadArchiveDuration(Enum):
    hour = 60
    day = 1440
    three_days = 4320
    week = 10080

    def __int__(self):
        return self.value


class WidgetStyle(Enum):
    shield = "shield"
    banner1 = "banner1"
    banner2 = "banner2"
    banner3 = "banner3"
    banner4 = "banner4"

    def __str__(self):
        return self.value


# reference: https://discord.com/developers/docs/reference#locales
class Locale(Enum):
    bg = "bg"
    "Bulgarian | български"
    cs = "cs"
    "Czech | Čeština"
    da = "da"
    "Danish | Dansk"
    de = "de"
    "German | Deutsch"
    el = "el"
    "Greek | Ελληνικά"
    en_GB = "en-GB"
    "English, UK | English, UK"
    en_US = "en-US"
    "English, US | English, US"
    es_ES = "es-ES"
    "Spanish | Español"
    fi = "fi"
    "Finnish | Suomi"
    fr = "fr"
    "French | Français"
    hi = "hi"
    "Hindi | हिन्दी"
    hr = "hr"
    "Croatian | Hrvatski"
    it = "it"
    "Italian | Italiano"
    ja = "ja"
    "Japanese | 日本語"
    ko = "ko"
    "Korean | 한국어"
    lt = "lt"
    "Lithuanian | Lietuviškai"
    hu = "hu"
    "Hungarian | Magyar"
    nl = "nl"
    "Dutch | Nederlands"
    no = "no"
    "Norwegian | Norsk"
    pl = "pl"
    "Polish | Polski"
    pt_BR = "pt-BR"
    "Portuguese, Brazilian | Português do Brasil"
    ro = "ro"
    "Romanian, Romania | Română"
    ru = "ru"
    "Russian | Pусский"
    sv_SE = "sv-SE"
    "Swedish | Svenska"
    th = "th"
    "Thai | ไทย"
    tr = "tr"
    "Turkish | Türkçe"
    uk = "uk"
    "Ukrainian | Українська"
    vi = "vi"
    "Vietnamese | Tiếng Việt"
    zh_CN = "zh-CN"
    "Chinese, China | 中文"
    zh_TW = "zh-TW"
    "Chinese, Taiwan | 繁體中文"

    def __str__(self):
        return self.value


class AutoModActionType(Enum):
    block_message = 1
    send_alert_message = 2
    timeout = 3


class AutoModEventType(Enum):
    message_send = 1


class AutoModTriggerType(Enum):
    keyword = 1
    harmful_link = 2
    spam = 3
    keyword_preset = 4
    mention_spam = 5


class ThreadSortOrder(Enum):
    latest_activity = 0
    creation_date = 1


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
