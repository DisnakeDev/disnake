# SPDX-License-Identifier: MIT

from __future__ import annotations

import types
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterator,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

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


_T = TypeVar("_T", bound="EnumMeta")


def _is_descriptor(obj):
    return hasattr(obj, "__get__") or hasattr(obj, "__set__") or hasattr(obj, "__delete__")


class _EnumDict(Dict[str, Any]):
    """
    Enforces proper enum value typing and prevents duplicate names.

    This is used as the ephemeral namespace in enum class creation.

    Class attributes such as descriptors and private attributes will be directly stored inside this
    dict, whereas any actual enum members are stored inside ``self.member_map``.

    ``EnumMeta`` will use the collected items in ``self.member_map`` as the enum members.
    """

    def __init__(self, base: Type[Any]):
        # We explicitly take a base in __init__, unlike default Enums, to more easily
        # enforce proper value typing. This should ensure better performance, as e.g.
        # `Enum[int].one + 3 == 4` is more performant than `Enum[Any].one.value + 3 == 4`,
        # as this saves a lookup. We do lose some functionality here, but it's probably
        # worth the cost; especially considering all current enums have monotyped values.
        super().__init__()
        self.base = base
        self.member_map: Dict[str, Any] = {}

    def __setitem__(self, name: str, value: Any) -> None:
        if name in {
            # Illegal names defined in original python enums:
            "mro",
            "",
            # Additional illegal names to prevent overwriting:
            "name",
            "value",
        }:
            raise ValueError(f"Invalid Enum member name: {name}.")

        if name.startswith("_") or _is_descriptor(value):
            super().__setitem__(name, value)
            return

        if not isinstance(value, self.base):
            raise TypeError(
                f"Member {name} must be of type {self.base.__name__}, got {type(value).__name__}."
            )

        if name in self.member_map:
            raise TypeError(f"Cannot create multiple members with the same name: {name!r}.")

        self.member_map[name] = value


class EnumMeta(type):
    __is_enum_instantiated__: ClassVar[bool] = False

    _member_map_: Mapping[str, Enum]
    _value2member_map_: Mapping[Any, Enum]

    def __new__(
        metacls: Type[_T],  # pyright: ignore[reportSelfClsParameterName]
        name: str,
        bases: Tuple[Type[Any], Type[Enum]],
        namespace: _EnumDict,
    ) -> _T:
        # Initialise basic namespace.
        # Falling back to dict here is fine; the class' __dict__ will be a normal dict regardless.
        ns: Dict[str, Any] = {
            "__base_type__": (base := namespace.base),
            "_member_map_": (name_map := {}),
            "_value2member_map_": (value_map := {}),
        }

        ns.update(namespace)

        # Member creation logic is not required for the base Enum class.
        # Set internal flag to True such that all following enums get proper member handling.
        if not EnumMeta.__is_enum_instantiated__:
            EnumMeta.__is_enum_instantiated__ = True
            ns["__enum_type__"] = enum = super().__new__(metacls, name, bases, ns)
            return enum

        # Ensure we aren't creating an enum with members and __base_type__ object.
        # This allows untyped enums to provide methods to all its further subclasses,
        # while disallowing untyped enum members.
        if base is object and namespace.member_map:
            raise TypeError(f"Cannot create enum {name} with members but no defined member type.")

        if len(bases) == 1:
            ns["__enum_type__"] = bases[0]
        else:
            _, ns["__enum_type__"] = bases  # ensured possible in __prepare__

        # Create new enum class...
        cls = super().__new__(metacls, name, bases, {**Enum.__dict__, **ns})

        # Create and populate new members...
        for name_, value_ in namespace.member_map.items():
            if value_ in value_map:
                member = name_map[name_] = value_map[value_]

            else:
                member = cls.__new__(cls, value_)  # type: ignore
                name_map[name_] = value_map[value_] = member

                # We use object's setattr method to bypass Enum's protected setattr.
                object.__setattr__(member, "name", name_)
                object.__setattr__(member, "value", value_)

            setattr(cls, name_, member)

        return cls

    @classmethod
    def __prepare__(
        metacls,  # pyright: ignore[reportSelfClsParameterName]
        name: str,
        bases: Tuple[Type[Any], ...] = (),
        /,
        **kwds: Any,
    ) -> _EnumDict:
        # with this we get to ensure the new class' namespace is an _EnumDict

        if not EnumMeta.__is_enum_instantiated__:
            return _EnumDict(object)

        if len(bases) == 1:
            # If single base, that base must be a predefined enum; get the base type from that
            # enum and use it for the new enum.
            enum_type = bases[0]
            base: Type[Any] = enum_type.__base_type__  # type: ignore

        else:
            # If multiple bases, the first base must be the base type, and the second must be
            # the enum to extend.
            try:
                base, enum_type = bases
            except ValueError:
                raise TypeError("Expected at most two base classes for an enum.") from None

            if isinstance(base, EnumMeta):
                raise TypeError("A typed Enum's first base class must be its values' type.")

        for enum_type_base in enum_type.__mro__:
            # Ensure the inherited base does not have any defined members...
            if issubclass(enum_type_base, Enum) and enum_type_base._member_map_:
                raise TypeError(f"{name} cannot extend enumeration {enum_type_base.__name__}.")

        return _EnumDict(base)

    def __repr__(cls) -> str:
        return f"<enum {cls.__name__}>"

    def __call__(cls, value: Any) -> Enum:
        try:
            return cls._value2member_map_[value]
        except KeyError:
            raise ValueError(f"{value} is not a valid {cls.__name__}.") from None

    def __getitem__(cls, name: str) -> Enum:
        return cls._member_map_[name]

    def __contains__(cls, value: Enum) -> bool:
        return value in cls._value2member_map_

    def __iter__(cls) -> Iterator[Enum]:
        yield from cls._member_map_.values()

    def __len__(cls) -> int:
        return len(cls._value2member_map_)

    @property
    def __members__(cls) -> Mapping[str, Enum]:
        return types.MappingProxyType(cls._member_map_)

    @property
    def _member_names_(cls) -> Sequence[str]:
        # I *think* this should be fine as a property?
        # Hardly ever gets used so I don't really see the value in pre-computing it like
        # vanilla Enums do. I decided to save memory but we can always just revert this.
        return tuple(cls._member_map_)


if TYPE_CHECKING:
    from enum import Enum
else:

    class Enum(metaclass=EnumMeta):
        __base_type__: ClassVar[Type[Any]]
        __enum_type__: ClassVar[Type[Enum]]
        name: str
        value: Any

        def __repr__(self) -> str:
            return f"<{type(self).__name__}.{self.name}: {self.value!r}>"

        def __str__(self) -> str:
            return self.name

        def __setattr__(self, name: str, value: Any) -> None:
            if name in {"name", "value"}:
                # We disallow overwriting enum members' names and values as this could very easily
                # break a bot, and would be extremely hard to debug from an outside perspective.
                # This is done via direct attributes and a setattr check to make reading these
                # attributes as fast as possible, which is relevant because enums are used extensively
                # in (de)serializing data sent to/received from discord.
                raise AttributeError(f"Overwriting {type(self).__name__}.{name} is not allowed.")

            super().__setattr__(name, value)


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


class SpeakingState(int, Enum):  # TODO: Docs
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
    """Represents the category that the :class:`AuditLogAction` belongs to.

    This can be retrieved via :attr:`AuditLogEntry.category`.
    """

    create = 1
    delete = 2
    update = 3


class AuditLogAction(int, Enum):
    """Represents the type of action being done for a :class:`AuditLogEntry`\\,
    which is retrievable via :meth:`Guild.audit_logs`.
    """

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
    automod_rule_create                   = 140
    automod_rule_update                   = 141
    automod_rule_delete                   = 142
    automod_block_message                 = 143
    automod_send_alert_message            = 144
    automod_timeout                       = 145
    # fmt: on

    @property
    def category(self) -> Optional[AuditLogActionCategory]:
        """The category of this :class:`AuditLogAction`."""

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
        """The target of this :class:`AuditLogAction`."""

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
        """The file extension associated with this type of sticker."""

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
    string_select = 3
    select = string_select  # backwards compatibility
    text_input = 4
    user_select = 5
    role_select = 6
    mentionable_select = 7
    channel_select = 8


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


class ApplicationCommandPermissionType(int, Enum):
    role = 1
    user = 2
    channel = 3


class OptionType(int, Enum):
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
    cancelled = 4


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
    cs = "cs"
    da = "da"
    de = "de"
    el = "el"
    en_GB = "en-GB"
    en_US = "en-US"
    es_ES = "es-ES"
    fi = "fi"
    fr = "fr"
    hi = "hi"
    hr = "hr"
    it = "it"
    ja = "ja"
    ko = "ko"
    lt = "lt"
    hu = "hu"
    nl = "nl"
    no = "no"
    pl = "pl"
    pt_BR = "pt-BR"
    ro = "ro"
    ru = "ru"
    sv_SE = "sv-SE"
    th = "th"
    tr = "tr"
    uk = "uk"
    vi = "vi"
    zh_CN = "zh-CN"
    zh_TW = "zh-TW"

    def __str__(self):
        return self.value


class AutoModActionType(int, Enum):
    block_message = 1
    send_alert_message = 2
    timeout = 3


class AutoModEventType(int, Enum):
    message_send = 1


class AutoModTriggerType(int, Enum):
    keyword = 1
    harmful_link = 2
    spam = 3
    keyword_preset = 4
    mention_spam = 5


class ThreadSortOrder(int, Enum):
    latest_activity = 0
    creation_date = 1


EnumT = TypeVar("EnumT", bound=Enum)


def try_enum(cls: Type[EnumT], val: Any) -> EnumT:
    """A function that tries to turn the value into enum ``cls``.
    If it fails it returns a proxy invalid value instead.
    If this fails, too, just return the value unedited.
    """
    try:
        return cls._value2member_map_[val]  # type: ignore

    except KeyError:
        try:
            unknown = cls.__new__(cls, val)
            object.__setattr__(unknown, "name", f"unknown_{val}")
            object.__setattr__(unknown, "value", val)

            return unknown

        except TypeError:
            return val


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
