# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Literal, Optional, Set, Union, cast

from .enums import ChannelType, try_enum
from .utils import _get_as_snowflake, get_slots

if TYPE_CHECKING:
    from .channel import VoiceChannelEffect
    from .member import Member
    from .message import Message
    from .partial_emoji import PartialEmoji
    from .threads import Thread, ThreadMember, ThreadType
    from .types.gateway import (
        GuildScheduledEventUserAddEvent,
        GuildScheduledEventUserRemoveEvent,
        IntegrationDeleteEvent,
        MessageDeleteBulkEvent,
        MessageDeleteEvent,
        MessageReactionAddEvent,
        MessageReactionRemoveAllEvent,
        MessageReactionRemoveEmojiEvent,
        MessageReactionRemoveEvent,
        MessageUpdateEvent,
        PollVoteAddEvent,
        PollVoteRemoveEvent,
        PresenceUpdateEvent,
        ThreadDeleteEvent,
        TypingStartEvent,
        VoiceChannelEffectSendEvent,
    )
    from .user import User


__all__ = (
    "RawMessageDeleteEvent",
    "RawBulkMessageDeleteEvent",
    "RawMessageUpdateEvent",
    "RawReactionActionEvent",
    "RawReactionClearEvent",
    "RawReactionClearEmojiEvent",
    "RawIntegrationDeleteEvent",
    "RawGuildScheduledEventUserActionEvent",
    "RawThreadDeleteEvent",
    "RawThreadMemberRemoveEvent",
    "RawTypingEvent",
    "RawGuildMemberRemoveEvent",
    "RawPresenceUpdateEvent",
    "RawPollVoteActionEvent",
    "RawVoiceChannelEffectEvent",
)


class _RawReprMixin:
    __slots__ = ()

    def __repr__(self) -> str:
        value = " ".join(f"{attr}={getattr(self, attr)!r}" for attr in get_slots(type(self)))
        return f"<{type(self).__name__} {value}>"


class RawMessageDeleteEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_message_delete` event.

    Attributes
    ----------
    channel_id: :class:`int`
        The channel ID where the deletion took place.
    guild_id: Optional[:class:`int`]
        The guild ID where the deletion took place, if applicable.
    message_id: :class:`int`
        The message ID that got deleted.
    cached_message: Optional[:class:`Message`]
        The cached message, if found in the internal message cache.
    """

    __slots__ = ("message_id", "channel_id", "guild_id", "cached_message")

    def __init__(self, data: MessageDeleteEvent) -> None:
        self.message_id: int = int(data["id"])
        self.channel_id: int = int(data["channel_id"])
        self.cached_message: Optional[Message] = None
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


class RawBulkMessageDeleteEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_bulk_message_delete` event.

    Attributes
    ----------
    message_ids: Set[:class:`int`]
        A :class:`set` of the message IDs that were deleted.
    channel_id: :class:`int`
        The channel ID where the deletion took place.
    guild_id: Optional[:class:`int`]
        The guild ID where the deletion took place, if applicable.
    cached_messages: List[:class:`Message`]
        The cached messages, if found in the internal message cache.
    """

    __slots__ = ("message_ids", "channel_id", "guild_id", "cached_messages")

    def __init__(self, data: MessageDeleteBulkEvent) -> None:
        self.message_ids: Set[int] = {int(x) for x in data.get("ids", [])}
        self.channel_id: int = int(data["channel_id"])
        self.cached_messages: List[Message] = []
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


class RawMessageUpdateEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_message_edit` event.

    Attributes
    ----------
    message_id: :class:`int`
        The message ID that got updated.
    channel_id: :class:`int`
        The channel ID where the update took place.

        .. versionadded:: 1.3

    guild_id: Optional[:class:`int`]
        The guild ID where the update took place, if applicable.

        .. versionadded:: 1.7

    data: :class:`dict`
        The raw data given by the :ddocs:`gateway <topics/gateway-events#message-update>`.
    cached_message: Optional[:class:`Message`]
        The cached message, if found in the internal message cache. Represents the message before
        it is modified by the data in :attr:`RawMessageUpdateEvent.data`.
    """

    __slots__ = ("message_id", "channel_id", "guild_id", "data", "cached_message")

    def __init__(self, data: MessageUpdateEvent) -> None:
        self.message_id: int = int(data["id"])
        self.channel_id: int = int(data["channel_id"])
        self.data: MessageUpdateEvent = data
        self.cached_message: Optional[Message] = None
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


PollEventType = Literal["POLL_VOTE_ADD", "POLL_VOTE_REMOVE"]


class RawPollVoteActionEvent(_RawReprMixin):
    """Represents the event payload for :func:`on_raw_poll_vote_add` and
    :func:`on_raw_poll_vote_remove` events.

    .. versionadded:: 2.10

    Attributes
    ----------
    message_id: :class:`int`
        The message ID that got or lost a vote.
    user_id: :class:`int`
        The user ID who added the vote or whose vote was removed.
    cached_member: Optional[:class:`Member`]
        The member who added the vote. Available only when the guilds and members are cached.
    channel_id: :class:`int`
        The channel ID where the vote addition or removal took place.
    guild_id: Optional[:class:`int`]
        The guild ID where the vote addition or removal took place, if applicable.
    answer_id: :class:`int`
        The ID of the answer that was voted or unvoted.
    event_type: :class:`str`
        The event type that triggered this action. Can be
        ``POLL_VOTE_ADD`` for vote addition or
        ``POLL_VOTE_REMOVE`` for vote removal.
    """

    __slots__ = (
        "message_id",
        "user_id",
        "cached_member",
        "channel_id",
        "guild_id",
        "event_type",
        "answer_id",
    )

    def __init__(
        self,
        data: Union[PollVoteAddEvent, PollVoteRemoveEvent],
        event_type: PollEventType,
    ) -> None:
        self.message_id: int = int(data["message_id"])
        self.user_id: int = int(data["user_id"])
        self.cached_member: Optional[Member] = None
        self.channel_id: int = int(data["channel_id"])
        self.event_type = event_type
        self.answer_id: int = int(data["answer_id"])
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


ReactionEventType = Literal["REACTION_ADD", "REACTION_REMOVE"]


class RawReactionActionEvent(_RawReprMixin):
    """Represents the event payload for :func:`on_raw_reaction_add` and
    :func:`on_raw_reaction_remove` events.

    Attributes
    ----------
    message_id: :class:`int`
        The message ID that got or lost a reaction.
    user_id: :class:`int`
        The user ID who added the reaction or whose reaction was removed.
    channel_id: :class:`int`
        The channel ID where the reaction addition or removal took place.
    guild_id: Optional[:class:`int`]
        The guild ID where the reaction addition or removal took place, if applicable.
    emoji: :class:`PartialEmoji`
        The custom or unicode emoji being used.

        .. versionchanged:: 2.9
            This now also includes the correct :attr:`~PartialEmoji.animated` value when a reaction was removed.

    member: Optional[:class:`Member`]
        The member who added the reaction. Only available if :attr:`event_type` is ``REACTION_ADD`` and the reaction is inside a guild.

        .. versionadded:: 1.3

    event_type: :class:`str`
        The event type that triggered this action. Can be
        ``REACTION_ADD`` for reaction addition or
        ``REACTION_REMOVE`` for reaction removal.

        .. versionadded:: 1.3

    message_author_id: Optional[:class:`int`]
        The ID of the author who created the message that got a reaction.
        Only available if :attr:`event_type` is ``REACTION_ADD``.
        May also be ``None`` if the message was created by a webhook.

        .. versionadded:: 2.10
    """

    __slots__ = (
        "message_id",
        "user_id",
        "channel_id",
        "guild_id",
        "emoji",
        "event_type",
        "member",
        "message_author_id",
    )

    def __init__(
        self,
        data: Union[MessageReactionAddEvent, MessageReactionRemoveEvent],
        emoji: PartialEmoji,
        event_type: ReactionEventType,
    ) -> None:
        self.message_id: int = int(data["message_id"])
        self.channel_id: int = int(data["channel_id"])
        self.user_id: int = int(data["user_id"])
        self.emoji: PartialEmoji = emoji
        self.event_type: ReactionEventType = event_type
        self.member: Optional[Member] = None
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None
        self.message_author_id: Optional[int] = _get_as_snowflake(data, "message_author_id")


class RawReactionClearEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_reaction_clear` event.

    Attributes
    ----------
    message_id: :class:`int`
        The message ID that got its reactions cleared.
    channel_id: :class:`int`
        The channel ID where the reaction clear took place.
    guild_id: Optional[:class:`int`]
        The guild ID where the reaction clear took place, if applicable.
    """

    __slots__ = ("message_id", "channel_id", "guild_id")

    def __init__(self, data: MessageReactionRemoveAllEvent) -> None:
        self.message_id: int = int(data["message_id"])
        self.channel_id: int = int(data["channel_id"])
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


class RawReactionClearEmojiEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_reaction_clear_emoji` event.

    .. versionadded:: 1.3

    Attributes
    ----------
    message_id: :class:`int`
        The message ID that got its reactions cleared.
    channel_id: :class:`int`
        The channel ID where the reaction clear took place.
    guild_id: Optional[:class:`int`]
        The guild ID where the reaction clear took place, if applicable.
    emoji: :class:`PartialEmoji`
        The custom or unicode emoji being removed.

        .. versionchanged:: 2.9
            This now also includes the correct :attr:`~PartialEmoji.animated` value.
    """

    __slots__ = ("message_id", "channel_id", "guild_id", "emoji")

    def __init__(self, data: MessageReactionRemoveEmojiEvent, emoji: PartialEmoji) -> None:
        self.emoji: PartialEmoji = emoji
        self.message_id: int = int(data["message_id"])
        self.channel_id: int = int(data["channel_id"])
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


class RawIntegrationDeleteEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_integration_delete` event.

    .. versionadded:: 2.0

    Attributes
    ----------
    integration_id: :class:`int`
        The ID of the integration that got deleted.
    application_id: Optional[:class:`int`]
        The ID of the bot/OAuth2 application for this deleted integration.
    guild_id: :class:`int`
        The guild ID where the integration deletion took place.
    """

    __slots__ = ("integration_id", "application_id", "guild_id")

    def __init__(self, data: IntegrationDeleteEvent) -> None:
        self.integration_id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        try:
            self.application_id: Optional[int] = int(data["application_id"])
        except KeyError:
            self.application_id: Optional[int] = None


class RawGuildScheduledEventUserActionEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_guild_scheduled_event_subscribe`
    and :func:`on_raw_guild_scheduled_event_unsubscribe` events.

    .. versionadded:: 2.3

    Attributes
    ----------
    event_id: :class:`int`
        The ID of the guild scheduled event that the user subscribed to or unsubscribed from.
    user_id: :class:`int`
        The ID of the user doing the action.
    guild_id: :class:`int`
        The guild ID where the guild scheduled event is located.
    """

    __slots__ = ("event_id", "user_id", "guild_id")

    def __init__(
        self, data: Union[GuildScheduledEventUserAddEvent, GuildScheduledEventUserRemoveEvent]
    ) -> None:
        self.event_id: int = int(data["guild_scheduled_event_id"])
        self.user_id: int = int(data["user_id"])
        self.guild_id: int = int(data["guild_id"])


class RawThreadDeleteEvent(_RawReprMixin):
    """Represents the payload for a :func:`on_raw_thread_delete` event.

    .. versionadded:: 2.5

    Attributes
    ----------
    thread_id: :class:`int`
        The ID of the thread that was deleted.
    guild_id: :class:`int`
        The ID of the guild the thread was deleted in.
    thread_type: :class:`ChannelType`
        The type of the deleted thread.
    parent_id: :class:`int`
        The ID of the channel the thread belonged to.
    thread: Optional[:class:`Thread`]
        The thread, if it could be found in the internal cache.
    """

    __slots__ = (
        "thread_id",
        "thread_type",
        "parent_id",
        "guild_id",
        "thread",
    )

    def __init__(self, data: ThreadDeleteEvent) -> None:
        self.thread_id: int = int(data["id"])
        self.thread_type: ThreadType = cast("ThreadType", try_enum(ChannelType, data["type"]))
        self.guild_id: int = int(data["guild_id"])
        self.parent_id: int = int(data["parent_id"])
        self.thread: Optional[Thread] = None


class RawThreadMemberRemoveEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_thread_member_remove` event.

    .. versionadded:: 2.5

    Attributes
    ----------
    thread: :class:`Thread`
        The Thread that the member was removed from
    member_id: :class:`int`
        The ID of the removed member.
    cached_member: Optional[:class:`.ThreadMember`]
        The member, if they could be found in the internal cache.
    """

    __slots__ = (
        "thread",
        "member_id",
        "cached_member",
    )

    def __init__(self, thread: Thread, member_id: int) -> None:
        self.thread: Thread = thread
        self.member_id: int = member_id
        self.cached_member: Optional[ThreadMember] = None


class RawTypingEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_typing` event.

    .. versionadded:: 2.3

    Attributes
    ----------
    user_id: :class:`int`
        The ID of the user who started typing.
    channel_id: :class:`int`
        The ID of the channel where the user started typing.
    guild_id: Optional[:class:`int`]
        The ID of the guild where the user started typing or ``None`` if it was in a DM.
    member: Optional[:class:`Member`]
        The member object of the user who started typing or ``None`` if it was in a DM.
    timestamp: :class:`datetime.datetime`
        The UTC datetime when the user started typing.

        .. versionchanged:: 2.9
            Changed from naive to aware datetime.
    """

    __slots__ = ("user_id", "channel_id", "guild_id", "member", "timestamp")

    def __init__(self, data: TypingStartEvent) -> None:
        self.user_id: int = int(data["user_id"])
        self.channel_id: int = int(data["channel_id"])
        self.member: Optional[Member] = None
        self.timestamp: datetime.datetime = datetime.datetime.fromtimestamp(
            data["timestamp"], tz=datetime.timezone.utc
        )
        try:
            self.guild_id: Optional[int] = int(data["guild_id"])
        except KeyError:
            self.guild_id: Optional[int] = None


class RawGuildMemberRemoveEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_member_remove` event.

    .. versionadded:: 2.6

    Attributes
    ----------
    guild_id: :class:`int`
        The ID of the guild where the member was removed from.
    user: Union[:class:`User`, :class:`Member`]
        The user object of the member that was removed.
    """

    __slots__ = (
        "guild_id",
        "user",
    )

    def __init__(self, user: Union[User, Member], guild_id: int) -> None:
        self.user: Union[User, Member] = user
        self.guild_id: int = guild_id


class RawPresenceUpdateEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_presence_update` event.

    .. versionadded:: 2.10

    Attributes
    ----------
    user_id: :class:`int`
        The ID of the user whose presence was updated.
    guild_id: :class:`int`
        The ID of the guild where the user's presence changed.
    data: :class:`dict`
        The raw data given by the :ddocs:`gateway <topics/gateway-events#presence-update>`.
    """

    __slots__ = (
        "user_id",
        "guild_id",
        "data",
    )

    def __init__(self, data: PresenceUpdateEvent) -> None:
        self.user_id: int = int(data["user"]["id"])
        self.guild_id: int = int(data["guild_id"])
        self.data: PresenceUpdateEvent = data


class RawVoiceChannelEffectEvent(_RawReprMixin):
    """Represents the event payload for an :func:`on_raw_voice_channel_effect` event.

    .. versionadded:: 2.10

    Attributes
    ----------
    channel_id: :class:`int`
        The ID of the channel where the effect was sent.
    guild_id: :class:`int`
        The ID of the guild where the effect was sent.
    user_id: :class:`int`
        The ID of the user who sent the effect.
    effect: :class:`VoiceChannelEffect`
        The effect that was sent.
    cached_member: Optional[:class:`Member`]
        The member who sent the effect, if they could be found in the internal cache.
    """

    __slots__ = (
        "channel_id",
        "guild_id",
        "user_id",
        "effect",
        "cached_member",
    )

    def __init__(self, data: VoiceChannelEffectSendEvent, effect: VoiceChannelEffect) -> None:
        self.channel_id: int = int(data["channel_id"])
        self.guild_id: int = int(data["guild_id"])
        self.user_id: int = int(data["user_id"])
        self.effect: VoiceChannelEffect = effect

        self.cached_member: Optional[Member] = None
