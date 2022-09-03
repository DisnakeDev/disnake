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
        cls = super().__new__(metacls, name, bases, Enum.__dict__ | ns)

        # Create and populate new members...
        for name_, value_ in namespace.member_map.items():
            member = cls.__new__(cls, value_)  # type: ignore

            # We use object's setattr method to bypass Enum's protected setattr.
            object.__setattr__(member, "name", name_)
            object.__setattr__(member, "value", value_)

            name_map[name_] = member
            value_map.setdefault(value_, member)  # Prioritize first defined in case of alias
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
    """Specifies the type of channel."""

    text = 0
    """A text channel."""
    private = 1
    """A voice channel."""
    voice = 2
    """A private text channel. Also called a direct message."""
    group = 3
    """A private group text channel."""
    category = 4
    """A category channel."""
    news = 5
    """A guild news channel."""
    news_thread = 10
    """ A guild stage voice channel.

    .. versionadded:: 1.7
    """
    public_thread = 11
    """A news thread.

    .. versionadded:: 2.0
    """
    private_thread = 12
    """A public thread.

    .. versionadded:: 2.0
    """
    stage_voice = 13
    """A private thread.

    .. versionadded:: 2.0
    """
    guild_directory = 14
    """A student hub channel.

    .. versionadded:: 2.1
    """
    forum = 15
    """A channel of only threads.

    .. versionadded:: 2.5
    """


class MessageType(int, Enum):
    """Specifies the type of :class:`Message`. This is used to denote if a message
    is to be interpreted as a system message or a regular message.

    .. container:: operations

      .. describe:: x == y

          Checks if two messages are equal.
      .. describe:: x != y

          Checks if two messages are not equal.
    """

    default = 0
    """The default message type. This is the same as regular messages."""
    recipient_add = 1
    """The system message when a user is added to a group private
    message or a thread.
    """
    recipient_remove = 2
    """The system message when a user is removed from a group private
    message or a thread.
    """
    call = 3
    """The system message denoting call state, e.g. missed call, started call,
    etc.
    """
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
    """The system message denoting that a member has "nitro boosted" a guild
    and it achieved level 1.
    """
    premium_guild_tier_2 = 10
    """The system message denoting that a member has "nitro boosted" a guild
    and it achieved level 2.
    """
    premium_guild_tier_3 = 11
    """The system message denoting that a member has "nitro boosted" a guild
    and it achieved level 3.
    """
    channel_follow_add = 12
    """ The system message denoting that an announcement channel has been followed.

    .. versionadded:: 1.3
    """
    guild_stream = 13
    """The system message denoting that a member is streaming in the guild.

    .. versionadded:: 1.7
    """
    guild_discovery_disqualified = 14
    """The system message denoting that the guild is no longer eligible for Server
    Discovery.

    .. versionadded:: 1.7
    """
    guild_discovery_requalified = 15
    """The system message denoting that the guild has become eligible again for Server
    Discovery.

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
    """The system message sent as a reminder to invite people to the guild.

    .. versionadded:: 2.0
    """
    guild_invite_reminder = 22
    """The system message denoting the message in the thread that is the one that started the
    thread's conversation topic.

    .. versionadded:: 2.0
    """
    context_menu_command = 23
    """The system message denoting that a context menu command was executed.

    .. versionadded:: 2.3
    """
    auto_moderation_action = 24
    """The system message denoting that Auto Moderation has taken an action on a message.

    .. versionadded:: 2.5
    """


class PartyType(int, Enum):
    """Represents the type of a voice channel activity/application."""

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


class SpeakingState(int, Enum):  # TODO: Docs
    """Specifies the speaking state of a user in a voice channel."""

    none = 0
    """The state of a user that is currently silent."""
    voice = 1
    """The state of a user that is currently transmitting voice data."""
    soundshare = 2
    """The state of a user that is currently transmitting voice data as part of
    sharing their screen. This does not display a speaking indicator.
    """
    priority = 4
    """The state of a user that is currently transmitting voice data as a priority speaker.
    This reduces the volume of other speakers.
    """


class VerificationLevel(int, Enum):
    """Specifies a :class:`Guild`\\'s verification level, which is the criteria in
    which a member must meet before being able to send messages to the guild.

    .. container:: operations

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
    """Member must have a verified email and be registered on Discord for more
    than five minutes.
    """
    high = 3
    """Member must have a verified email, be registered on Discord for more
    than five minutes, and be a member of the guild itself for more than
    ten minutes.
    """
    highest = 4
    """Member must have a verified phone on their Discord account."""


class ContentFilter(int, Enum):
    """Specifies a :class:`Guild`\\'s explicit content filter, which is the machine
    learning algorithms that Discord uses to detect if an image contains
    pornography or otherwise explicit content.

    .. container:: operations

        .. versionadded:: 2.0

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


class Status(str, Enum):
    """Specifies a :class:`Member`\\'s status."""

    online = "online"
    """The member is online."""
    offline = "offline"
    """The member is offline."""
    idle = "idle"
    """The member is idle."""
    dnd = "dnd"
    """The member is on "Do Not Disturb"."""
    do_not_disturb = "dnd"
    """An alias for :attr:`dnd`."""
    invisible = "invisible"
    """The member is "invisible". In reality, this is only used in sending
    a presence a la :meth:`Client.change_presence`. When you receive a
    user's presence this will be :attr:`offline` instead.
    """
    streaming = "streaming"
    """The member is live streaming to Twitch.

    .. versionadded:: 2.3
    """


class DefaultAvatar(int, Enum):
    """Represents the default avatar of a Discord :class:`User`"""

    blurple = 0
    """Represents the default avatar with the color blurple.
    See also :attr:`Colour.blurple`
    """
    grey = 1
    """Represents the default avatar with the color grey.
    See also :attr:`Colour.greyple`
    """
    gray = 1
    """An alias for :attr:`grey`."""
    green = 2
    """Represents the default avatar with the color green.
    See also :attr:`Colour.green`
    """
    orange = 3
    """Represents the default avatar with the color orange.
    See also :attr:`Colour.orange`
    """
    red = 4
    """Represents the default avatar with the color red.
    See also :attr:`Colour.red`
    """


class NotificationLevel(int, Enum):
    """Specifies whether a :class:`Guild` has notifications on for all messages or mentions only by default.

    .. container:: operations

        .. versionadded:: 2.0

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


class AuditLogActionCategory(int, Enum):
    """Represents the category that the :class:`AuditLogAction` belongs to.

    This can be retrieved via :attr:`AuditLogEntry.category`.
    """

    create = 1
    """The action is the creation of something."""
    delete = 2
    """The action is the deletion of something."""
    update = 3
    """The action is the update of something."""


class AuditLogAction(int, Enum):
    """Represents the type of action being done for a :class:`AuditLogEntry`\\,
    which is retrievable via :meth:`Guild.audit_logs`.
    """

    # fmt: off
    guild_update                     = 1
    """The guild has updated. Things that trigger this include:

    - Changing the guild vanity URL
    - Changing the guild invite splash
    - Changing the guild AFK channel or timeout
    - Changing the guild voice server region
    - Changing the guild icon, banner, or discovery splash
    - Changing the guild moderation settings
    - Changing things related to the guild widget

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Guild`.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.afk_channel`
    - :attr:`~AuditLogDiff.system_channel`
    - :attr:`~AuditLogDiff.afk_timeout`
    - :attr:`~AuditLogDiff.default_message_notifications`
    - :attr:`~AuditLogDiff.explicit_content_filter`
    - :attr:`~AuditLogDiff.mfa_level`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.owner`
    - :attr:`~AuditLogDiff.splash`
    - :attr:`~AuditLogDiff.discovery_splash`
    - :attr:`~AuditLogDiff.icon`
    - :attr:`~AuditLogDiff.banner`
    - :attr:`~AuditLogDiff.vanity_url_code`
    - :attr:`~AuditLogDiff.preferred_locale`
    """
    channel_create                   = 10
    """A new channel was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    either a :class:`abc.GuildChannel` or :class:`Object` with an ID.

    A more filled out object in the :class:`Object` case can be found
    by using :attr:`~AuditLogEntry.after`.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.overwrites`
    """
    channel_update                   = 11
    """A channel was updated. Things that trigger this include:

    - The channel name or topic was changed
    - The channel bitrate was changed

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`abc.GuildChannel` or :class:`Object` with an ID.

    A more filled out object in the :class:`Object` case can be found
    by using :attr:`~AuditLogEntry.after` or :attr:`~AuditLogEntry.before`.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.position`
    - :attr:`~AuditLogDiff.overwrites`
    - :attr:`~AuditLogDiff.topic`
    - :attr:`~AuditLogDiff.bitrate`
    - :attr:`~AuditLogDiff.rtc_region`
    - :attr:`~AuditLogDiff.video_quality_mode`
    - :attr:`~AuditLogDiff.default_auto_archive_duration`
    """
    channel_delete                   = 12
    """A channel was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    an :class:`Object` with an ID.

    A more filled out object can be found by using the
    :attr:`~AuditLogEntry.before` object.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.overwrites`
    """
    overwrite_create                 = 13
    """A channel permission overwrite was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`abc.GuildChannel` or :class:`Object` with an ID.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    either a :class:`Role` or :class:`Member`. If the object is not found
    then it is a :class:`Object` with an ID being filled, a name, and a
    ``type`` attribute set to either ``'role'`` or ``'member'`` to help
    dictate what type of ID it is.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.deny`
    - :attr:`~AuditLogDiff.allow`
    - :attr:`~AuditLogDiff.id`
    - :attr:`~AuditLogDiff.type`

    .. versionchanged:: 2.6
        :attr:`~AuditLogDiff.type` for this action is now an :class:`int`.
    """
    overwrite_update                 = 14
    """A channel permission overwrite was changed, this is typically
    when the permission values change.

    See :attr:`overwrite_create` for more information on how the
    :attr:`~AuditLogEntry.target` and :attr:`~AuditLogEntry.extra` fields
    are set.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.deny`
    - :attr:`~AuditLogDiff.allow`
    - :attr:`~AuditLogDiff.id`
    - :attr:`~AuditLogDiff.type`

    .. versionchanged:: 2.6
        :attr:`~AuditLogDiff.type` for this action is now an :class:`int`.
    """
    overwrite_delete                 = 15
    """A channel permission overwrite was deleted.

    See :attr:`overwrite_create` for more information on how the
    :attr:`~AuditLogEntry.target` and :attr:`~AuditLogEntry.extra` fields
    are set.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.deny`
    - :attr:`~AuditLogDiff.allow`
    - :attr:`~AuditLogDiff.id`
    - :attr:`~AuditLogDiff.type`

    .. versionchanged:: 2.6
        :attr:`~AuditLogDiff.type` for this action is now an :class:`int`.
    """
    kick                             = 20
    """A member was kicked.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`User` who got kicked.

    When this is the action, :attr:`~AuditLogEntry.changes` is empty.
    """
    member_prune                     = 21
    """A member prune was triggered.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    set to ``None``.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with two attributes:

    - ``delete_members_days``: An integer specifying how far the prune was.
    - ``members_removed``: An integer specifying how many members were removed.

    When this is the action, :attr:`~AuditLogEntry.changes` is empty.
    """
    ban                              = 22
    """A member was banned.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`User` who got banned.

    When this is the action, :attr:`~AuditLogEntry.changes` is empty.
    """
    unban                            = 23
    """A member was unbanned.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`User` who got unbanned.

    When this is the action, :attr:`~AuditLogEntry.changes` is empty.
    """
    member_update                    = 24
    """A member has updated. This triggers in the following situations:

    - A nickname was changed
    - They were server muted or deafened (or it was undone)
    - They were timed out

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who got updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.nick`
    - :attr:`~AuditLogDiff.mute`
    - :attr:`~AuditLogDiff.deaf`
    - :attr:`~AuditLogDiff.timeout`
    """
    member_role_update               = 25
    """A member's role has been updated. This triggers when a member
    either gains a role or loses a role.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who got the role.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.roles`
    """
    member_move                      = 26
    """A member's voice channel has been updated. This triggers when a
    member is moved to a different voice channel.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with two attributes:

    - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the members were moved.
    - ``count``: An integer specifying how many members were moved.

    .. versionadded:: 1.3
    """
    member_disconnect                = 27
    """A member's voice state has changed. This triggers when a
    member is force disconnected from voice.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with one attribute:

    - ``count``: An integer specifying how many members were disconnected.

    .. versionadded:: 1.3
    """
    bot_add                          = 28
    """A bot was added to the guild.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` which was added to the guild.

    .. versionadded:: 1.3
    """
    role_create                      = 30
    """A new role was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Role` or a :class:`Object` with the ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.colour`
    - :attr:`~AuditLogDiff.mentionable`
    - :attr:`~AuditLogDiff.hoist`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.permissions`
    """
    role_update                      = 31
    """A role was updated. This triggers in the following situations:

    - The name has changed
    - The permissions have changed
    - The colour has changed
    - Its hoist/mentionable state has changed

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Role` or a :class:`Object` with the ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.colour`
    - :attr:`~AuditLogDiff.mentionable`
    - :attr:`~AuditLogDiff.hoist`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.permissions`
    """
    role_delete                      = 32
    """A role was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Role` or a :class:`Object` with the ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.colour`
    - :attr:`~AuditLogDiff.mentionable`
    - :attr:`~AuditLogDiff.hoist`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.permissions`
    """
    invite_create                    = 40
    """An invite was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Invite` that was created.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.max_age`
    - :attr:`~AuditLogDiff.code`
    - :attr:`~AuditLogDiff.temporary`
    - :attr:`~AuditLogDiff.inviter`
    - :attr:`~AuditLogDiff.channel`
    - :attr:`~AuditLogDiff.uses`
    - :attr:`~AuditLogDiff.max_uses`
    """
    invite_update                    = 41
    """An invite was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Invite` that was updated.
    """
    invite_delete                    = 42
    """An invite was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Invite` that was deleted.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.max_age`
    - :attr:`~AuditLogDiff.code`
    - :attr:`~AuditLogDiff.temporary`
    - :attr:`~AuditLogDiff.inviter`
    - :attr:`~AuditLogDiff.channel`
    - :attr:`~AuditLogDiff.uses`
    - :attr:`~AuditLogDiff.max_uses`
    """
    webhook_create                   = 50
    """A webhook was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the webhook ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.channel`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.application_id`

    .. versionchanged:: 2.6
        Added :attr:`~AuditLogDiff.application_id`.

    .. versionchanged:: 2.6
        :attr:`~AuditLogDiff.type` for this action is now a :class:`WebhookType`.
    """
    webhook_update                   = 51
    """A webhook was updated. This trigger in the following situations:

    - The webhook name changed
    - The webhook channel changed

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the webhook ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.channel`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.avatar`
    """
    webhook_delete                   = 52
    """A webhook was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the webhook ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.channel`
    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.application_id`

    .. versionchanged:: 2.6
        Added :attr:`~AuditLogDiff.application_id`.

    .. versionchanged:: 2.6
        :attr:`~AuditLogDiff.type` for this action is now a :class:`WebhookType`.
    """
    emoji_create                     = 60
    """An emoji was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Emoji` or :class:`Object` with the emoji ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    """
    emoji_update                     = 61
    """An emoji was updated. This triggers when the name has changed.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Emoji` or :class:`Object` with the emoji ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    """
    emoji_delete                     = 62
    """An emoji was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the emoji ID.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    """
    message_delete                   = 72
    """A message was deleted by a moderator. Note that this
    only triggers if the message was deleted by someone other than the author.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who had their message deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with two attributes:

    - ``count``: An integer specifying how many messages were deleted.
    - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message got deleted.
    """
    message_bulk_delete              = 73
    """Messages were bulk deleted by a moderator.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`TextChannel` or :class:`Object` with the ID of the channel that was purged.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with one attribute:

    - ``count``: An integer specifying how many messages were deleted.

    .. versionadded:: 1.3
    """
    message_pin                      = 74
    """A message was pinned in a channel.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who had their message pinned.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with two attributes:

    - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message was pinned.
    - ``message_id``: the ID of the message which was pinned.

    .. versionadded:: 1.3
    """
    message_unpin                    = 75
    """A message was unpinned in a channel.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who had their message unpinned.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with two attributes:

    - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message was unpinned.
    - ``message_id``: the ID of the message which was unpinned.

    .. versionadded:: 1.3
    """
    integration_create               = 80
    """A guild integration was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the integration ID of the integration which was created.

    .. versionadded:: 1.3
    """
    integration_update               = 81
    """A guild integration was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the integration ID of the integration which was updated.

    .. versionadded:: 1.3
    """
    integration_delete               = 82
    """A guild integration was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the integration ID of the integration which was deleted.

    .. versionadded:: 1.3
    """
    stage_instance_create            = 83
    """A stage instance was started.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`StageInstance` or :class:`Object` with the ID of the stage
    instance which was created.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.topic`
    - :attr:`~AuditLogDiff.privacy_level`

    .. versionadded:: 2.0
    """
    stage_instance_update            = 84
    """A stage instance was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`StageInstance` or :class:`Object` with the ID of the stage
    instance which was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.topic`
    - :attr:`~AuditLogDiff.privacy_level`

    .. versionadded:: 2.0
    """
    stage_instance_delete            = 85
    """A stage instance was ended.

    .. versionadded:: 2.0
    """
    sticker_create                   = 90
    """A sticker was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
    which was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.emoji`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.format_type`
    - :attr:`~AuditLogDiff.description`
    - :attr:`~AuditLogDiff.available`

    .. versionadded:: 2.0
    """
    sticker_update                   = 91
    """A sticker was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
    which was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.emoji`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.format_type`
    - :attr:`~AuditLogDiff.description`
    - :attr:`~AuditLogDiff.available`

    .. versionadded:: 2.0
    """
    sticker_delete                   = 92
    """A sticker was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
    which was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.emoji`
    - :attr:`~AuditLogDiff.type`
    - :attr:`~AuditLogDiff.format_type`
    - :attr:`~AuditLogDiff.description`
    - :attr:`~AuditLogDiff.available`

    .. versionadded:: 2.0
    """
    guild_scheduled_event_create     = 100
    """A guild scheduled event was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`GuildScheduledEvent` or :class:`Object` with the ID of the event
    which was created.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.description`
    - :attr:`~AuditLogDiff.privacy_level`
    - :attr:`~AuditLogDiff.status`

    .. versionadded:: 2.3
    """
    guild_scheduled_event_update     = 101
    """A guild scheduled event was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`GuildScheduledEvent` or :class:`Object` with the ID of the event
    which was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.description`
    - :attr:`~AuditLogDiff.privacy_level`
    - :attr:`~AuditLogDiff.status`
    - :attr:`~AuditLogDiff.image`

    .. versionadded:: 2.3
    """
    guild_scheduled_event_delete     = 102
    """A guild scheduled event was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`GuildScheduledEvent` or :class:`Object` with the ID of the event
    which was deleted.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.description`
    - :attr:`~AuditLogDiff.privacy_level`
    - :attr:`~AuditLogDiff.status`

    .. versionadded:: 2.3
    """
    thread_create                    = 110
    """A thread was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Thread` or :class:`Object` with the ID of the thread which
    was created.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.archived`
    - :attr:`~AuditLogDiff.locked`
    - :attr:`~AuditLogDiff.auto_archive_duration`
    - :attr:`~AuditLogDiff.type`

    .. versionadded:: 2.0
    """
    thread_update                    = 111
    """A thread was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Thread` or :class:`Object` with the ID of the thread which
    was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.archived`
    - :attr:`~AuditLogDiff.locked`
    - :attr:`~AuditLogDiff.auto_archive_duration`

    .. versionadded:: 2.0
    """
    thread_delete                    = 112
    """A thread was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Thread` or :class:`Object` with the ID of the thread which
    was deleted.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.archived`
    - :attr:`~AuditLogDiff.locked`
    - :attr:`~AuditLogDiff.auto_archive_duration`
    - :attr:`~AuditLogDiff.type`

    .. versionadded:: 2.0
    """
    application_command_permission_update = 121
    """The permissions of an application command were updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`ApplicationCommand` or :class:`Object` with the ID of the command whose
    permissions were updated or the application ID if these are application-wide permissions.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.command_permissions`

    .. versionadded:: 2.5
    """
    automod_rule_create                   = 140
    """An auto moderation rule was created.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`AutoModRule` or :class:`Object` with the ID of the auto moderation rule which
    was created.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.enabled`
    - :attr:`~AuditLogDiff.trigger_type`
    - :attr:`~AuditLogDiff.event_type`
    - :attr:`~AuditLogDiff.actions`
    - :attr:`~AuditLogDiff.trigger_metadata`
    - :attr:`~AuditLogDiff.exempt_roles`
    - :attr:`~AuditLogDiff.exempt_channels`

    .. versionadded:: 2.6
    """
    automod_rule_update                   = 141
    """An auto moderation rule was updated.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`AutoModRule` or :class:`Object` with the ID of the auto moderation rule which
    was updated.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.enabled`
    - :attr:`~AuditLogDiff.trigger_type`
    - :attr:`~AuditLogDiff.event_type`
    - :attr:`~AuditLogDiff.actions`
    - :attr:`~AuditLogDiff.trigger_metadata`
    - :attr:`~AuditLogDiff.exempt_roles`
    - :attr:`~AuditLogDiff.exempt_channels`

    .. versionadded:: 2.6
    """
    automod_rule_delete                   = 142
    """An auto moderation rule was deleted.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Object` with the ID of the auto moderation rule which
    was deleted.

    Possible attributes for :class:`AuditLogDiff`:

    - :attr:`~AuditLogDiff.name`
    - :attr:`~AuditLogDiff.enabled`
    - :attr:`~AuditLogDiff.trigger_type`
    - :attr:`~AuditLogDiff.event_type`
    - :attr:`~AuditLogDiff.actions`
    - :attr:`~AuditLogDiff.trigger_metadata`
    - :attr:`~AuditLogDiff.exempt_roles`
    - :attr:`~AuditLogDiff.exempt_channels`

    .. versionadded:: 2.6
    """
    automod_block_message                 = 143
    """A message was blocked by an auto moderation rule.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who had their message blocked.

    When this is the action, the type of :attr:`~AuditLogEntry.extra` is
    set to an unspecified proxy object with these attributes:

    - ``channel``: A :class:`~abc.GuildChannel`, :class:`Thread` or :class:`Object` with the channel ID where the message got blocked.
    - ``rule_name``: A :class:`str` with the name of the rule that matched.
    - ``rule_trigger_type``: A :class:`AutoModTriggerType` value with the trigger type of the rule.
    """
    automod_send_alert_message            = 144
    """An alert message was sent by an auto moderation rule.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who had their message flagged.

    See :attr:`automod_block_message` for more information on how the
    :attr:`~AuditLogEntry.extra` field is set.
    """
    automod_timeout                       = 145
    """A user was timed out by an auto moderation rule.

    When this is the action, the type of :attr:`~AuditLogEntry.target` is
    the :class:`Member` or :class:`User` who was timed out.

    See :attr:`automod_block_message` for more information on how the
    :attr:`~AuditLogEntry.extra` field is set.
    """
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
    """Represents Discord User flags."""

    staff = 1
    """The user is a Discord Employee."""
    partner = 2
    """The user is a Discord Partner."""
    hypesquad = 4
    """The user is a HypeSquad Events member."""
    bug_hunter = 8
    """The user is a Bug Hunter."""
    mfa_sms = 16
    """The user has SMS recovery for Multi Factor Authentication enabled."""
    premium_promo_dismissed = 32
    """The user has dismissed the Discord Nitro promotion."""
    hypesquad_bravery = 64
    """The user is a HypeSquad Bravery member."""
    hypesquad_brilliance = 128
    """The user is a HypeSquad Brilliance member."""
    hypesquad_balance = 256
    """The user is a HypeSquad Balance member."""
    early_supporter = 512
    """The user is an Early Supporter."""
    team_user = 1024
    """The user is a Team User."""
    system = 4096
    """The user is a system user (i.e. represents Discord officially)."""
    has_unread_urgent_messages = 8192
    """The user has an unread system message."""
    bug_hunter_level_2 = 16384
    """The user is a Bug Hunter Level 2."""
    verified_bot = 65536
    """The user is a Verified Bot."""
    verified_bot_developer = 131072
    """The user is an Early Verified Bot Developer."""
    discord_certified_moderator = 262144
    """The user is a Discord Certified Moderator."""
    http_interactions_bot = 524288
    """The user is a bot that only uses HTTP interactions.

    .. versionadded:: 2.3
    """
    spammer = 1048576
    """The user is marked as a spammer.

    .. versionadded:: 2.3
    """


class ActivityType(int, Enum):
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


class TeamMembershipState(int, Enum):
    """Represents the membership state of a team member
    retrieved through :func:`Client.application_info`.

    .. versionadded:: 1.3
    """

    invited = 1
    """Represents an invited member."""
    accepted = 2
    """Represents a member currently in the team."""


class WebhookType(int, Enum):
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


class ExpireBehaviour(int, Enum):
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


class StickerType(int, Enum):
    """Represents the type of sticker.

    .. versionadded:: 2.0
    """

    standard = 1
    """Represents a standard sticker that all Nitro users can use."""
    guild = 2
    """Represents a custom sticker created in a guild."""


class StickerFormatType(int, Enum):
    """Represents the type of sticker images.

    .. versionadded:: 1.6
    """

    png = 1
    """Represents a sticker with a png image."""
    apng = 2
    """Represents a sticker with an apng image."""
    lottie = 3
    """Represents a sticker with a lottie image."""

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
    """Represents the invite type for voice channel invites.

    .. versionadded:: 2.0
    """

    unknown = 0
    """The invite doesn't target anyone or anything."""
    stream = 1
    """A stream invite that targets a user."""
    embedded_application = 2
    """A stream invite that targets an embedded application."""


class InteractionType(int, Enum):
    """Specifies the type of :class:`Interaction`.

    .. versionadded:: 2.0
    """

    ping = 1
    """Represents Discord pinging to see if the interaction response server is alive."""
    application_command = 2
    """Represents an application command interaction."""
    component = 3
    """Represents a component based interaction."""
    application_command_autocomplete = 4
    """Represents an application command autocomplete interaction."""
    modal_submit = 5
    """Represents a modal submit interaction."""


class InteractionResponseType(int, Enum):
    """Specifies the response type for the interaction.

    .. versionadded:: 2.0
    """

    pong = 1
    """Pongs the interaction when given a ping.

    See also :meth:`InteractionResponse.pong`
    """
    # ack = 2 (deprecated)
    # channel_message = 3 (deprecated)
    channel_message = 4  # (with source)
    """Respond to the interaction with a message.

    See also :meth:`InteractionResponse.send_message`
    """
    deferred_channel_message = 5  # (with source)
    """Responds to the interaction with a message at a later time.

    See also :meth:`InteractionResponse.defer`
    """
    deferred_message_update = 6  # for components
    """Acknowledges the component interaction with a promise that
    the message will update later (though there is no need to actually update the message).

    See also :meth:`InteractionResponse.defer`
    """
    message_update = 7  # for components
    """Responds to the interaction by editing the message.

    See also :meth:`InteractionResponse.edit_message`
    """
    application_command_autocomplete_result = 8  # for autocomplete
    """Responds to the autocomplete interaction with suggested choices.

    See also :meth:`InteractionResponse.autocomplete`
    """
    modal = 9  # for modals
    """Responds to the interaction by displaying a modal.

    See also :meth:`InteractionResponse.send_modal`
    """


class VideoQualityMode(int, Enum):
    """Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0
    """

    auto = 1
    """Represents auto camera video quality."""
    full = 2
    """Represents full camera video quality."""


class ComponentType(int, Enum):
    """Represents the component type of a component.

    .. versionadded:: 2.0
    """

    action_row = 1
    """Represents the group component which holds different components in a row."""
    button = 2
    """Represents a button component."""
    select = 3
    """Represents a select component."""
    text_input = 4
    """Represents a text input component."""


class ButtonStyle(int, Enum):
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


class TextInputStyle(int, Enum):
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


class ApplicationCommandType(int, Enum):
    """Represents the type of an application command.

    .. versionadded:: 2.1
    """

    chat_input = 1
    """Represents a slash command."""
    user = 2
    """Represents a user command from the context menu."""
    message = 3
    """Represents a message command from the context menu."""


class ApplicationCommandPermissionType(int, Enum):
    """Represents the type of a permission of an application command.

    .. versionadded:: 2.5
    """

    role = 1
    """Represents a permission that affects roles."""
    user = 2
    """Represents a permission that affects users."""
    channel = 3
    """Represents a permission that affects channels."""


class OptionType(int, Enum):
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


class StagePrivacyLevel(int, Enum):
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


class NSFWLevel(int, Enum):
    """Represents the NSFW level of a guild.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two NSFW levels are equal.
        .. describe:: x != y

            Checks if two NSFW levels are not equal.
        .. describe:: x > y

            Checks if a NSFW level is higher than another.
        .. describe:: x < y

            Checks if a NSFW level is lower than another.
        .. describe:: x >= y

            Checks if a NSFW level is higher or equal to another.
        .. describe:: x <= y

            Checks if a NSFW level is lower or equal to another.
    """

    default = 0
    """The guild has not been categorised yet."""
    explicit = 1
    """The guild contains NSFW content."""
    safe = 2
    """The guild does not contain any NSFW content."""
    age_restricted = 3
    """The guild may contain NSFW content."""


class GuildScheduledEventEntityType(int, Enum):
    """Represents the type of a guild scheduled event entity.

    .. versionadded:: 2.3
    """

    stage_instance = 1
    """The guild scheduled event will take place in a stage channel."""
    voice = 2
    """The guild scheduled event will take place in a voice channel."""
    external = 3
    """The guild scheduled event will take place in a custom location."""


class GuildScheduledEventStatus(int, Enum):
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
    """An alias for :attr:`canceled`

    .. versionadded:: 2.6
    """


class GuildScheduledEventPrivacyLevel(int, Enum):
    """Represents the privacy level of a guild scheduled event.

    .. versionadded:: 2.3
    """

    guild_only = 2
    """The guild scheduled event is only for a specific guild."""


class ThreadArchiveDuration(int, Enum):
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


class WidgetStyle(str, Enum):
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


# reference: https://discord.com/developers/docs/reference#locales
class Locale(str, Enum):
    """Represents supported locales by Discord."""

    bg = "bg"
    """The ``bg`` (Bulgarian | български) locale."""
    cs = "cs"
    """The ``cs`` (Czech | Čeština) locale."""
    da = "da"
    """The ``da`` (Danish | Dansk) locale."""
    de = "de"
    """The ``de`` (German | Deutsch) locale."""
    el = "el"
    """The ``el`` (Greek | Ελληνικά) locale."""
    en_GB = "en-GB"
    """The ``en-GB`` (English, UK | English, UK) locale."""
    en_US = "en-US"
    """The ``en-US`` (English, US | English, US) locale."""
    es_ES = "es-ES"
    """The ``es-ES`` (Spanish | Español) locale."""
    fi = "fi"
    """The ``fi`` (Finnish | Suomi) locale."""
    fr = "fr"
    """The ``fr`` (French | Français) locale."""
    hi = "hi"
    """The ``hi`` (Hindi | हिन्दी) locale."""
    hr = "hr"
    """The ``hr`` (Croatian | Hrvatski) locale."""
    it = "it"
    """The ``it`` (Italian | Italiano) locale."""
    ja = "ja"
    """The ``ja`` (Japanese | 日本語) locale."""
    ko = "ko"
    """The ``ko`` (Korean | 한국어) locale."""
    lt = "lt"
    """The ``lt`` (Lithuanian | Lietuviškai) locale."""
    hu = "hu"
    """The ``hu`` (Hungarian | Magyar) locale."""
    nl = "nl"
    """The ``nl`` (Dutch | Nederlands) locale."""
    no = "no"
    """The ``no`` (Norwegian | Norsk) locale."""
    pl = "pl"
    """The ``pl`` (Polish | Polski) locale."""
    pt_BR = "pt-BR"
    """The ``pt-BR`` (Portuguese, Brazilian | Português do Brasil) locale."""
    ro = "ro"
    """The ``ro`` (Romanian, Romania | Română) locale."""
    ru = "ru"
    """The ``ru`` (Russian | Pусский) locale."""
    sv_SE = "sv-SE"
    """The ``sv-SE`` (Swedish | Svenska) locale."""
    th = "th"
    """The ``th`` (Thai | ไทย) locale."""
    tr = "tr"
    """The ``tr`` (Turkish | Türkçe) locale."""
    uk = "uk"
    """The ``uk`` (Ukrainian | Українська) locale."""
    vi = "vi"
    """The ``vi`` (Vietnamese | Tiếng Việt) locale."""
    zh_CN = "zh-CN"
    """The ``zh-CN`` (Chinese, China | 中文) locale."""
    zh_TW = "zh-TW"
    """The ``zh-TW`` (Chinese, Taiwan | 繁體中文) locale."""

    # def __str__(self):
    #     return self.value


class AutoModActionType(int, Enum):
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
        :attr:`~AutoModTriggerType.keyword`, and :attr:`~Permissions.moderate_members`
        permissions are required to use it.
    """


class AutoModEventType(int, Enum):
    """Represents the type of event/context an auto moderation rule will be checked in.

    .. versionadded:: 2.6
    """

    message_send = 1
    """The rule will apply when a member sends or edits a message in the guild."""


class AutoModTriggerType(int, Enum):
    """Represents the type of content that can trigger an auto moderation rule.

    .. versionadded:: 2.6
    """

    keyword = 1
    """The rule will filter messages based on a custom keyword list.

    This trigger type requires additional :class:`metadata <AutoModTriggerMetadata>`.
    """
    harmful_link = 2
    """The rule will filter messages containing malicious links."""
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


EnumT = TypeVar("EnumT", bound=Enum)


def try_enum(cls: Type[EnumT], val: Any) -> EnumT:
    """A function that tries to turn the value into enum ``cls``.
    If it fails it returns a proxy invalid value instead.
    """
    try:
        return cls._value2member_map_[val]  # type: ignore
    except KeyError:
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
