"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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

import types
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Iterator, Mapping, Optional, Sequence, Tuple, Type, TypeVar, Union

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
)


_T = TypeVar("_T", bound="EnumMeta")


def _is_descriptor(obj):
    return hasattr(obj, "__get__") or hasattr(obj, "__set__") or hasattr(obj, "__delete__")


class _EnumDict(Dict[str, Any]):

    def __init__(self, base: Type[Any]):
        # We explicitly take a base in __init__, unlike default Enums, to more easily
        # enforce proper value typing. This should ensure better performance, as e.g.
        # `Enum[int].one + 3 == 4` is more performant than `Enum[Any].one.value + 3 == 4`,
        # as this saves a lookup. We do lose some functionality here, but it's probably
        # worth the cost; especially considering all current enums have monotyped values.
        super().__init__()
        self.base = base
        self.member_map: Dict[str, Any] = {}
        self.value_map: Dict[Any, str] = {}

    def __getitem__(self, name: str) -> Any:
        try:
            return super().__getitem__(name)
        except KeyError:
            return self.value_map[name]

    def __setitem__(self, name: str, value: Any) -> None:
        if name in {"mro", ""}:  # illegal names defined in original python enums
            raise ValueError(f"Invalid Enum member name: {name}")

        if name.startswith("_") or _is_descriptor(value):
            super().__setitem__(name, value)
            return

        if not isinstance(value, self.base):
            raise TypeError(
                f"Member {name} must be of type {self.base.__name__}, got {type(value).__name__}"
            )

        if name in self.member_map:
            raise TypeError(f"Attempted to reuse key: '{name!r}'")
        if value in self.value_map:
            # We'll have to settle for slower value lookup in case of a dupe
            self.member_map[name] = value
            return

        self.member_map[name] = value
        self.value_map[value] = name


class EnumMeta(type):
    __is_enum_instantiated: ClassVar[bool] = False

    _name_map_: ClassVar[Mapping[str, Enum]]
    _value2member_map_: ClassVar[Mapping[Any, Enum]]

    def __new__(
        metacls: Type[_T],  # pyright: reportSelfClsParameterName=false
        name: str,
        bases: Tuple[Type[Any], Type[Any]],
        namespace: _EnumDict
    ) -> _T:
        
        if not EnumMeta.__is_enum_instantiated:
            EnumMeta.__is_enum_instantiated = True
            return super().__new__(metacls, name, bases, namespace)

        base, enum_type = bases  # ensured possible in __prepare__

        ns: Dict[str, Any] = {
            "__objtype__": base,
            "__enumtype__": enum_type,
            "_name_map_" : (name_map := {}),
            "_value2member_map_": (value_map := {}),
            **{
                name_: value_
                for name_, value_ in Enum.__dict__.items()
                if name_ not in ("__class__", "__module__", "__doc__")
            }
        }

        ns.update(namespace)

        cls = super().__new__(metacls, name, bases, ns)

        for name_, value_ in namespace.member_map.items():
            member = cls.__new__(cls, value_)  # type: ignore
            member._name_ = name_
            member._value_ = value_
            name_map[name_] = value_map[value_] = member
            setattr(cls, name_, member)

        return cls

    @classmethod
    def __prepare__(
        metacls, name: str, bases: Tuple[Type[Any], ...] = (), /, **kwds: Any
    ) -> Union[Dict[str, Any], _EnumDict]:
        # with this we get to ensure the new class' namespace is an _EnumDict

        if not EnumMeta.__is_enum_instantiated:
            return _EnumDict(object)

        try:
            base, _ = bases  # 'loss' of functionality: only (type, Enum) enums are allowed
        except ValueError:
            raise TypeError("Expected exactly two base classes for an enum") from None

        if isinstance(base, EnumMeta):
            raise TypeError("An Enum's first base class must be its values' type")

        return _EnumDict(base)

    def __repr__(cls) -> str:
        return f"<enum {cls.__name__}>"

    def __call__(cls, value: Any) -> Any:
        try:
            return cls._value2member_map_[value]
        except KeyError:
            raise KeyError(f"{value} is not a valid {cls.__name__}") from None

    def __getitem__(cls, name: str) -> Any:
        return cls._name_map_[name]

    def __contains__(cls, value: Any) -> bool:
        return value in cls._value2member_map_

    def __iter__(cls) -> Iterator[Any]:
        yield from cls._name_map_.values()


if TYPE_CHECKING:
    from enum import Enum
else:

    class Enum(metaclass=EnumMeta):
        _name_map_: ClassVar[Mapping[str, Enum]]
        _value2member_map_: ClassVar[Mapping[Any, Enum]]
        _name_: str
        _value_: Any

        @property
        def name(self) -> str:
            """Return the name of the enum member as a `builtins.str`."""
            return self._name_

        @property
        def value(self):
            """Return the value of the enum member."""
            return self._value_

        # The rest is just to remain compatible with vanilla Enum API

        @classmethod
        @property
        def __members__(cls) -> types.MappingProxyType[str, Enum]:
            return types.MappingProxyType(cls._name_map_)

        @classmethod
        @property
        def _member_names_(cls) -> Sequence[str]:
            # I *think* this should be fine as a property?
            # Hardly ever gets used so I don't really see the value in pre-computing it like
            # vanilla Enums do. I decided to save memory but we can always just revert this.
            return tuple(cls._name_map_)

        def __repr__(self) -> str:
            return f"<{type(self).__name__}.{self._name_}: {self._value_!r}>"

        def __str__(self) -> str:
            return self._name_


class ChannelType(int, Enum):
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


class MessageType(int, Enum):
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


class PartyType(int, Enum):
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


class SpeakingState(int, Enum):
    none = 0
    voice = 1
    soundshare = 2
    priority = 4


class VerificationLevel(int, Enum):
    none = 0
    low = 1
    medium = 2
    high = 3
    highest = 4


class ContentFilter(int, Enum):
    disabled = 0
    no_role = 1
    all_members = 2


class Status(str, Enum):
    online = "online"
    offline = "offline"
    idle = "idle"
    dnd = "dnd"
    do_not_disturb = "dnd"
    invisible = "invisible"
    streaming = "streaming"


class DefaultAvatar(int, Enum):
    blurple = 0
    grey = 1
    gray = 1
    green = 2
    orange = 3
    red = 4


class NotificationLevel(int, Enum):
    all_messages = 0
    only_mentions = 1


class AuditLogActionCategory(int, Enum):
    create = 1
    delete = 2
    update = 3


class AuditLogAction(int, Enum):
    # fmt: off
    guild_update                     = 1
    channel_create                   = 10
    channel_update                   = 11
    channel_delete                   = 12
    overwrite_create                 = 13
    overwrite_update                 = 14
    overwrite_delete                 = 15
    kick                             = 20
    member_prune                     = 21
    ban                              = 22
    unban                            = 23
    member_update                    = 24
    member_role_update               = 25
    member_move                      = 26
    member_disconnect                = 27
    bot_add                          = 28
    role_create                      = 30
    role_update                      = 31
    role_delete                      = 32
    invite_create                    = 40
    invite_update                    = 41
    invite_delete                    = 42
    webhook_create                   = 50
    webhook_update                   = 51
    webhook_delete                   = 52
    emoji_create                     = 60
    emoji_update                     = 61
    emoji_delete                     = 62
    message_delete                   = 72
    message_bulk_delete              = 73
    message_pin                      = 74
    message_unpin                    = 75
    integration_create               = 80
    integration_update               = 81
    integration_delete               = 82
    stage_instance_create            = 83
    stage_instance_update            = 84
    stage_instance_delete            = 85
    sticker_create                   = 90
    sticker_update                   = 91
    sticker_delete                   = 92
    guild_scheduled_event_create     = 100
    guild_scheduled_event_update     = 101
    guild_scheduled_event_delete     = 102
    thread_create                    = 110
    thread_update                    = 111
    thread_delete                    = 112
    application_command_permission_update = 121
    # fmt: on

    @property
    def category(self) -> Optional[AuditLogActionCategory]:
        # fmt: off
        lookup: Dict[AuditLogAction, Optional[AuditLogActionCategory]] = {
            AuditLogAction.guild_update:                 AuditLogActionCategory.update,
            AuditLogAction.channel_create:               AuditLogActionCategory.create,
            AuditLogAction.channel_update:               AuditLogActionCategory.update,
            AuditLogAction.channel_delete:               AuditLogActionCategory.delete,
            AuditLogAction.overwrite_create:             AuditLogActionCategory.create,
            AuditLogAction.overwrite_update:             AuditLogActionCategory.update,
            AuditLogAction.overwrite_delete:             AuditLogActionCategory.delete,
            AuditLogAction.kick:                         None,
            AuditLogAction.member_prune:                 None,
            AuditLogAction.ban:                          None,
            AuditLogAction.unban:                        None,
            AuditLogAction.member_update:                AuditLogActionCategory.update,
            AuditLogAction.member_role_update:           AuditLogActionCategory.update,
            AuditLogAction.member_move:                  None,
            AuditLogAction.member_disconnect:            None,
            AuditLogAction.bot_add:                      None,
            AuditLogAction.role_create:                  AuditLogActionCategory.create,
            AuditLogAction.role_update:                  AuditLogActionCategory.update,
            AuditLogAction.role_delete:                  AuditLogActionCategory.delete,
            AuditLogAction.invite_create:                AuditLogActionCategory.create,
            AuditLogAction.invite_update:                AuditLogActionCategory.update,
            AuditLogAction.invite_delete:                AuditLogActionCategory.delete,
            AuditLogAction.webhook_create:               AuditLogActionCategory.create,
            AuditLogAction.webhook_update:               AuditLogActionCategory.update,
            AuditLogAction.webhook_delete:               AuditLogActionCategory.delete,
            AuditLogAction.emoji_create:                 AuditLogActionCategory.create,
            AuditLogAction.emoji_update:                 AuditLogActionCategory.update,
            AuditLogAction.emoji_delete:                 AuditLogActionCategory.delete,
            AuditLogAction.message_delete:               AuditLogActionCategory.delete,
            AuditLogAction.message_bulk_delete:          AuditLogActionCategory.delete,
            AuditLogAction.message_pin:                  None,
            AuditLogAction.message_unpin:                None,
            AuditLogAction.integration_create:           AuditLogActionCategory.create,
            AuditLogAction.integration_update:           AuditLogActionCategory.update,
            AuditLogAction.integration_delete:           AuditLogActionCategory.delete,
            AuditLogAction.stage_instance_create:        AuditLogActionCategory.create,
            AuditLogAction.stage_instance_update:        AuditLogActionCategory.update,
            AuditLogAction.stage_instance_delete:        AuditLogActionCategory.delete,
            AuditLogAction.sticker_create:               AuditLogActionCategory.create,
            AuditLogAction.sticker_update:               AuditLogActionCategory.update,
            AuditLogAction.sticker_delete:               AuditLogActionCategory.delete,
            AuditLogAction.thread_create:                AuditLogActionCategory.create,
            AuditLogAction.thread_update:                AuditLogActionCategory.update,
            AuditLogAction.thread_delete:                AuditLogActionCategory.delete,
            AuditLogAction.guild_scheduled_event_create: AuditLogActionCategory.create,
            AuditLogAction.guild_scheduled_event_update: AuditLogActionCategory.update,
            AuditLogAction.guild_scheduled_event_delete: AuditLogActionCategory.delete,
            AuditLogAction.application_command_permission_update: AuditLogActionCategory.update,
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
            return "application_command"
        else:
            return None


class UserFlags(int, Enum):
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


class ActivityType(int, Enum):
    unknown = -1
    playing = 0
    streaming = 1
    listening = 2
    watching = 3
    custom = 4
    competing = 5


class TeamMembershipState(int, Enum):
    invited = 1
    accepted = 2


class WebhookType(int, Enum):
    incoming = 1
    channel_follower = 2
    application = 3


class ExpireBehaviour(int, Enum):
    remove_role = 0
    kick = 1


ExpireBehavior = ExpireBehaviour


class StickerType(int, Enum):
    standard = 1
    guild = 2


class StickerFormatType(int, Enum):
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


class InviteTarget(int, Enum):
    unknown = 0
    stream = 1
    embedded_application = 2


class InteractionType(int, Enum):
    ping = 1
    application_command = 2
    component = 3
    application_command_autocomplete = 4
    modal_submit = 5


class InteractionResponseType(int, Enum):
    pong = 1
    # ack = 2 (deprecated)
    # channel_message = 3 (deprecated)
    channel_message = 4  # (with source)
    deferred_channel_message = 5  # (with source)
    deferred_message_update = 6  # for components
    message_update = 7  # for components
    application_command_autocomplete_result = 8  # for autocomplete
    modal = 9  # for modals


class VideoQualityMode(int, Enum):
    auto = 1
    full = 2


class ComponentType(int, Enum):
    action_row = 1
    button = 2
    select = 3
    text_input = 4


class ButtonStyle(int, Enum):
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


class TextInputStyle(int, Enum):
    short = 1
    paragraph = 2
    # Aliases
    single_line = 1
    multi_line = 2
    long = 2


class ApplicationCommandType(int, Enum):
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


class StagePrivacyLevel(int, Enum):
    public = 1
    closed = 2
    guild_only = 2


class NSFWLevel(int, Enum):
    default = 0
    explicit = 1
    safe = 2
    age_restricted = 3


class GuildScheduledEventEntityType(int, Enum):
    stage_instance = 1
    voice = 2
    external = 3


class GuildScheduledEventStatus(int, Enum):
    scheduled = 1
    active = 2
    completed = 3
    canceled = 4


class GuildScheduledEventPrivacyLevel(int, Enum):
    guild_only = 2


class ThreadArchiveDuration(int, Enum):
    hour = 60
    day = 1440
    three_days = 4320
    week = 10080


class WidgetStyle(str, Enum):
    shield = "shield"
    banner1 = "banner1"
    banner2 = "banner2"
    banner3 = "banner3"
    banner4 = "banner4"


# reference: https://discord.com/developers/docs/reference#locales
class Locale(str, Enum):
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


EnumT = TypeVar("EnumT", bound=Enum)

def create_unknown_value(cls: Type[EnumT], val: Any) -> EnumT:
    unknown = cls.__new__(cls)  # type: ignore  # skip Enum type validation
    unknown._name_ = f"unknown_{val}"
    unknown._value_ = val
    return unknown


def try_enum(cls: Type[EnumT], val: Any) -> EnumT:
    """A function that tries to turn the value into enum ``cls``.
    If it fails it returns a proxy invalid value instead.
    """
    try:
        return cls._value2member_map_[val]  # type: ignore
    except KeyError:
        return create_unknown_value(cls, val)


# These can probably be deprecated:


def enum_if_int(cls: Type[EnumT], val: Any) -> EnumT:
    """A function that tries to turn the value into enum ``cls``.

    If it fails it returns a proxy invalid value instead.
    """
    return try_enum(cls, val) if isinstance(val, int) else val


def try_enum_to_int(val: Any) -> Any:
    if isinstance(val, int):
        return val
    try:
        return val.value
    except Exception:
        return val
