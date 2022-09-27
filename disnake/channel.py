# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import datetime
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

import disnake.abc

from . import utils
from .asset import Asset
from .context_managers import Typing
from .enums import (
    ChannelType,
    StagePrivacyLevel,
    ThreadSortOrder,
    VideoQualityMode,
    try_enum,
    try_enum_to_int,
)
from .errors import ClientException
from .file import File
from .flags import ChannelFlags
from .iterators import ArchivedThreadIterator
from .mixins import Hashable
from .partial_emoji import PartialEmoji
from .permissions import PermissionOverwrite, Permissions
from .stage_instance import StageInstance
from .threads import ForumTag, Thread
from .utils import MISSING

__all__ = (
    "TextChannel",
    "VoiceChannel",
    "StageChannel",
    "DMChannel",
    "CategoryChannel",
    "NewsChannel",
    "ForumChannel",
    "GroupChannel",
    "PartialMessageable",
)

if TYPE_CHECKING:
    from typing_extensions import Never, Self

    from .abc import Snowflake, SnowflakeTime
    from .asset import AssetBytes
    from .embeds import Embed
    from .emoji import Emoji
    from .guild import Guild, GuildChannel as GuildChannelType
    from .member import Member, VoiceState
    from .message import AllowedMentions, Message, PartialMessage
    from .role import Role
    from .state import ConnectionState
    from .sticker import GuildSticker, StickerItem
    from .threads import AnyThreadArchiveDuration, ThreadType
    from .types.channel import (
        CategoryChannel as CategoryChannelPayload,
        DMChannel as DMChannelPayload,
        ForumChannel as ForumChannelPayload,
        GroupDMChannel as GroupChannelPayload,
        StageChannel as StageChannelPayload,
        TextChannel as TextChannelPayload,
        VoiceChannel as VoiceChannelPayload,
    )
    from .types.snowflake import SnowflakeList
    from .types.threads import ThreadArchiveDurationLiteral
    from .ui.action_row import Components, MessageUIComponent
    from .ui.view import View
    from .user import BaseUser, ClientUser, User
    from .voice_region import VoiceRegion
    from .webhook import Webhook


async def _single_delete_strategy(messages: Iterable[Message]):
    for m in messages:
        await m.delete()


class TextChannel(disnake.abc.Messageable, disnake.abc.GuildChannel, Hashable):
    """Represents a Discord guild text channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns the channel's name.

    Attributes
    ----------
    name: :class:`str`
        The channel's name.
    guild: :class:`Guild`
        The guild the channel belongs to.
    id: :class:`int`
        The channel's ID.
    category_id: Optional[:class:`int`]
        The category channel ID this channel belongs to, if applicable.
    topic: Optional[:class:`str`]
        The channel's topic. ``None`` if it doesn't exist.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0. e.g. the
        top channel is position 0.
    last_message_id: Optional[:class:`int`]
        The last message ID of the message sent to this channel. It may
        *not* point to an existing or valid message.
    slowmode_delay: :class:`int`
        The number of seconds a member must wait between sending messages
        in this channel. A value of `0` denotes that it is disabled.
        Bots, and users with :attr:`~Permissions.manage_channels` or
        :attr:`~Permissions.manage_messages` permissions, bypass slowmode.
    nsfw: :class:`bool`
        Whether the channel is marked as "not safe for work".

        .. note::

            To check if the channel or the guild of that channel are marked as NSFW, consider :meth:`is_nsfw` instead.
    default_auto_archive_duration: :class:`int`
        The default auto archive duration in minutes for threads created in this channel.

        .. versionadded:: 2.0

    last_pin_timestamp: Optional[:class:`datetime.datetime`]
        The time the most recent message was pinned, or ``None`` if no message is currently pinned.

        .. versionadded:: 2.5
    """

    __slots__ = (
        "name",
        "id",
        "guild",
        "topic",
        "_state",
        "nsfw",
        "category_id",
        "position",
        "slowmode_delay",
        "last_message_id",
        "default_auto_archive_duration",
        "last_pin_timestamp",
        "_overwrites",
        "_flags",
        "_type",
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: TextChannelPayload):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._type: Literal[0, 5] = data["type"]
        self._update(guild, data)

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("name", self.name),
            ("position", self.position),
            ("nsfw", self.nsfw),
            ("news", self.is_news()),
            ("category_id", self.category_id),
            ("default_auto_archive_duration", self.default_auto_archive_duration),
            ("flags", self.flags),
        )
        joined = " ".join(f"{k!s}={v!r}" for k, v in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def _update(self, guild: Guild, data: TextChannelPayload) -> None:
        self.guild: Guild = guild
        # apparently this can be nullable in the case of a bad api deploy
        self.name: str = data.get("name") or ""
        self.category_id: Optional[int] = utils._get_as_snowflake(data, "parent_id")
        self.topic: Optional[str] = data.get("topic")
        self.position: int = data["position"]
        self._flags = data.get("flags", 0)
        self.nsfw: bool = data.get("nsfw", False)
        # Does this need coercion into `int`? No idea yet.
        self.slowmode_delay: int = data.get("rate_limit_per_user", 0)
        self.default_auto_archive_duration: ThreadArchiveDurationLiteral = data.get(
            "default_auto_archive_duration", 1440
        )
        self._type: Literal[0, 5] = data.get("type", self._type)
        self.last_message_id: Optional[int] = utils._get_as_snowflake(data, "last_message_id")
        self.last_pin_timestamp: Optional[datetime.datetime] = utils.parse_time(
            data.get("last_pin_timestamp")
        )
        self._fill_overwrites(data)

    async def _get_channel(self):
        return self

    @property
    def type(self) -> Literal[ChannelType.text, ChannelType.news]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.text` or :attr:`ChannelType.news`.
        """
        if self._type == ChannelType.text.value:
            return ChannelType.text
        return ChannelType.news

    @property
    def _sorting_bucket(self) -> int:
        return ChannelType.text.value

    @utils.copy_doc(disnake.abc.GuildChannel.permissions_for)
    def permissions_for(
        self,
        obj: Union[Member, Role],
        /,
        *,
        ignore_timeout: bool = MISSING,
    ) -> Permissions:
        base = super().permissions_for(obj, ignore_timeout=ignore_timeout)

        # text channels do not have voice related permissions
        denied = Permissions.voice()
        base.value &= ~denied.value
        return base

    @property
    def members(self) -> List[Member]:
        """List[:class:`Member`]: Returns all members that can see this channel."""
        return [m for m in self.guild.members if self.permissions_for(m).view_channel]

    @property
    def threads(self) -> List[Thread]:
        """List[:class:`Thread`]: Returns all the threads that you can see.

        .. versionadded:: 2.0
        """
        return [thread for thread in self.guild._threads.values() if thread.parent_id == self.id]

    def is_nsfw(self) -> bool:
        """Whether the channel is marked as NSFW.

        :return type: :class:`bool`
        """
        return self.nsfw

    def is_news(self) -> bool:
        """Whether the channel is a news channel.

        :return type: :class:`bool`
        """
        return self._type == ChannelType.news.value

    @property
    def last_message(self) -> Optional[Message]:
        """Gets the last message in this channel from the cache.

        The message might not be valid or point to an existing message.

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last message, consider using either :meth:`history`
            or :meth:`fetch_message` with the :attr:`last_message_id`
            attribute.

        Returns
        -------
        Optional[:class:`Message`]
            The last message in this channel or ``None`` if not found.
        """
        return self._state._get_message(self.last_message_id) if self.last_message_id else None

    # if only these parameters are passed, `_move` is called and no channel will be returned
    @overload
    async def edit(
        self,
        *,
        position: int,
        category: Optional[Snowflake] = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    # only passing `sync_permissions` may or may not return a channel,
    # depending on whether the channel is in a category
    @overload
    async def edit(
        self,
        *,
        sync_permissions: bool,
        reason: Optional[str] = ...,
    ) -> Optional[TextChannel]:
        ...

    @overload
    async def edit(
        self,
        *,
        name: str = ...,
        topic: Optional[str] = ...,
        position: int = ...,
        nsfw: bool = ...,
        sync_permissions: bool = ...,
        category: Optional[Snowflake] = ...,
        slowmode_delay: Optional[int] = ...,
        default_auto_archive_duration: Optional[AnyThreadArchiveDuration] = ...,
        type: ChannelType = ...,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
        flags: ChannelFlags = ...,
        reason: Optional[str] = ...,
    ) -> TextChannel:
        ...

    async def edit(
        self,
        *,
        name: str = MISSING,
        topic: Optional[str] = MISSING,
        position: int = MISSING,
        nsfw: bool = MISSING,
        sync_permissions: bool = MISSING,
        category: Optional[Snowflake] = MISSING,
        slowmode_delay: Optional[int] = MISSING,
        default_auto_archive_duration: Optional[AnyThreadArchiveDuration] = MISSING,
        type: ChannelType = MISSING,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = MISSING,
        flags: ChannelFlags = MISSING,
        reason: Optional[str] = None,
        **kwargs: Never,
    ) -> Optional[TextChannel]:
        """|coro|

        Edits the channel.

        You must have :attr:`~Permissions.manage_channels` permission to
        do this.

        .. versionchanged:: 1.3
            The ``overwrites`` keyword-only parameter was added.

        .. versionchanged:: 1.4
            The ``type`` keyword-only parameter was added.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited channel is returned instead.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` or :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        name: :class:`str`
            The new channel's name.
        topic: Optional[:class:`str`]
            The new channel's topic.
        position: :class:`int`
            The new channel's position.
        nsfw: :class:`bool`
            Whether to mark the channel as NSFW.
        sync_permissions: :class:`bool`
            Whether to sync permissions with the channel's new or pre-existing
            category. Defaults to ``False``.
        category: Optional[:class:`abc.Snowflake`]
            The new category for this channel. Can be ``None`` to remove the
            category.
        slowmode_delay: Optional[:class:`int`]
            Specifies the slowmode rate limit for users in this channel, in seconds.
            A value of ``0`` disables slowmode. The maximum value possible is ``21600``.
        type: :class:`ChannelType`
            The new type of this text channel. Currently, only conversion between
            :attr:`ChannelType.text` and :attr:`ChannelType.news` is supported. This
            is only available to guilds that contain ``NEWS`` in :attr:`Guild.features`.
        overwrites: :class:`Mapping`
            A :class:`Mapping` of target (either a role or a member) to
            :class:`PermissionOverwrite` to apply to the channel.
        default_auto_archive_duration: Optional[Union[:class:`int`, :class:`ThreadArchiveDuration`]]
            The new default auto archive duration in minutes for threads created in this channel.
            Must be one of ``60``, ``1440``, ``4320``, or ``10080``.
        flags: :class:`ChannelFlags`
            The new flags to set for this channel. This will overwrite any existing flags set on this channel.

            .. versionadded:: 2.6

        reason: Optional[:class:`str`]
            The reason for editing this channel. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to edit the channel.
        HTTPException
            Editing the channel failed.
        TypeError
            The permission overwrite information is not in proper form.
        ValueError
            The position is less than 0.

        Returns
        -------
        Optional[:class:`.TextChannel`]
            The newly edited text channel. If the edit was only positional
            then ``None`` is returned instead.
        """
        payload = await self._edit(
            name=name,
            topic=topic,
            position=position,
            nsfw=nsfw,
            sync_permissions=sync_permissions,
            category=category,
            slowmode_delay=slowmode_delay,
            default_auto_archive_duration=default_auto_archive_duration,
            type=type,
            overwrites=overwrites,
            flags=flags,
            reason=reason,
            **kwargs,
        )
        if payload is not None:
            # the payload will always be the proper channel payload
            return self.__class__(state=self._state, guild=self.guild, data=payload)  # type: ignore

    @utils.copy_doc(disnake.abc.GuildChannel.clone)
    async def clone(
        self, *, name: Optional[str] = None, reason: Optional[str] = None
    ) -> TextChannel:
        return await self._clone_impl(
            {"topic": self.topic, "nsfw": self.nsfw, "rate_limit_per_user": self.slowmode_delay},
            name=name,
            reason=reason,
        )

    async def delete_messages(self, messages: Iterable[Snowflake]) -> None:
        """|coro|

        Deletes a list of messages. This is similar to :meth:`Message.delete`
        except it bulk deletes multiple messages.

        As a special case, if the number of messages is 0, then nothing
        is done. If the number of messages is 1 then single message
        delete is done. If it's more than two, then bulk delete is used.

        You cannot bulk delete more than 100 messages or messages that
        are older than 14 days.

        You must have :attr:`~Permissions.manage_messages` permission to
        do this.

        Parameters
        ----------
        messages: Iterable[:class:`abc.Snowflake`]
            An iterable of messages denoting which ones to bulk delete.

        Raises
        ------
        ClientException
            The number of messages to delete was more than 100.
        Forbidden
            You do not have proper permissions to delete the messages.
        NotFound
            If single delete, then the message was already deleted.
        HTTPException
            Deleting the messages failed.
        """
        if not isinstance(messages, (list, tuple)):
            messages = list(messages)

        if len(messages) == 0:
            return  # do nothing

        if len(messages) == 1:
            message_id: int = messages[0].id
            await self._state.http.delete_message(self.id, message_id)
            return

        if len(messages) > 100:
            raise ClientException("Can only bulk delete messages up to 100 messages")

        message_ids: SnowflakeList = [m.id for m in messages]
        await self._state.http.delete_messages(self.id, message_ids)

    async def purge(
        self,
        *,
        limit: Optional[int] = 100,
        check: Callable[[Message], bool] = MISSING,
        before: Optional[SnowflakeTime] = None,
        after: Optional[SnowflakeTime] = None,
        around: Optional[SnowflakeTime] = None,
        oldest_first: Optional[bool] = False,
        bulk: bool = True,
    ) -> List[Message]:
        """|coro|

        Purges a list of messages that meet the criteria given by the predicate
        ``check``. If a ``check`` is not provided then all messages are deleted
        without discrimination.

        You must have :attr:`~Permissions.manage_messages` permission to
        delete messages even if they are your own.
        :attr:`~Permissions.read_message_history` permission is
        also needed to retrieve message history.

        Examples
        --------

        Deleting bot's messages ::

            def is_me(m):
                return m.author == client.user

            deleted = await channel.purge(limit=100, check=is_me)
            await channel.send(f'Deleted {len(deleted)} message(s)')

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of messages to search through. This is not the number
            of messages that will be deleted, though it can be.
        check: Callable[[:class:`Message`], :class:`bool`]
            The function used to check if a message should be deleted.
            It must take a :class:`Message` as its sole parameter.
        before: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Same as ``before`` in :meth:`history`.
        after: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Same as ``after`` in :meth:`history`.
        around: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Same as ``around`` in :meth:`history`.
        oldest_first: Optional[:class:`bool`]
            Same as ``oldest_first`` in :meth:`history`.
        bulk: :class:`bool`
            If ``True``, use bulk delete. Setting this to ``False`` is useful for mass-deleting
            a bot's own messages without :attr:`Permissions.manage_messages`. When ``True``, will
            fall back to single delete if messages are older than two weeks.

        Raises
        ------
        Forbidden
            You do not have proper permissions to do the actions required.
        HTTPException
            Purging the messages failed.

        Returns
        -------
        List[:class:`.Message`]
            A list of messages that were deleted.
        """
        if check is MISSING:
            check = lambda m: True

        iterator = self.history(
            limit=limit, before=before, after=after, oldest_first=oldest_first, around=around
        )
        ret: List[Message] = []
        count = 0

        minimum_time = int((time.time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
        strategy = self.delete_messages if bulk else _single_delete_strategy

        async for message in iterator:
            if count == 100:
                to_delete = ret[-100:]
                await strategy(to_delete)
                count = 0
                await asyncio.sleep(1)

            if not check(message):
                continue

            if message.id < minimum_time:
                # older than 14 days old
                if count == 1:
                    await ret[-1].delete()
                elif count >= 2:
                    to_delete = ret[-count:]
                    await strategy(to_delete)

                count = 0
                strategy = _single_delete_strategy

            count += 1
            ret.append(message)

        # SOme messages remaining to poll
        if count >= 2:
            # more than 2 messages -> bulk delete
            to_delete = ret[-count:]
            await strategy(to_delete)
        elif count == 1:
            # delete a single message
            await ret[-1].delete()

        return ret

    async def webhooks(self) -> List[Webhook]:
        """|coro|

        Retrieves the list of webhooks this channel has.

        You must have :attr:`~.Permissions.manage_webhooks` permission to
        use this.

        Raises
        ------
        Forbidden
            You don't have permissions to get the webhooks.

        Returns
        -------
        List[:class:`Webhook`]
            The list of webhooks this channel has.
        """
        from .webhook import Webhook

        data = await self._state.http.channel_webhooks(self.id)
        return [Webhook.from_state(d, state=self._state) for d in data]

    async def create_webhook(
        self, *, name: str, avatar: Optional[AssetBytes] = None, reason: Optional[str] = None
    ) -> Webhook:
        """|coro|

        Creates a webhook for this channel.

        You must have :attr:`~.Permissions.manage_webhooks` permission to
        do this.

        .. versionchanged:: 1.1
            The ``reason`` keyword-only parameter was added.

        Parameters
        ----------
        name: :class:`str`
            The webhook's name.
        avatar: Optional[|resource_type|]
            The webhook's default avatar.
            This operates similarly to :meth:`~ClientUser.edit`.

            .. versionchanged:: 2.5
                Now accepts various resource types in addition to :class:`bytes`.

        reason: Optional[:class:`str`]
            The reason for creating this webhook. Shows up in the audit logs.

        Raises
        ------
        NotFound
            The ``avatar`` asset couldn't be found.
        Forbidden
            You do not have permissions to create a webhook.
        HTTPException
            Creating the webhook failed.
        TypeError
            The ``avatar`` asset is a lottie sticker (see :func:`Sticker.read`).

        Returns
        -------
        :class:`Webhook`
            The newly created webhook.
        """
        from .webhook import Webhook

        avatar_data = await utils._assetbytes_to_base64_data(avatar)

        data = await self._state.http.create_webhook(
            self.id, name=str(name), avatar=avatar_data, reason=reason
        )
        return Webhook.from_state(data, state=self._state)

    async def follow(self, *, destination: TextChannel, reason: Optional[str] = None) -> Webhook:
        """|coro|

        Follows a channel using a webhook.

        Only news channels can be followed.

        .. note::

            The webhook returned will not provide a token to do webhook
            actions, as Discord does not provide it.

        .. versionadded:: 1.3

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` instead of ``InvalidArgument``.

        Parameters
        ----------
        destination: :class:`TextChannel`
            The channel you would like to follow from.
        reason: Optional[:class:`str`]
            The reason for following the channel. Shows up on the destination guild's audit log.

            .. versionadded:: 1.4

        Raises
        ------
        HTTPException
            Following the channel failed.
        Forbidden
            You do not have the permissions to create a webhook.
        TypeError
            The current or provided channel is not of the correct type.

        Returns
        -------
        :class:`Webhook`
            The newly created webhook.
        """
        if not self.is_news():
            raise TypeError("This channel must be a news channel.")

        if not isinstance(destination, TextChannel):
            raise TypeError(f"Expected TextChannel received {destination.__class__.__name__}")

        from .webhook import Webhook

        data = await self._state.http.follow_webhook(
            self.id, webhook_channel_id=destination.id, reason=reason
        )
        return Webhook._as_follower(data, channel=destination, user=self._state.user)

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the given message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        .. versionadded:: 1.6

        Parameters
        ----------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        -------
        :class:`PartialMessage`
            The partial message object.
        """
        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)

    def get_thread(self, thread_id: int, /) -> Optional[Thread]:
        """Returns a thread with the given ID.

        .. versionadded:: 2.0

        Parameters
        ----------
        thread_id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`Thread`]
            The returned thread or ``None`` if not found.
        """
        return self.guild.get_thread(thread_id)

    @overload
    async def create_thread(
        self,
        *,
        name: str,
        message: Snowflake,
        auto_archive_duration: Optional[AnyThreadArchiveDuration] = None,
        slowmode_delay: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Thread:
        ...

    @overload
    async def create_thread(
        self,
        *,
        name: str,
        type: ThreadType,
        auto_archive_duration: Optional[AnyThreadArchiveDuration] = None,
        invitable: Optional[bool] = None,
        slowmode_delay: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Thread:
        ...

    async def create_thread(
        self,
        *,
        name: str,
        message: Optional[Snowflake] = None,
        auto_archive_duration: Optional[AnyThreadArchiveDuration] = None,
        type: Optional[ThreadType] = None,
        invitable: Optional[bool] = None,
        slowmode_delay: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Thread:
        """|coro|

        Creates a thread in this text channel.

        To create a public thread, you must have :attr:`~disnake.Permissions.create_public_threads` permission.
        For a private thread, :attr:`~disnake.Permissions.create_private_threads` permission is needed instead.
        Additionally, the guild must have ``PRIVATE_THREADS`` in :attr:`Guild.features` to create private threads.

        .. versionadded:: 2.0

        .. versionchanged:: 2.5

            - Only one of ``message`` and ``type`` may be provided.
            - ``type`` is now required if ``message`` is not provided.


        Parameters
        ----------
        name: :class:`str`
            The name of the thread.
        message: :class:`abc.Snowflake`
            A snowflake representing the message to create the thread with.

            .. versionchanged:: 2.5

                Cannot be provided with ``type``.

        type: :class:`ChannelType`
            The type of thread to create.

            .. versionchanged:: 2.5

                Cannot be provided with ``message``.
                Now required if message is not provided.

        auto_archive_duration: Union[:class:`int`, :class:`ThreadArchiveDuration`]
            The duration in minutes before a thread is automatically archived for inactivity.
            If not provided, the channel's default auto archive duration is used.
            Must be one of ``60``, ``1440``, ``4320``, or ``10080``.
        invitable: :class:`bool`
            Whether non-moderators can add other non-moderators to this thread.
            Only available for private threads.
            If a ``message`` is passed then this parameter is ignored, as a thread
            created with a message is always a public thread.
            Defaults to ``True``.

            .. versionadded:: 2.3

        slowmode_delay: :class:`int`
            Specifies the slowmode rate limit for users in this thread, in seconds.
            A value of ``0`` disables slowmode. The maximum value possible is ``21600``.
            If not provided, slowmode is disabled.

            .. versionadded:: 2.3

        reason: Optional[:class:`str`]
            The reason for creating the thread. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to create a thread.
        HTTPException
            Starting the thread failed.

        Returns
        -------
        :class:`Thread`
            The newly created thread
        """
        if not ((message is None) ^ (type is None)):
            raise ValueError("Exactly one of message and type must be provided.")

        if auto_archive_duration is not None:
            auto_archive_duration = cast(
                "ThreadArchiveDurationLiteral", try_enum_to_int(auto_archive_duration)
            )

        if message is None:
            data = await self._state.http.start_thread_without_message(
                self.id,
                name=name,
                auto_archive_duration=auto_archive_duration or self.default_auto_archive_duration,
                type=type.value,  # type: ignore
                invitable=invitable if invitable is not None else True,
                rate_limit_per_user=slowmode_delay or 0,
                reason=reason,
            )
        else:
            data = await self._state.http.start_thread_with_message(
                self.id,
                message.id,
                name=name,
                auto_archive_duration=auto_archive_duration or self.default_auto_archive_duration,
                rate_limit_per_user=slowmode_delay or 0,
                reason=reason,
            )

        return Thread(guild=self.guild, state=self._state, data=data)

    def archived_threads(
        self,
        *,
        private: bool = False,
        joined: bool = False,
        limit: Optional[int] = 50,
        before: Optional[Union[Snowflake, datetime.datetime]] = None,
    ) -> ArchivedThreadIterator:
        """Returns an :class:`~disnake.AsyncIterator` that iterates over all archived threads in the channel.

        You must have :attr:`~Permissions.read_message_history` permission to use this. If iterating over private threads
        then :attr:`~Permissions.manage_threads` permission is also required.

        .. versionadded:: 2.0

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of threads to retrieve.
            If ``None``, retrieves every archived thread in the channel. Note, however,
            that this would make it a slow operation.
        before: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve archived channels before the given date or ID.
        private: :class:`bool`
            Whether to retrieve private archived threads.
        joined: :class:`bool`
            Whether to retrieve private archived threads that you've joined.
            You cannot set ``joined`` to ``True`` and ``private`` to ``False``.

        Raises
        ------
        Forbidden
            You do not have permissions to get archived threads.
        HTTPException
            The request to get the archived threads failed.

        Yields
        -------
        :class:`Thread`
            The archived threads.
        """
        return ArchivedThreadIterator(
            self.id, self.guild, limit=limit, joined=joined, private=private, before=before
        )


class VocalGuildChannel(disnake.abc.Connectable, disnake.abc.GuildChannel, Hashable):
    __slots__ = (
        "name",
        "id",
        "guild",
        "bitrate",
        "user_limit",
        "_state",
        "position",
        "_overwrites",
        "category_id",
        "rtc_region",
        "video_quality_mode",
        "_flags",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        guild: Guild,
        data: Union[VoiceChannelPayload, StageChannelPayload],
    ):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._update(guild, data)

    def _get_voice_client_key(self) -> Tuple[int, str]:
        return self.guild.id, "guild_id"

    def _get_voice_state_pair(self) -> Tuple[int, int]:
        return self.guild.id, self.id

    def _update(self, guild: Guild, data: Union[VoiceChannelPayload, StageChannelPayload]) -> None:
        self.guild = guild
        # apparently this can be nullable in the case of a bad api deploy
        self.name: str = data.get("name") or ""
        rtc = data.get("rtc_region")
        self.rtc_region: Optional[str] = rtc
        self.video_quality_mode: VideoQualityMode = try_enum(
            VideoQualityMode, data.get("video_quality_mode", 1)
        )
        self._flags = data.get("flags", 0)
        self.category_id: Optional[int] = utils._get_as_snowflake(data, "parent_id")
        self.position: int = data["position"]
        # these don't exist in partial channel objects of slash command options
        self.bitrate: int = data.get("bitrate", 0)
        self.user_limit: int = data.get("user_limit", 0)
        self._fill_overwrites(data)

    @property
    def _sorting_bucket(self) -> int:
        return ChannelType.voice.value

    @property
    def members(self) -> List[Member]:
        """List[:class:`Member`]: Returns all members that are currently inside this voice channel."""
        ret = []
        for user_id, state in self.guild._voice_states.items():
            if state.channel and state.channel.id == self.id:
                member = self.guild.get_member(user_id)
                if member is not None:
                    ret.append(member)
        return ret

    @property
    def voice_states(self) -> Dict[int, VoiceState]:
        """Returns a mapping of member IDs who have voice states in this channel.

        .. versionadded:: 1.3

        .. note::

            This function is intentionally low level to replace :attr:`members`
            when the member cache is unavailable.

        Returns
        -------
        Mapping[:class:`int`, :class:`VoiceState`]
            The mapping of member ID to a voice state.
        """
        return {
            key: value
            for key, value in self.guild._voice_states.items()
            if value.channel and value.channel.id == self.id
        }


class VoiceChannel(disnake.abc.Messageable, VocalGuildChannel):
    """Represents a Discord guild voice channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns the channel's name.

    Attributes
    ----------
    name: :class:`str`
        The channel's name.
    guild: :class:`Guild`
        The guild the channel belongs to.
    id: :class:`int`
        The channel's ID.
    category_id: Optional[:class:`int`]
        The category channel ID this channel belongs to, if applicable.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0. e.g. the
        top channel is position 0.
    bitrate: :class:`int`
        The channel's preferred audio bitrate in bits per second.
    user_limit: :class:`int`
        The channel's limit for number of members that can be in a voice channel.
    rtc_region: Optional[:class:`str`]
        The region for the voice channel's voice communication.
        A value of ``None`` indicates automatic voice region detection.

        .. versionadded:: 1.7

        .. versionchanged:: 2.5
            No longer a ``VoiceRegion`` instance.

    video_quality_mode: :class:`VideoQualityMode`
        The camera video quality for the voice channel's participants.
    nsfw: :class:`bool`
        Whether the channel is marked as "not safe for work".

        .. note::

            To check if the channel or the guild of that channel are marked as NSFW, consider :meth:`is_nsfw` instead.

        .. versionadded:: 2.3

    slowmode_delay: :class:`int`
        The number of seconds a member must wait between sending messages
        in this channel. A value of `0` denotes that it is disabled.
        Bots, and users with :attr:`~Permissions.manage_channels` or
        :attr:`~Permissions.manage_messages`, bypass slowmode.

        .. versionadded:: 2.3

    last_message_id: Optional[:class:`int`]
        The last message ID of the message sent to this channel. It may
        *not* point to an existing or valid message.

        .. versionadded:: 2.3
    """

    __slots__ = (
        "nsfw",
        "slowmode_delay",
        "last_message_id",
    )

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("name", self.name),
            ("rtc_region", self.rtc_region),
            ("position", self.position),
            ("bitrate", self.bitrate),
            ("video_quality_mode", self.video_quality_mode),
            ("user_limit", self.user_limit),
            ("category_id", self.category_id),
            ("nsfw", self.nsfw),
            ("flags", self.flags),
        )
        joined = " ".join(f"{k!s}={v!r}" for k, v in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def _update(self, guild: Guild, data: VoiceChannelPayload) -> None:
        super()._update(guild, data)
        self.nsfw: bool = data.get("nsfw", False)
        self.slowmode_delay: int = data.get("rate_limit_per_user", 0)
        self.last_message_id: Optional[int] = utils._get_as_snowflake(data, "last_message_id")

    async def _get_channel(self):
        return self

    @property
    def type(self) -> Literal[ChannelType.voice]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.voice`.
        """
        return ChannelType.voice

    @utils.copy_doc(disnake.abc.GuildChannel.clone)
    async def clone(
        self, *, name: Optional[str] = None, reason: Optional[str] = None
    ) -> VoiceChannel:
        return await self._clone_impl(
            {"bitrate": self.bitrate, "user_limit": self.user_limit}, name=name, reason=reason
        )

    def is_nsfw(self) -> bool:
        """Whether the channel is marked as NSFW.

        .. versionadded:: 2.3

        :return type: :class:`bool`
        """
        return self.nsfw

    @property
    def last_message(self) -> Optional[Message]:
        """Gets the last message in this channel from the cache.

        The message might not be valid or point to an existing message.

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last message, consider using either :meth:`history`
            or :meth:`fetch_message` with the :attr:`last_message_id`
            attribute.

        .. versionadded:: 2.3

        Returns
        -------
        Optional[:class:`Message`]
            The last message in this channel or ``None`` if not found.
        """
        return self._state._get_message(self.last_message_id) if self.last_message_id else None

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the given message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        .. versionadded:: 2.3

        Parameters
        ----------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        -------
        :class:`PartialMessage`
            The partial message object.
        """
        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)

    @utils.copy_doc(disnake.abc.GuildChannel.permissions_for)
    def permissions_for(
        self,
        obj: Union[Member, Role],
        /,
        *,
        ignore_timeout: bool = MISSING,
    ) -> Permissions:
        base = super().permissions_for(obj, ignore_timeout=ignore_timeout)

        # voice channels cannot be edited by people who can't connect to them
        # It also implicitly denies all other voice perms
        if not base.connect:
            denied = Permissions.voice()
            # voice channels also deny all text related permissions
            denied.value |= Permissions.text().value
            denied.update(manage_channels=True, manage_roles=True)
            base.value &= ~denied.value
        return base

    # if only these parameters are passed, `_move` is called and no channel will be returned
    @overload
    async def edit(
        self,
        *,
        position: int,
        category: Optional[Snowflake] = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    # only passing `sync_permissions` may or may not return a channel,
    # depending on whether the channel is in a category
    @overload
    async def edit(
        self,
        *,
        sync_permissions: bool,
        reason: Optional[str] = ...,
    ) -> Optional[VoiceChannel]:
        ...

    @overload
    async def edit(
        self,
        *,
        name: str = ...,
        bitrate: int = ...,
        user_limit: int = ...,
        position: int = ...,
        sync_permissions: bool = ...,
        category: Optional[Snowflake] = ...,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
        rtc_region: Optional[Union[str, VoiceRegion]] = ...,
        video_quality_mode: VideoQualityMode = ...,
        nsfw: bool = ...,
        slowmode_delay: Optional[int] = ...,
        flags: ChannelFlags = ...,
        reason: Optional[str] = ...,
    ) -> VoiceChannel:
        ...

    async def edit(
        self,
        *,
        name: str = MISSING,
        bitrate: int = MISSING,
        user_limit: int = MISSING,
        position: int = MISSING,
        sync_permissions: bool = MISSING,
        category: Optional[Snowflake] = MISSING,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = MISSING,
        rtc_region: Optional[Union[str, VoiceRegion]] = MISSING,
        video_quality_mode: VideoQualityMode = MISSING,
        nsfw: bool = MISSING,
        slowmode_delay: Optional[int] = MISSING,
        flags: ChannelFlags = MISSING,
        reason: Optional[str] = None,
        **kwargs: Never,
    ) -> Optional[VoiceChannel]:
        """|coro|

        Edits the channel.

        You must have :attr:`~Permissions.manage_channels` permission to
        do this.

        .. versionchanged:: 1.3
            The ``overwrites`` keyword-only parameter was added.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited channel is returned instead.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` or :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        name: :class:`str`
            The new channel's name.
        bitrate: :class:`int`
            The new channel's bitrate.
        user_limit: :class:`int`
            The new channel's user limit.
        position: :class:`int`
            The new channel's position.
        sync_permissions: :class:`bool`
            Whether to sync permissions with the channel's new or pre-existing
            category. Defaults to ``False``.
        category: Optional[:class:`abc.Snowflake`]
            The new category for this channel. Can be ``None`` to remove the
            category.
        reason: Optional[:class:`str`]
            The reason for editing this channel. Shows up on the audit log.
        overwrites: :class:`Mapping`
            A :class:`Mapping` of target (either a role or a member) to
            :class:`PermissionOverwrite` to apply to the channel.
        rtc_region: Optional[Union[:class:`str`, :class:`VoiceRegion`]]
            The new region for the voice channel's voice communication.
            A value of ``None`` indicates automatic voice region detection.

            .. versionadded:: 1.7

        video_quality_mode: :class:`VideoQualityMode`
            The camera video quality for the voice channel's participants.

            .. versionadded:: 2.0

        nsfw: :class:`bool`
            Whether to mark the channel as NSFW.

            .. versionadded:: 2.3

        slowmode_delay: Optional[:class:`int`]
            Specifies the slowmode rate limit for users in this channel, in seconds.
            A value of ``0`` disables slowmode. The maximum value possible is ``21600``.

            .. versionadded:: 2.3

        flags: :class:`ChannelFlags`
            The new flags to set for this channel. This will overwrite any existing flags set on this channel.

            .. versionadded:: 2.6

        Raises
        ------
        Forbidden
            You do not have permissions to edit the channel.
        HTTPException
            Editing the channel failed.
        TypeError
            The permission overwrite information is not in proper form.
        ValueError
            The position is less than 0.

        Returns
        -------
        Optional[:class:`.VoiceChannel`]
            The newly edited voice channel. If the edit was only positional
            then ``None`` is returned instead.
        """
        payload = await self._edit(
            name=name,
            bitrate=bitrate,
            user_limit=user_limit,
            position=position,
            sync_permissions=sync_permissions,
            category=category,
            overwrites=overwrites,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            nsfw=nsfw,
            slowmode_delay=slowmode_delay,
            flags=flags,
            reason=reason,
            **kwargs,
        )
        if payload is not None:
            # the payload will always be the proper channel payload
            return self.__class__(state=self._state, guild=self.guild, data=payload)  # type: ignore

    async def delete_messages(self, messages: Iterable[Snowflake]) -> None:
        """|coro|

        Deletes a list of messages. This is similar to :meth:`Message.delete`
        except it bulk deletes multiple messages.

        As a special case, if the number of messages is 0, then nothing
        is done. If the number of messages is 1 then single message
        delete is done. If it's more than two, then bulk delete is used.

        You cannot bulk delete more than 100 messages or messages that
        are older than 14 days.

        You must have :attr:`~Permissions.manage_messages` permission to
        do this.

        .. versionadded:: 2.5

        Parameters
        ----------
        messages: Iterable[:class:`abc.Snowflake`]
            An iterable of messages denoting which ones to bulk delete.

        Raises
        ------
        ClientException
            The number of messages to delete was more than 100.
        Forbidden
            You do not have proper permissions to delete the messages.
        NotFound
            If single delete, then the message was already deleted.
        HTTPException
            Deleting the messages failed.
        """
        if not isinstance(messages, (list, tuple)):
            messages = list(messages)

        if len(messages) == 0:
            return  # do nothing

        if len(messages) == 1:
            message_id: int = messages[0].id
            await self._state.http.delete_message(self.id, message_id)
            return

        if len(messages) > 100:
            raise ClientException("Can only bulk delete messages up to 100 messages")

        message_ids: SnowflakeList = [m.id for m in messages]
        await self._state.http.delete_messages(self.id, message_ids)

    async def purge(
        self,
        *,
        limit: Optional[int] = 100,
        check: Callable[[Message], bool] = MISSING,
        before: Optional[SnowflakeTime] = None,
        after: Optional[SnowflakeTime] = None,
        around: Optional[SnowflakeTime] = None,
        oldest_first: Optional[bool] = False,
        bulk: bool = True,
    ) -> List[Message]:
        """|coro|

        Purges a list of messages that meet the criteria given by the predicate
        ``check``. If a ``check`` is not provided then all messages are deleted
        without discrimination.

        You must have :attr:`~Permissions.manage_messages` permission to
        delete messages even if they are your own.
        :attr:`~Permissions.read_message_history` permission is
        also needed to retrieve message history.

        .. versionadded:: 2.5

        .. note::

            See :meth:`TextChannel.purge` for examples.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of messages to search through. This is not the number
            of messages that will be deleted, though it can be.
        check: Callable[[:class:`Message`], :class:`bool`]
            The function used to check if a message should be deleted.
            It must take a :class:`Message` as its sole parameter.
        before: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Same as ``before`` in :meth:`history`.
        after: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Same as ``after`` in :meth:`history`.
        around: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Same as ``around`` in :meth:`history`.
        oldest_first: Optional[:class:`bool`]
            Same as ``oldest_first`` in :meth:`history`.
        bulk: :class:`bool`
            If ``True``, use bulk delete. Setting this to ``False`` is useful for mass-deleting
            a bot's own messages without :attr:`Permissions.manage_messages`. When ``True``, will
            fall back to single delete if messages are older than two weeks.

        Raises
        ------
        Forbidden
            You do not have proper permissions to do the actions required.
        HTTPException
            Purging the messages failed.

        Returns
        -------
        List[:class:`.Message`]
            A list of messages that were deleted.
        """
        if check is MISSING:
            check = lambda m: True

        iterator = self.history(
            limit=limit, before=before, after=after, oldest_first=oldest_first, around=around
        )
        ret: List[Message] = []
        count = 0

        minimum_time = int((time.time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
        strategy = self.delete_messages if bulk else _single_delete_strategy

        async for message in iterator:
            if count == 100:
                to_delete = ret[-100:]
                await strategy(to_delete)
                count = 0
                await asyncio.sleep(1)

            if not check(message):
                continue

            if message.id < minimum_time:
                # older than 14 days old
                if count == 1:
                    await ret[-1].delete()
                elif count >= 2:
                    to_delete = ret[-count:]
                    await strategy(to_delete)

                count = 0
                strategy = _single_delete_strategy

            count += 1
            ret.append(message)

        # SOme messages remaining to poll
        if count >= 2:
            # more than 2 messages -> bulk delete
            to_delete = ret[-count:]
            await strategy(to_delete)
        elif count == 1:
            # delete a single message
            await ret[-1].delete()

        return ret

    async def webhooks(self) -> List[Webhook]:
        """|coro|

        Retrieves the list of webhooks this channel has.

        You must have :attr:`~.Permissions.manage_webhooks` permission to
        use this.

        .. versionadded:: 2.5

        Raises
        ------
        Forbidden
            You don't have permissions to get the webhooks.

        Returns
        -------
        List[:class:`Webhook`]
            The list of webhooks this channel has.
        """
        from .webhook import Webhook

        data = await self._state.http.channel_webhooks(self.id)
        return [Webhook.from_state(d, state=self._state) for d in data]

    async def create_webhook(
        self, *, name: str, avatar: Optional[bytes] = None, reason: Optional[str] = None
    ) -> Webhook:
        """|coro|

        Creates a webhook for this channel.

        You must have :attr:`~.Permissions.manage_webhooks` permission to
        do this.

        .. versionadded:: 2.5

        Parameters
        ----------
        name: :class:`str`
            The webhook's name.
        avatar: Optional[:class:`bytes`]
            The webhook's default avatar.
            This operates similarly to :meth:`~ClientUser.edit`.
        reason: Optional[:class:`str`]
            The reason for creating this webhook. Shows up in the audit logs.

        Raises
        ------
        NotFound
            The ``avatar`` asset couldn't be found.
        Forbidden
            You do not have permissions to create a webhook.
        HTTPException
            Creating the webhook failed.
        TypeError
            The ``avatar`` asset is a lottie sticker (see :func:`Sticker.read`).

        Returns
        -------
        :class:`Webhook`
            The newly created webhook.
        """
        from .webhook import Webhook

        avatar_data = await utils._assetbytes_to_base64_data(avatar)

        data = await self._state.http.create_webhook(
            self.id, name=str(name), avatar=avatar_data, reason=reason
        )
        return Webhook.from_state(data, state=self._state)


class StageChannel(VocalGuildChannel):
    """Represents a Discord guild stage channel.

    .. versionadded:: 1.7

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns the channel's name.

    Attributes
    ----------
    name: :class:`str`
        The channel's name.
    guild: :class:`Guild`
        The guild the channel belongs to.
    id: :class:`int`
        The channel's ID.
    topic: Optional[:class:`str`]
        The channel's topic. ``None`` if it isn't set.
    category_id: Optional[:class:`int`]
        The category channel ID this channel belongs to, if applicable.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0. e.g. the
        top channel is position 0.
    bitrate: :class:`int`
        The channel's preferred audio bitrate in bits per second.
    user_limit: :class:`int`
        The channel's limit for number of members that can be in a stage channel.
    rtc_region: Optional[:class:`str`]
        The region for the stage channel's voice communication.
        A value of ``None`` indicates automatic voice region detection.

        .. versionchanged:: 2.5
            No longer a ``VoiceRegion`` instance.

    video_quality_mode: :class:`VideoQualityMode`
        The camera video quality for the stage channel's participants.

        .. versionadded:: 2.0
    """

    __slots__ = ("topic",)

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("name", self.name),
            ("topic", self.topic),
            ("rtc_region", self.rtc_region),
            ("position", self.position),
            ("bitrate", self.bitrate),
            ("video_quality_mode", self.video_quality_mode),
            ("user_limit", self.user_limit),
            ("category_id", self.category_id),
            ("flags", self.flags),
        )
        joined = " ".join(f"{k!s}={v!r}" for k, v in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def _update(self, guild: Guild, data: StageChannelPayload) -> None:
        super()._update(guild, data)
        self.topic: Optional[str] = data.get("topic")

    @property
    def requesting_to_speak(self) -> List[Member]:
        """List[:class:`Member`]: A list of members who are requesting to speak in the stage channel."""
        return [
            member
            for member in self.members
            if member.voice and member.voice.requested_to_speak_at is not None
        ]

    @property
    def speakers(self) -> List[Member]:
        """List[:class:`Member`]: A list of members who have been permitted to speak in the stage channel.

        .. versionadded:: 2.0
        """
        return [
            member
            for member in self.members
            if member.voice
            and not member.voice.suppress
            and member.voice.requested_to_speak_at is None
        ]

    @property
    def listeners(self) -> List[Member]:
        """List[:class:`Member`]: A list of members who are listening in the stage channel.

        .. versionadded:: 2.0
        """
        return [member for member in self.members if member.voice and member.voice.suppress]

    @property
    def moderators(self) -> List[Member]:
        """List[:class:`Member`]: A list of members who are moderating the stage channel.

        .. versionadded:: 2.0
        """
        required_permissions = Permissions.stage_moderator()
        return [
            member
            for member in self.members
            if self.permissions_for(member) >= required_permissions
        ]

    @property
    def type(self) -> Literal[ChannelType.stage_voice]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.stage_voice`.
        """
        return ChannelType.stage_voice

    @utils.copy_doc(disnake.abc.GuildChannel.clone)
    async def clone(
        self, *, name: Optional[str] = None, reason: Optional[str] = None
    ) -> StageChannel:
        return await self._clone_impl({}, name=name, reason=reason)

    @property
    def instance(self) -> Optional[StageInstance]:
        """Optional[:class:`StageInstance`]: The running stage instance of the stage channel.

        .. versionadded:: 2.0
        """
        return utils.get(self.guild.stage_instances, channel_id=self.id)

    @utils.copy_doc(disnake.abc.GuildChannel.permissions_for)
    def permissions_for(
        self,
        obj: Union[Member, Role],
        /,
        *,
        ignore_timeout: bool = MISSING,
    ) -> Permissions:
        base = super().permissions_for(obj, ignore_timeout=ignore_timeout)

        # voice channels cannot be edited by people who can't connect to them
        # It also implicitly denies all other voice perms
        if not base.connect:
            denied = Permissions.voice()
            denied.update(manage_channels=True, manage_roles=True)
            base.value &= ~denied.value
        return base

    async def create_instance(
        self,
        *,
        topic: str,
        privacy_level: StagePrivacyLevel = MISSING,
        notify_everyone: bool = False,
        reason: Optional[str] = None,
    ) -> StageInstance:
        """|coro|

        Creates a stage instance.

        You must have :attr:`~Permissions.manage_channels` permission to
        do this.

        .. versionadded:: 2.0

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` instead of ``InvalidArgument``.

        Parameters
        ----------
        topic: :class:`str`
            The stage instance's topic.
        privacy_level: :class:`StagePrivacyLevel`
            The stage instance's privacy level. Defaults to :attr:`StagePrivacyLevel.guild_only`.
        reason: Optional[:class:`str`]
            The reason the stage instance was created. Shows up on the audit log.
        notify_everyone: :class:`bool`
            Whether to notify ``@everyone`` that the stage instance has started.
            Requires the :attr:`~Permissions.mention_everyone` permission on the stage channel.
            Defaults to ``False``.

            .. versionadded:: 2.5

        Raises
        ------
        Forbidden
            You do not have permissions to create a stage instance.
        HTTPException
            Creating a stage instance failed.
        TypeError
            If the ``privacy_level`` parameter is not the proper type.

        Returns
        -------
        :class:`StageInstance`
            The newly created stage instance.
        """
        payload: Dict[str, Any] = {
            "channel_id": self.id,
            "topic": topic,
            "send_start_notification": notify_everyone,
        }

        if privacy_level is not MISSING:
            if not isinstance(privacy_level, StagePrivacyLevel):
                raise TypeError("privacy_level field must be of type PrivacyLevel")
            if privacy_level is StagePrivacyLevel.public:
                utils.warn_deprecated(
                    "Setting privacy_level to public is deprecated and will be removed in a future version.",
                    stacklevel=2,
                )

            payload["privacy_level"] = privacy_level.value

        data = await self._state.http.create_stage_instance(**payload, reason=reason)
        return StageInstance(guild=self.guild, state=self._state, data=data)

    async def fetch_instance(self) -> StageInstance:
        """|coro|

        Retrieves the running :class:`StageInstance`.

        .. versionadded:: 2.0

        Raises
        ------
        NotFound
            The stage instance or channel could not be found.
        HTTPException
            Retrieving the stage instance failed.

        Returns
        -------
        :class:`StageInstance`
            The stage instance.
        """
        data = await self._state.http.get_stage_instance(self.id)
        return StageInstance(guild=self.guild, state=self._state, data=data)

    # if only these parameters are passed, `_move` is called and no channel will be returned
    @overload
    async def edit(
        self,
        *,
        position: int,
        category: Optional[Snowflake] = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    # only passing `sync_permissions` may or may not return a channel,
    # depending on whether the channel is in a category
    @overload
    async def edit(
        self,
        *,
        sync_permissions: bool,
        reason: Optional[str] = ...,
    ) -> Optional[StageChannel]:
        ...

    @overload
    async def edit(
        self,
        *,
        name: str = ...,
        position: int = ...,
        sync_permissions: bool = ...,
        category: Optional[Snowflake] = ...,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
        rtc_region: Optional[Union[str, VoiceRegion]] = ...,
        video_quality_mode: VideoQualityMode = ...,
        bitrate: int = ...,
        flags: ChannelFlags = ...,
        reason: Optional[str] = ...,
    ) -> StageChannel:
        ...

    async def edit(
        self,
        *,
        name: str = MISSING,
        position: int = MISSING,
        sync_permissions: bool = MISSING,
        category: Optional[Snowflake] = MISSING,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = MISSING,
        rtc_region: Optional[Union[str, VoiceRegion]] = MISSING,
        video_quality_mode: VideoQualityMode = MISSING,
        bitrate: int = MISSING,
        flags: ChannelFlags = MISSING,
        reason: Optional[str] = None,
        **kwargs: Never,
    ) -> Optional[StageChannel]:
        """|coro|

        Edits the channel.

        You must have :attr:`~Permissions.manage_channels` permission to
        do this.

        .. versionchanged:: 2.0
            The ``topic`` parameter must now be set via :attr:`create_instance`.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited channel is returned instead.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` or :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        name: :class:`str`
            The new channel's name.
        position: :class:`int`
            The new channel's position.
        sync_permissions: :class:`bool`
            Whether to sync permissions with the channel's new or pre-existing
            category. Defaults to ``False``.
        category: Optional[:class:`abc.Snowflake`]
            The new category for this channel. Can be ``None`` to remove the
            category.
        overwrites: :class:`Mapping`
            A :class:`Mapping` of target (either a role or a member) to
            :class:`PermissionOverwrite` to apply to the channel.
        rtc_region: Optional[Union[:class:`str`, :class:`VoiceRegion`]]
            The new region for the stage channel's voice communication.
            A value of ``None`` indicates automatic voice region detection.
        video_quality_mode: :class:`VideoQualityMode`
            The camera video quality for the stage channel's participants.

            .. versionadded:: 2.0

        bitrate: :class:`int`
            The new channel's bitrate.

            .. versionadded:: 2.6

        flags: :class:`ChannelFlags`
            The new flags to set for this channel. This will overwrite any existing flags set on this channel.

            .. versionadded:: 2.6

        reason: Optional[:class:`str`]
            The reason for editing this channel. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to edit the channel.
        HTTPException
            Editing the channel failed.
        TypeError
            The permission overwrite information is not in proper form.
        ValueError
            The position is less than 0.

        Returns
        -------
        Optional[:class:`.StageChannel`]
            The newly edited stage channel. If the edit was only positional
            then ``None`` is returned instead.
        """
        payload = await self._edit(
            name=name,
            position=position,
            sync_permissions=sync_permissions,
            category=category,
            overwrites=overwrites,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            bitrate=bitrate,
            flags=flags,
            reason=reason,
            **kwargs,
        )
        if payload is not None:
            # the payload will always be the proper channel payload
            return self.__class__(state=self._state, guild=self.guild, data=payload)  # type: ignore


class CategoryChannel(disnake.abc.GuildChannel, Hashable):
    """Represents a Discord channel category.

    These are useful to group channels to logical compartments.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the category's hash.

        .. describe:: str(x)

            Returns the category's name.

    Attributes
    ----------
    name: :class:`str`
        The category name.
    guild: :class:`Guild`
        The guild the category belongs to.
    id: :class:`int`
        The category channel ID.
    position: :class:`int`
        The position in the category list. This is a number that starts at 0. e.g. the
        top category is position 0.
    nsfw: :class:`bool`
        If the channel is marked as "not safe for work".

        .. note::

            To check if the channel or the guild of that channel are marked as NSFW, consider :meth:`is_nsfw` instead.
    """

    __slots__ = (
        "name",
        "id",
        "guild",
        "nsfw",
        "_state",
        "position",
        "_overwrites",
        "category_id",
        "_flags",
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: CategoryChannelPayload):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._update(guild, data)

    def __repr__(self) -> str:
        return f"<CategoryChannel id={self.id} name={self.name!r} position={self.position} nsfw={self.nsfw} flags={self.flags!r}>"

    def _update(self, guild: Guild, data: CategoryChannelPayload) -> None:
        self.guild: Guild = guild
        # apparently this can be nullable in the case of a bad api deploy
        self.name: str = data.get("name") or ""
        self.category_id: Optional[int] = utils._get_as_snowflake(data, "parent_id")
        self._flags = data.get("flags", 0)
        self.nsfw: bool = data.get("nsfw", False)
        self.position: int = data["position"]
        self._fill_overwrites(data)

    @property
    def _sorting_bucket(self) -> int:
        return ChannelType.category.value

    @property
    def type(self) -> Literal[ChannelType.category]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.category`.
        """
        return ChannelType.category

    def is_nsfw(self) -> bool:
        """Whether the category is marked as NSFW.

        :return type: :class:`bool`
        """
        return self.nsfw

    @utils.copy_doc(disnake.abc.GuildChannel.clone)
    async def clone(
        self, *, name: Optional[str] = None, reason: Optional[str] = None
    ) -> CategoryChannel:
        return await self._clone_impl({"nsfw": self.nsfw}, name=name, reason=reason)

    # if only these parameters are passed, `_move` is called and no channel will be returned
    @overload
    async def edit(
        self,
        *,
        position: int,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    @overload
    async def edit(
        self,
        *,
        name: str = ...,
        position: int = ...,
        nsfw: bool = ...,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
        flags: ChannelFlags = ...,
        reason: Optional[str] = ...,
    ) -> CategoryChannel:
        ...

    async def edit(
        self,
        *,
        name: str = MISSING,
        position: int = MISSING,
        nsfw: bool = MISSING,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = MISSING,
        flags: ChannelFlags = MISSING,
        reason: Optional[str] = None,
        **kwargs: Never,
    ) -> Optional[CategoryChannel]:
        """|coro|

        Edits the category.

        You must have :attr:`~Permissions.manage_channels` permission to
        do this.

        .. versionchanged:: 1.3
            The ``overwrites`` keyword-only parameter was added.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited channel is returned instead.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` or :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        name: :class:`str`
            The new category's name.
        position: :class:`int`
            The new category's position.
        nsfw: :class:`bool`
            Whether to mark the category as NSFW.
        overwrites: :class:`Mapping`
            A :class:`Mapping` of target (either a role or a member) to
            :class:`PermissionOverwrite` to apply to the category.
        flags: :class:`ChannelFlags`
            The new flags to set for this channel. This will overwrite any existing flags set on this channel.

            .. versionadded:: 2.6

        reason: Optional[:class:`str`]
            The reason for editing this category. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to edit the category.
        HTTPException
            Editing the category failed.
        TypeError
            The permission overwrite information is not in proper form.
        ValueError
            The position is less than 0.

        Returns
        -------
        Optional[:class:`.CategoryChannel`]
            The newly edited category channel. If the edit was only positional
            then ``None`` is returned instead.
        """
        payload = await self._edit(
            name=name,
            position=position,
            nsfw=nsfw,
            overwrites=overwrites,
            flags=flags,
            reason=reason,
            **kwargs,
        )
        if payload is not None:
            # the payload will always be the proper channel payload
            return self.__class__(state=self._state, guild=self.guild, data=payload)  # type: ignore

    @overload
    async def move(
        self,
        *,
        beginning: bool,
        offset: int = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    @overload
    async def move(
        self,
        *,
        end: bool,
        offset: int = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    @overload
    async def move(
        self,
        *,
        before: Snowflake,
        offset: int = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    @overload
    async def move(
        self,
        *,
        after: Snowflake,
        offset: int = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    @utils.copy_doc(disnake.abc.GuildChannel.move)
    async def move(self, **kwargs):
        kwargs.pop("category", None)
        await super().move(**kwargs)

    @property
    def channels(self) -> List[GuildChannelType]:
        """List[:class:`abc.GuildChannel`]: Returns the channels that are under this category.

        These are sorted by the official Discord UI, which places voice channels below the text channels.
        """

        def comparator(channel):
            return (not isinstance(channel, (TextChannel, ForumChannel)), channel.position)

        ret = [c for c in self.guild.channels if c.category_id == self.id]
        ret.sort(key=comparator)
        return ret

    @property
    def text_channels(self) -> List[TextChannel]:
        """List[:class:`TextChannel`]: Returns the text channels that are under this category."""
        ret = [
            c
            for c in self.guild.channels
            if c.category_id == self.id and isinstance(c, TextChannel)
        ]
        ret.sort(key=lambda c: (c.position, c.id))
        return ret

    @property
    def voice_channels(self) -> List[VoiceChannel]:
        """List[:class:`VoiceChannel`]: Returns the voice channels that are under this category."""
        ret = [
            c
            for c in self.guild.channels
            if c.category_id == self.id and isinstance(c, VoiceChannel)
        ]
        ret.sort(key=lambda c: (c.position, c.id))
        return ret

    @property
    def stage_channels(self) -> List[StageChannel]:
        """List[:class:`StageChannel`]: Returns the stage channels that are under this category.

        .. versionadded:: 1.7
        """
        ret = [
            c
            for c in self.guild.channels
            if c.category_id == self.id and isinstance(c, StageChannel)
        ]
        ret.sort(key=lambda c: (c.position, c.id))
        return ret

    @property
    def forum_channels(self) -> List[ForumChannel]:
        """List[:class:`ForumChannel`]: Returns the forum channels that are under this category.

        .. versionadded:: 2.5
        """
        ret = [
            c
            for c in self.guild.channels
            if c.category_id == self.id and isinstance(c, ForumChannel)
        ]
        ret.sort(key=lambda c: (c.position, c.id))
        return ret

    async def create_text_channel(self, name: str, **options: Any) -> TextChannel:
        """|coro|

        A shortcut method to :meth:`Guild.create_text_channel` to create a :class:`TextChannel` in the category.

        Returns
        -------
        :class:`TextChannel`
            The newly created text channel.
        """
        if "category" in options:
            raise TypeError("got an unexpected keyword argument 'category'")
        return await self.guild.create_text_channel(name, category=self, **options)

    async def create_voice_channel(self, name: str, **options: Any) -> VoiceChannel:
        """|coro|

        A shortcut method to :meth:`Guild.create_voice_channel` to create a :class:`VoiceChannel` in the category.

        Returns
        -------
        :class:`VoiceChannel`
            The newly created voice channel.
        """
        if "category" in options:
            raise TypeError("got an unexpected keyword argument 'category'")
        return await self.guild.create_voice_channel(name, category=self, **options)

    async def create_stage_channel(self, name: str, **options: Any) -> StageChannel:
        """|coro|

        A shortcut method to :meth:`Guild.create_stage_channel` to create a :class:`StageChannel` in the category.

        .. versionadded:: 1.7

        Returns
        -------
        :class:`StageChannel`
            The newly created stage channel.
        """
        if "category" in options:
            raise TypeError("got an unexpected keyword argument 'category'")
        return await self.guild.create_stage_channel(name, category=self, **options)

    async def create_forum_channel(self, name: str, **options: Any) -> ForumChannel:
        """|coro|

        A shortcut method to :meth:`Guild.create_forum_channel` to create a :class:`ForumChannel` in the category.

        .. versionadded:: 2.5

        Returns
        -------
        :class:`ForumChannel`
            The newly created forum channel.
        """
        if "category" in options:
            raise TypeError("got an unexpected keyword argument 'category'")
        return await self.guild.create_forum_channel(name, category=self, **options)


class NewsChannel(TextChannel):
    """Represents a Discord news channel

    An exact 1:1 copy of :class:`TextChannel` meant for command annotations
    """

    type: ChannelType = ChannelType.news


class ThreadWithMessage(NamedTuple):
    thread: Thread
    message: Message


class ForumChannel(disnake.abc.GuildChannel, Hashable):
    """Represents a Discord Forum channel.

    .. versionadded:: 2.5

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns the channel's name.

    Attributes
    ----------
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    guild: :class:`Guild`
        The guild the channel belongs to.
    topic: Optional[:class:`str`]
        The channel's topic. ``None`` if it isn't set.
    category_id: Optional[:class:`int`]
        The category channel ID this channel belongs to, if applicable.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0. e.g. the
        top channel is position 0.
    nsfw: :class:`bool`
        Whether the channel is marked as "not safe for work".

        .. note::

            To check if the channel or the guild of that channel are marked as NSFW, consider :meth:`is_nsfw` instead.
    last_thread_id: Optional[:class:`int`]
        The ID of the last created thread in this channel. It may
        *not* point to an existing or valid thread.
    default_auto_archive_duration: :class:`int`
        The default auto archive duration in minutes for threads created in this channel.
    slowmode_delay: :class:`int`
        The number of seconds a member must wait between creating threads
        in this channel.

        A value of ``0`` denotes that it is disabled.
        Bots, and users with :attr:`~Permissions.manage_channels` or
        :attr:`~Permissions.manage_messages`, bypass slowmode.

        See also :attr:`default_thread_slowmode_delay`.

    default_thread_slowmode_delay: :class:`int`
        The default number of seconds a member must wait between sending messages
        in newly created threads in this channel.

        A value of ``0`` denotes that it is disabled.
        Bots, and users with :attr:`~Permissions.manage_channels` or
        :attr:`~Permissions.manage_messages`, bypass slowmode.

        .. versionadded:: 2.6

    default_sort_order: Optional[:class:`ThreadSortOrder`]
        The default sort order of threads in this channel.
        Members will still be able to change this locally.

        .. versionadded:: 2.6
    """

    __slots__ = (
        "id",
        "name",
        "category_id",
        "topic",
        "position",
        "nsfw",
        "last_thread_id",
        "_flags",
        "default_auto_archive_duration",
        "guild",
        "slowmode_delay",
        "default_thread_slowmode_delay",
        "default_sort_order",
        "_available_tags",
        "_default_reaction_emoji_id",
        "_default_reaction_emoji_name",
        "_state",
        "_type",
        "_overwrites",
    )

    def __init__(self, *, state: ConnectionState, guild: Guild, data: ForumChannelPayload) -> None:
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._type: int = data["type"]
        self._update(guild, data)

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("name", self.name),
            ("topic", self.topic),
            ("position", self.position),
            ("nsfw", self.nsfw),
            ("category_id", self.category_id),
            ("default_auto_archive_duration", self.default_auto_archive_duration),
            ("flags", self.flags),
        )
        joined = " ".join(f"{k!s}={v!r}" for k, v in attrs)
        return f"<{type(self).__name__} {joined}>"

    def _update(self, guild: Guild, data: ForumChannelPayload) -> None:
        self.guild: Guild = guild
        # apparently this can be nullable in the case of a bad api deploy
        self.name: str = data.get("name") or ""
        self.category_id: Optional[int] = utils._get_as_snowflake(data, "parent_id")
        self.topic: Optional[str] = data.get("topic")
        self.position: int = data["position"]
        self._flags = data.get("flags", 0)
        self.nsfw: bool = data.get("nsfw", False)
        self.last_thread_id: Optional[int] = utils._get_as_snowflake(data, "last_message_id")
        self.default_auto_archive_duration: ThreadArchiveDurationLiteral = data.get(
            "default_auto_archive_duration", 1440
        )
        self.slowmode_delay: int = data.get("rate_limit_per_user", 0)
        self.default_thread_slowmode_delay: int = data.get("default_thread_rate_limit_per_user", 0)

        tags = [
            ForumTag._from_data(data=tag, state=self._state)
            for tag in data.get("available_tags", [])
        ]
        self._available_tags: Dict[int, ForumTag] = {tag.id: tag for tag in tags}

        default_reaction_emoji = data.get("default_reaction_emoji") or {}
        # emoji_id may be `0`, use `None` instead
        self._default_reaction_emoji_id: Optional[int] = (
            utils._get_as_snowflake(default_reaction_emoji, "emoji_id") or None
        )
        self._default_reaction_emoji_name: Optional[str] = default_reaction_emoji.get("emoji_name")

        self.default_sort_order: Optional[ThreadSortOrder] = (
            try_enum(ThreadSortOrder, order)
            if (order := data.get("default_sort_order")) is not None
            else None
        )

        self._fill_overwrites(data)

    async def _get_channel(self) -> ForumChannel:
        return self

    @property
    def type(self) -> Literal[ChannelType.forum]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.forum`.
        """
        return ChannelType.forum

    @property
    def _sorting_bucket(self) -> int:
        return ChannelType.text.value

    @utils.copy_doc(disnake.abc.GuildChannel.permissions_for)
    def permissions_for(
        self,
        obj: Union[Member, Role],
        /,
        *,
        ignore_timeout: bool = MISSING,
    ) -> Permissions:
        base = super().permissions_for(obj, ignore_timeout=ignore_timeout)

        # forum channels do not have voice related permissions
        denied = Permissions.voice()
        base.value &= ~denied.value
        return base

    @property
    def members(self) -> List[Member]:
        """List[:class:`Member`]: Returns all members that can see this channel."""
        return [m for m in self.guild.members if self.permissions_for(m).view_channel]

    @property
    def threads(self) -> List[Thread]:
        """List[:class:`Thread`]: Returns all the threads that you can see."""
        return [thread for thread in self.guild._threads.values() if thread.parent_id == self.id]

    def is_nsfw(self) -> bool:
        """Whether the channel is marked as NSFW.

        :return type: :class:`bool`
        """
        return self.nsfw

    def requires_tag(self) -> bool:
        """Whether all newly created threads in this channel are required to have a tag.

        This is a shortcut to :attr:`self.flags.require_tag <ChannelFlags.require_tag>`.

        .. versionadded:: 2.6

        :return type: :class:`bool`
        """
        return self.flags.require_tag

    @property
    def default_reaction(self) -> Optional[Union[Emoji, PartialEmoji]]:
        """Optional[Union[:class:`Emoji`, :class:`PartialEmoji`]]:
        The default emoji shown for reacting to threads.

        Due to a Discord limitation, this will have an empty
        :attr:`~PartialEmoji.name` if it is a custom :class:`PartialEmoji`.

        .. versionadded:: 2.6
        """
        return PartialEmoji._emoji_from_name_id(
            self._default_reaction_emoji_name, self._default_reaction_emoji_id, state=self._state
        )

    @property
    def last_thread(self) -> Optional[Thread]:
        """Gets the last created thread in this channel from the cache.

        The thread might not be valid or point to an existing thread.

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last thread, use :meth:`Guild.fetch_channel` with the :attr:`last_thread_id`
            attribute.

        Returns
        -------
        Optional[:class:`Thread`]
            The last created thread in this channel or ``None`` if not found.
        """
        return self._state.get_channel(self.last_thread_id) if self.last_thread_id else None  # type: ignore

    @property
    def available_tags(self) -> List[ForumTag]:
        """List[:class:`ForumTag`]: The available tags for threads in this forum channel.

        To create/edit/delete tags, use :func:`~ForumChannel.edit`.

        .. versionadded:: 2.6
        """
        return list(self._available_tags.values())

    # both of these are re-implemented due to forum channels not being messageables
    async def trigger_typing(self) -> None:
        """|coro|

        Triggers a *typing* indicator to the desination.

        *Typing* indicator will go away after 10 seconds.
        """
        channel = await self._get_channel()
        await self._state.http.send_typing(channel.id)

    @utils.copy_doc(disnake.abc.Messageable.typing)
    def typing(self) -> Typing:
        return Typing(self)

    # if only these parameters are passed, `_move` is called and no channel will be returned
    @overload
    async def edit(
        self,
        *,
        position: int,
        category: Optional[Snowflake] = ...,
        sync_permissions: bool = ...,
        reason: Optional[str] = ...,
    ) -> None:
        ...

    # only passing `sync_permissions` may or may not return a channel,
    # depending on whether the channel is in a category
    @overload
    async def edit(
        self,
        *,
        sync_permissions: bool,
        reason: Optional[str] = ...,
    ) -> Optional[ForumChannel]:
        ...

    @overload
    async def edit(
        self,
        *,
        name: str = ...,
        topic: Optional[str] = ...,
        position: int = ...,
        nsfw: bool = ...,
        sync_permissions: bool = ...,
        category: Optional[Snowflake] = ...,
        slowmode_delay: Optional[int] = ...,
        default_thread_slowmode_delay: Optional[int] = ...,
        default_auto_archive_duration: Optional[AnyThreadArchiveDuration] = ...,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
        flags: ChannelFlags = ...,
        require_tag: bool = ...,
        available_tags: Sequence[ForumTag] = ...,
        default_reaction: Optional[Union[str, Emoji, PartialEmoji]] = ...,
        default_sort_order: Optional[ThreadSortOrder] = ...,
        reason: Optional[str] = ...,
    ) -> ForumChannel:
        ...

    async def edit(
        self,
        *,
        name: str = MISSING,
        topic: Optional[str] = MISSING,
        position: int = MISSING,
        nsfw: bool = MISSING,
        sync_permissions: bool = MISSING,
        category: Optional[Snowflake] = MISSING,
        slowmode_delay: Optional[int] = MISSING,
        default_thread_slowmode_delay: Optional[int] = MISSING,
        default_auto_archive_duration: Optional[AnyThreadArchiveDuration] = MISSING,
        overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = MISSING,
        flags: ChannelFlags = MISSING,
        require_tag: bool = MISSING,
        available_tags: Sequence[ForumTag] = MISSING,
        default_reaction: Optional[Union[str, Emoji, PartialEmoji]] = MISSING,
        default_sort_order: Optional[ThreadSortOrder] = MISSING,
        reason: Optional[str] = None,
        **kwargs: Never,
    ) -> Optional[ForumChannel]:
        """|coro|

        Edits the channel.

        You must have :attr:`~Permissions.manage_channels` permission to
        do this.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` or :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        name: :class:`str`
            The channel's new name.
        topic: Optional[:class:`str`]
            The channel's new topic.
        position: :class:`int`
            The channel's new position.
        nsfw: :class:`bool`
            Whether to mark the channel as NSFW.
        sync_permissions: :class:`bool`
            Whether to sync permissions with the channel's new or pre-existing
            category. Defaults to ``False``.
        category: Optional[:class:`abc.Snowflake`]
            The new category for this channel. Can be ``None`` to remove the
            category.
        slowmode_delay: Optional[:class:`int`]
            Specifies the slowmode rate limit at which users can create
            threads in this channel, in seconds.
            A value of ``0`` or ``None`` disables slowmode. The maximum value possible is ``21600``.
        default_thread_slowmode_delay: Optional[:class:`int`]
            Specifies the slowmode rate limit at which users can send messages
            in newly created threads in this channel, in seconds.
            This does not apply retroactively to existing threads.
            A value of ``0`` or ``None`` disables slowmode. The maximum value possible is ``21600``.

            .. versionadded:: 2.6

        overwrites: :class:`Mapping`
            A :class:`Mapping` of target (either a role or a member) to
            :class:`PermissionOverwrite` to apply to the channel.
        default_auto_archive_duration: Optional[Union[:class:`int`, :class:`ThreadArchiveDuration`]]
            The new default auto archive duration in minutes for threads created in this channel.
            Must be one of ``60``, ``1440``, ``4320``, or ``10080``.
        flags: :class:`ChannelFlags`
            The new flags to set for this channel. This will overwrite any existing flags set on this channel.
            If parameter ``require_tag`` is provided, that will override the setting of :attr:`ChannelFlags.require_tag`.

            .. versionadded:: 2.6

        require_tag: :class:`bool`
            Whether all newly created threads are required to have a tag.

            .. versionadded:: 2.6

        available_tags: Sequence[:class:`ForumTag`]
            The new :class:`ForumTag`\\s available for threads in this channel.
            Can be used to create new tags and edit/reorder/delete existing tags.
            Maximum of 20.

            Note that this overwrites all tags, removing existing tags unless they're passed as well.

            See :class:`ForumTag` for examples regarding creating/editing tags.

            .. versionadded:: 2.6

        default_reaction: Optional[Union[:class:`str`, :class:`Emoji`, :class:`PartialEmoji`]]
            The new default emoji shown for reacting to threads.

            .. versionadded:: 2.6

        default_sort_order: Optional[:class:`ThreadSortOrder`]
            The new default sort order of threads in this channel.

            .. versionadded:: 2.6

        reason: Optional[:class:`str`]
            The reason for editing this channel. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to edit the channel.
        HTTPException
            Editing the channel failed.
        TypeError
            The permission overwrite information is not in proper form.
        ValueError
            The position is less than 0.

        Returns
        -------
        Optional[:class:`ForumChannel`]
            The newly edited forum channel. If the edit was only positional
            then ``None`` is returned instead.
        """
        if require_tag is not MISSING:
            # create base flags if flags are provided, otherwise use the internal flags.
            flags = ChannelFlags._from_value(self._flags if flags is MISSING else flags.value)
            flags.require_tag = require_tag

        payload = await self._edit(
            name=name,
            topic=topic,
            position=position,
            nsfw=nsfw,
            sync_permissions=sync_permissions,
            category=category,
            slowmode_delay=slowmode_delay,
            default_thread_slowmode_delay=default_thread_slowmode_delay,
            default_auto_archive_duration=default_auto_archive_duration,
            overwrites=overwrites,
            flags=flags,
            available_tags=available_tags,
            default_reaction=default_reaction,
            default_sort_order=default_sort_order,
            reason=reason,
            **kwargs,
        )
        if payload is not None:
            # the payload will always be the proper channel payload
            return self.__class__(state=self._state, guild=self.guild, data=payload)  # type: ignore

    @utils.copy_doc(disnake.abc.GuildChannel.clone)
    async def clone(
        self, *, name: Optional[str] = None, reason: Optional[str] = None
    ) -> ForumChannel:
        return await self._clone_impl(
            {
                "topic": self.topic,
                "nsfw": self.nsfw,
                "rate_limit_per_user": self.slowmode_delay,
                "default_auto_archive_duration": self.default_auto_archive_duration,
            },
            name=name,
            reason=reason,
        )

    def get_thread(self, thread_id: int, /) -> Optional[Thread]:
        """Returns a thread with the given ID.

        Parameters
        ----------
        thread_id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`Thread`]
            The returned thread of ``None`` if not found.
        """
        return self.guild.get_thread(thread_id)

    @overload
    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: AnyThreadArchiveDuration = ...,
        slowmode_delay: int = ...,
        content: str = ...,
        embed: Embed = ...,
        file: File = ...,
        suppress_embeds: bool = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        allowed_mentions: AllowedMentions = ...,
        view: View = ...,
        components: Components = ...,
        reason: Optional[str] = None,
    ) -> ThreadWithMessage:
        ...

    @overload
    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: AnyThreadArchiveDuration = ...,
        slowmode_delay: int = ...,
        content: str = ...,
        embed: Embed = ...,
        files: List[File] = ...,
        suppress_embeds: bool = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        allowed_mentions: AllowedMentions = ...,
        view: View = ...,
        components: Components = ...,
        reason: Optional[str] = None,
    ) -> ThreadWithMessage:
        ...

    @overload
    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: AnyThreadArchiveDuration = ...,
        slowmode_delay: int = ...,
        content: str = ...,
        embeds: List[Embed] = ...,
        file: File = ...,
        suppress_embeds: bool = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        allowed_mentions: AllowedMentions = ...,
        view: View = ...,
        components: Components = ...,
        reason: Optional[str] = None,
    ) -> ThreadWithMessage:
        ...

    @overload
    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: AnyThreadArchiveDuration = ...,
        slowmode_delay: int = ...,
        content: str = ...,
        embeds: List[Embed] = ...,
        files: List[File] = ...,
        suppress_embeds: bool = ...,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = ...,
        allowed_mentions: AllowedMentions = ...,
        view: View = ...,
        components: Components = ...,
        reason: Optional[str] = None,
    ) -> ThreadWithMessage:
        ...

    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: AnyThreadArchiveDuration = MISSING,
        slowmode_delay: int = MISSING,
        applied_tags: Sequence[Snowflake] = MISSING,
        content: str = MISSING,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        suppress_embeds: bool = MISSING,
        stickers: Sequence[Union[GuildSticker, StickerItem]] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        view: View = MISSING,
        components: Components[MessageUIComponent] = MISSING,
        reason: Optional[str] = None,
    ) -> ThreadWithMessage:
        """|coro|

        Creates a thread in this forum channel.

        You must have the :attr:`~Permissions.create_forum_threads` permission to do this.

        At least one of ``content``, ``embed``/``embeds``, ``file``/``files``,
        ``stickers``, ``components``, or ``view`` must be provided.

        .. versionchanged:: 2.6
            Raises :exc:`TypeError` or :exc:`ValueError` instead of ``InvalidArgument``.

        .. versionchanged:: 2.6
            The ``content`` parameter is no longer required.

        Parameters
        ----------
        name: :class:`str`
            The name of the thread.
        auto_archive_duration: Union[:class:`int`, :class:`ThreadArchiveDuration`]
            The duration in minutes before the thread is automatically archived for inactivity.
            If not provided, the channel's default auto archive duration is used.
            Must be one of ``60``, ``1440``, ``4320``, or ``10080``.
        slowmode_delay: :class:`int`
            Specifies the slowmode rate limit for users in this thread, in seconds.
            A value of ``0`` disables slowmode. The maximum value possible is ``21600``.
            If not provided, slowmode is inherited from the parent's :attr:`~ForumChannel.default_thread_slowmode_delay`.
        applied_tags: Sequence[:class:`abc.Snowflake`]
            The tags to apply to the new thread. Maximum of 5.

            .. versionadded:: 2.6

        content: :class:`str`
            The content of the message to send.
        embed: :class:`.Embed`
            The rich embed for the content to send. This cannot be mixed with the
            ``embeds`` parameter.
        embeds: List[:class:`.Embed`]
            A list of embeds to send with the content. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
        suppress_embeds: :class:`bool`
            Whether to suppress embeds for the message. This hides
            all embeds from the UI if set to ``True``.
        file: :class:`.File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
        files: List[:class:`.File`]
            A list of files to upload. Must be a maximum of 10.
            This cannot be mixed with the ``file`` parameter.
        stickers: Sequence[Union[:class:`.GuildSticker`, :class:`.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3.
        allowed_mentions: :class:`.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`.Client.allowed_mentions`
            are used instead.
        view: :class:`.ui.View`
            A Discord UI View to add to the message. This cannot be mixed with ``components``.
        components: |components_type|
            A list of components to include in the message. This cannot be mixed with ``view``.
        reason: Optional[:class:`str`]
            The reason for creating the thread. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to create a thread.
        HTTPException
            Starting the thread failed.
        TypeError
            Specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or you specified both ``view`` and ``components``.
            or you have passed an object that is not :class:`File` to ``file`` or ``files``.
        ValueError
            Specified more than 10 embeds,
            or more than 10 files.

        Returns
        -------
        Tuple[:class:`Thread`, :class:`Message`]
            A :class:`~typing.NamedTuple` with the newly created thread and the message sent in it.

            These values can also be accessed through the ``thread`` and ``message`` fields.
        """
        from .message import Message
        from .webhook.async_ import handle_message_parameters_dict

        params = handle_message_parameters_dict(
            content,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            suppress_embeds=suppress_embeds,
            view=view,
            components=components,
            allowed_mentions=allowed_mentions,
            stickers=stickers,
        )

        if auto_archive_duration is not None:
            auto_archive_duration = cast(
                "ThreadArchiveDurationLiteral", try_enum_to_int(auto_archive_duration)
            )

        tag_ids = [t.id for t in applied_tags] if applied_tags else []

        if params.files and len(params.files) > 10:
            raise ValueError("files parameter must be a list of up to 10 elements")
        elif params.files and not all(isinstance(file, File) for file in params.files):
            raise TypeError("files parameter must be a list of File")

        channel_data = {
            "name": name,
            "auto_archive_duration": auto_archive_duration or self.default_auto_archive_duration,
            "applied_tags": tag_ids,
        }

        if slowmode_delay is not MISSING:
            channel_data["rate_limit_per_user"] = slowmode_delay

        try:
            data = await self._state.http.start_thread_in_forum_channel(
                self.id,
                **channel_data,
                files=params.files,
                reason=reason,
                **params.payload,
            )
        finally:
            if params.files:
                for f in params.files:
                    f.close()

        thread = Thread(guild=self.guild, data=data, state=self._state)
        message = Message(channel=thread, data=data["message"], state=self._state)

        if view:
            self._state.store_view(view, message.id)

        return ThreadWithMessage(thread, message)

    def archived_threads(
        self,
        *,
        limit: Optional[int] = 50,
        before: Optional[Union[Snowflake, datetime.datetime]] = None,
    ) -> ArchivedThreadIterator:
        """Returns an :class:`~disnake.AsyncIterator` that iterates over all archived threads in the channel.

        You must have :attr:`~Permissions.read_message_history` permission to use this.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of threads to retrieve.
            If ``None``, retrieves every archived thread in the channel. Note, however,
            that this would make it a slow operation.
        before: Optional[Union[:class:`abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve archived channels before the given date or ID.

        Raises
        ------
        Forbidden
            You do not have permissions to get archived threads.
        HTTPException
            The request to get the archived threads failed.

        Yields
        -------
        :class:`Thread`
            The archived threads.
        """
        return ArchivedThreadIterator(
            self.id, self.guild, limit=limit, joined=False, private=False, before=before
        )

    async def webhooks(self) -> List[Webhook]:
        """|coro|

        Retrieves the list of webhooks this channel has.

        You must have :attr:`~.Permissions.manage_webhooks` permission to
        use this.

        .. versionadded:: 2.6

        Raises
        ------
        Forbidden
            You don't have permissions to get the webhooks.

        Returns
        -------
        List[:class:`Webhook`]
            The list of webhooks this channel has.
        """
        from .webhook import Webhook

        data = await self._state.http.channel_webhooks(self.id)
        return [Webhook.from_state(d, state=self._state) for d in data]

    async def create_webhook(
        self, *, name: str, avatar: Optional[bytes] = None, reason: Optional[str] = None
    ) -> Webhook:
        """|coro|

        Creates a webhook for this channel.

        You must have :attr:`~.Permissions.manage_webhooks` permission to
        do this.

        .. versionadded:: 2.6

        Parameters
        ----------
        name: :class:`str`
            The webhook's name.
        avatar: Optional[:class:`bytes`]
            The webhook's default avatar.
            This operates similarly to :meth:`~ClientUser.edit`.
        reason: Optional[:class:`str`]
            The reason for creating this webhook. Shows up in the audit logs.

        Raises
        ------
        NotFound
            The ``avatar`` asset couldn't be found.
        Forbidden
            You do not have permissions to create a webhook.
        HTTPException
            Creating the webhook failed.
        TypeError
            The ``avatar`` asset is a lottie sticker (see :func:`Sticker.read`).

        Returns
        -------
        :class:`Webhook`
            The newly created webhook.
        """
        from .webhook import Webhook

        avatar_data = await utils._assetbytes_to_base64_data(avatar)

        data = await self._state.http.create_webhook(
            self.id, name=str(name), avatar=avatar_data, reason=reason
        )
        return Webhook.from_state(data, state=self._state)

    def get_tag(self, tag_id: int, /) -> Optional[ForumTag]:
        """Returns a thread tag with the given ID.

        .. versionadded:: 2.6

        Parameters
        ----------
        tag_id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`ForumTag`]
            The tag with the given ID, or ``None`` if not found.
        """
        return self._available_tags.get(tag_id)

    def get_tag_by_name(self, name: str, /) -> Optional[ForumTag]:
        """Returns a thread tag with the given name.

        Tags can be uniquely identified based on the name, as tag names
        in a forum channel must be unique.

        .. versionadded:: 2.6

        Parameters
        ----------
        name: :class:`str`
            The name to search for.

        Returns
        -------
        Optional[:class:`ForumTag`]
            The tag with the given name, or ``None`` if not found.
        """
        return utils.get(self._available_tags.values(), name=name)


class DMChannel(disnake.abc.Messageable, Hashable):
    """Represents a Discord direct message channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns a string representation of the channel

    Attributes
    ----------
    recipient: Optional[:class:`User`]
        The user you are participating with in the direct message channel.
        If this channel is received through the gateway, the recipient information
        may not be always available.
    me: :class:`ClientUser`
        The user presenting yourself.
    id: :class:`int`
        The direct message channel ID.
    last_pin_timestamp: Optional[:class:`datetime.datetime`]
        The time the most recent message was pinned, or ``None`` if no message is currently pinned.

        .. versionadded:: 2.5
    """

    __slots__ = (
        "id",
        "recipient",
        "me",
        "last_pin_timestamp",
        "_state",
        "_flags",
    )

    def __init__(self, *, me: ClientUser, state: ConnectionState, data: DMChannelPayload):
        self._state: ConnectionState = state
        self.recipient: Optional[User] = state.store_user(data["recipients"][0])  # type: ignore
        self.me: ClientUser = me
        self.id: int = int(data["id"])
        self.last_pin_timestamp: Optional[datetime.datetime] = utils.parse_time(
            data.get("last_pin_timestamp")
        )
        self._flags: int = data.get("flags", 0)

    async def _get_channel(self):
        return self

    def __str__(self) -> str:
        if self.recipient:
            return f"Direct Message with {self.recipient}"
        return "Direct Message with Unknown User"

    def __repr__(self) -> str:
        return f"<DMChannel id={self.id} recipient={self.recipient!r}>"

    @classmethod
    def _from_message(cls, state: ConnectionState, channel_id: int, user_id: int) -> Self:
        self = cls.__new__(cls)
        self._state = state
        self.id = channel_id
        # state.user won't be None here
        self.me = state.user
        self.recipient = state.get_user(user_id) if user_id != self.me.id else None
        self.last_pin_timestamp = None
        return self

    @property
    def type(self) -> Literal[ChannelType.private]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.private`.
        """
        return ChannelType.private

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the direct message channel's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def jump_url(self) -> str:
        """
        A URL that can be used to jump to this channel.

        .. versionadded:: 2.4
        """
        return f"https://discord.com/channels/@me/{self.id}"

    @property
    def flags(self) -> ChannelFlags:
        """:class:`.ChannelFlags`: The channel flags for this channel.

        .. versionadded:: 2.6
        """
        return ChannelFlags._from_value(self._flags)

    def permissions_for(
        self,
        obj: Any = None,
        /,
        *,
        ignore_timeout: bool = MISSING,
    ) -> Permissions:
        """Handles permission resolution for a :class:`User`.

        This function is there for compatibility with other channel types.

        Actual direct messages do not really have the concept of permissions.

        This returns all the :meth:`Permissions.private_channel` permissions set to ``True``.

        Parameters
        ----------
        obj: :class:`User`
            The user to check permissions for. This parameter is ignored
            but kept for compatibility with other ``permissions_for`` methods.

        ignore_timeout: :class:`bool`
            Whether to ignore the guild timeout when checking permsisions.
            This parameter is ignored but kept for compatibility with other ``permissions_for`` methods.

        Returns
        -------
        :class:`Permissions`
            The resolved permissions.
        """
        return Permissions.private_channel()

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the given message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        .. versionadded:: 1.6

        Parameters
        ----------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        -------
        :class:`PartialMessage`
            The partial message object.
        """
        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)


class GroupChannel(disnake.abc.Messageable, Hashable):
    """Represents a Discord group channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns a string representation of the channel

    Attributes
    ----------
    recipients: List[:class:`User`]
        The users you are participating with in the group channel.
    me: :class:`ClientUser`
        The user presenting yourself.
    id: :class:`int`
        The group channel ID.
    owner: Optional[:class:`User`]
        The user that owns the group channel.
    owner_id: :class:`int`
        The owner ID that owns the group channel.

        .. versionadded:: 2.0

    name: Optional[:class:`str`]
        The group channel's name if provided.
    """

    __slots__ = ("id", "recipients", "owner_id", "owner", "_icon", "name", "me", "_state")

    def __init__(self, *, me: ClientUser, state: ConnectionState, data: GroupChannelPayload):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.me: ClientUser = me
        self._update_group(data)

    def _update_group(self, data: GroupChannelPayload) -> None:
        self.owner_id: Optional[int] = utils._get_as_snowflake(data, "owner_id")
        self._icon: Optional[str] = data.get("icon")
        self.name: Optional[str] = data.get("name")
        self.recipients: List[User] = [
            self._state.store_user(u) for u in data.get("recipients", [])
        ]

        self.owner: Optional[BaseUser]
        if self.owner_id == self.me.id:
            self.owner = self.me
        else:
            self.owner = utils.find(lambda u: u.id == self.owner_id, self.recipients)

    async def _get_channel(self):
        return self

    def __str__(self) -> str:
        if self.name:
            return self.name

        if len(self.recipients) == 0:
            return "Unnamed"

        return ", ".join([x.name for x in self.recipients])

    def __repr__(self) -> str:
        return f"<GroupChannel id={self.id} name={self.name!r}>"

    @property
    def type(self) -> Literal[ChannelType.group]:
        """:class:`ChannelType`: The channel's Discord type.

        This always returns :attr:`ChannelType.group`.
        """
        return ChannelType.group

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the channel's icon asset if available."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="channel")

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the channel's creation time in UTC."""
        return utils.snowflake_time(self.id)

    def permissions_for(
        self,
        obj: Snowflake,
        /,
        *,
        ignore_timeout: bool = MISSING,
    ) -> Permissions:
        """Handles permission resolution for a :class:`User`.

        This function is there for compatibility with other channel types.

        Actual direct messages do not really have the concept of permissions.

        This returns all the :meth:`Permissions.private_channel` permissions set to ``True``.

        This also checks the kick_members permission if the user is the owner.

        Parameters
        ----------
        obj: :class:`~disnake.abc.Snowflake`
            The user to check permissions for.

        ignore_timeout: :class:`bool`
            Whether to ignore the guild timeout when checking permsisions.
            This parameter is ignored but kept for compatibility with other ``permissions_for`` methods.

        Returns
        -------
        :class:`Permissions`
            The resolved permissions for the user.
        """
        base = Permissions.private_channel()

        if obj.id == self.owner_id:
            base.kick_members = True

        return base

    async def leave(self) -> None:
        """|coro|

        Leaves the group.

        If you are the only one in the group, this deletes it as well.

        Raises
        ------
        HTTPException
            Leaving the group failed.
        """
        await self._state.http.leave_group(self.id)


class PartialMessageable(disnake.abc.Messageable, Hashable):
    """Represents a partial messageable to aid with working messageable channels when
    only a channel ID is present.

    The only way to construct this class is through :meth:`Client.get_partial_messageable`.

    Note that this class is trimmed down and has no rich attributes.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two partial messageables are equal.

        .. describe:: x != y

            Checks if two partial messageables are not equal.

        .. describe:: hash(x)

            Returns the partial messageable's hash.

    Attributes
    ----------
    id: :class:`int`
        The channel ID associated with this partial messageable.
    type: Optional[:class:`ChannelType`]
        The channel type associated with this partial messageable, if given.
    """

    def __init__(self, state: ConnectionState, id: int, type: Optional[ChannelType] = None):
        self._state: ConnectionState = state
        self.id: int = id
        self.type: Optional[ChannelType] = type

    async def _get_channel(self) -> PartialMessageable:
        return self

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the given message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        Parameters
        ----------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        -------
        :class:`PartialMessage`
            The partial message object.
        """
        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)


def _guild_channel_factory(channel_type: int):
    value = try_enum(ChannelType, channel_type)
    if value is ChannelType.text:
        return TextChannel, value
    elif value is ChannelType.voice:
        return VoiceChannel, value
    elif value is ChannelType.category:
        return CategoryChannel, value
    elif value is ChannelType.news:
        return TextChannel, value
    elif value is ChannelType.stage_voice:
        return StageChannel, value
    elif value is ChannelType.forum:
        return ForumChannel, value
    else:
        return None, value


def _channel_factory(channel_type: int):
    cls, value = _guild_channel_factory(channel_type)
    if value is ChannelType.private:
        return DMChannel, value
    elif value is ChannelType.group:
        return GroupChannel, value
    else:
        return cls, value


def _threaded_channel_factory(channel_type: int):
    cls, value = _channel_factory(channel_type)
    if value in (ChannelType.private_thread, ChannelType.public_thread, ChannelType.news_thread):
        return Thread, value
    return cls, value


def _threaded_guild_channel_factory(channel_type: int):
    cls, value = _guild_channel_factory(channel_type)
    if value in (ChannelType.private_thread, ChannelType.public_thread, ChannelType.news_thread):
        return Thread, value
    return cls, value


def _channel_type_factory(
    cls: Union[Type[disnake.abc.GuildChannel], Type[Thread]]
) -> List[ChannelType]:
    return {
        disnake.abc.GuildChannel: list(ChannelType.__members__.values()),
        VocalGuildChannel: [ChannelType.voice, ChannelType.stage_voice],
        disnake.abc.PrivateChannel: [ChannelType.private, ChannelType.group],
        TextChannel: [ChannelType.text, ChannelType.news],
        DMChannel: [ChannelType.private],
        VoiceChannel: [ChannelType.voice],
        GroupChannel: [ChannelType.group],
        CategoryChannel: [ChannelType.category],
        NewsChannel: [ChannelType.news],
        Thread: [ChannelType.news_thread, ChannelType.public_thread, ChannelType.private_thread],
        StageChannel: [ChannelType.stage_voice],
        ForumChannel: [ChannelType.forum],
    }.get(cls, [])
