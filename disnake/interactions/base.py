# -*- coding: utf-8 -*-

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

import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple, Union, cast, overload

from .. import utils
from ..app_commands import OptionChoice
from ..channel import ChannelType, PartialMessageable
from ..enums import InteractionResponseType, InteractionType, WebhookType, try_enum
from ..errors import (
    HTTPException,
    InteractionNotResponded,
    InteractionResponded,
    InteractionTimedOut,
    ModalChainNotSupported,
    NotFound,
)
from ..guild import Guild
from ..member import Member
from ..message import Attachment, Message
from ..object import Object
from ..permissions import Permissions
from ..ui.action_row import components_to_dict
from ..user import ClientUser, User
from ..webhook.async_ import Webhook, async_context, handle_message_parameters

__all__ = (
    "Interaction",
    "InteractionMessage",
    "InteractionResponse",
)

if TYPE_CHECKING:
    from datetime import datetime

    from aiohttp import ClientSession

    from ..app_commands import Choices
    from ..channel import (
        CategoryChannel,
        PartialMessageable,
        StageChannel,
        StoreChannel,
        TextChannel,
        VoiceChannel,
    )
    from ..client import Client
    from ..embeds import Embed
    from ..ext.commands import AutoShardedBot, Bot
    from ..file import File
    from ..mentions import AllowedMentions
    from ..state import ConnectionState
    from ..threads import Thread
    from ..types.components import Modal as ModalPayload
    from ..types.interactions import (
        ApplicationCommandOptionChoice as ApplicationCommandOptionChoicePayload,
        Interaction as InteractionPayload,
    )
    from ..ui.action_row import Components
    from ..ui.modal import Modal
    from ..ui.view import View
    from .message import MessageInteraction

    InteractionChannel = Union[
        VoiceChannel,
        StageChannel,
        TextChannel,
        CategoryChannel,
        StoreChannel,
        Thread,
        PartialMessageable,
    ]

    AnyBot = Union[Bot, AutoShardedBot]
else:
    MessageInteraction = ...  # only used for typecasting

MISSING: Any = utils.MISSING


class Interaction:
    """A base class representing a user-initiated Discord interaction.

    An interaction happens when a user performs an action that the client needs to
    be notified of. Current examples are application commands and components.

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction's type.
    application_id: :class:`int`
        The application ID that the interaction was for.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    guild_locale: Optional[:class:`str`]
        The selected language of the interaction's guild.
        This value is only meaningful in guilds with ``COMMUNITY`` feature and receives a default value otherwise.
        If the interaction was in a DM, then this value is ``None``.

        .. versionadded:: 2.4
    channel_id: :class:`int`
        The channel ID the interaction was sent from.
    author: Union[:class:`User`, :class:`Member`]
        The user or member that sent the interaction.
    locale: :class:`str`
        The selected language of the interaction's author.

        .. versionadded:: 2.4

    token: :class:`str`
        The token to continue the interaction. These are valid for 15 minutes.
    client: :class:`Client`
        The interaction client.
    """

    __slots__: Tuple[str, ...] = (
        "id",
        "type",
        "guild_id",
        "channel_id",
        "application_id",
        "author",
        "token",
        "version",
        "locale",
        "guild_locale",
        "client",
        "_permissions",
        "_state",
        "_session",
        "_original_message",
        "_cs_response",
        "_cs_followup",
        "_cs_channel",
        "_cs_me",
    )

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        self._state: ConnectionState = state
        # TODO: Maybe use a unique session
        self._session: ClientSession = state.http._HTTPClient__session  # type: ignore
        self.client: Client = state._get_client()
        self._original_message: Optional[InteractionMessage] = None

        self.id: int = int(data["id"])
        self.type: InteractionType = try_enum(InteractionType, data["type"])
        self.token: str = data["token"]
        self.version: int = data["version"]
        self.application_id: int = int(data["application_id"])

        self.channel_id: int = int(data["channel_id"])
        self.guild_id: Optional[int] = utils._get_as_snowflake(data, "guild_id")
        self.locale: str = data["locale"]
        self.guild_locale: Optional[str] = data.get("guild_locale")
        # one of user and member will always exist
        self.author: Union[User, Member] = MISSING
        self._permissions = None

        if self.guild_id and (member := data.get("member")):
            guild: Guild = self.guild or Object(id=self.guild_id)  # type: ignore
            self.author = (
                isinstance(guild, Guild)
                and guild.get_member(int(member["user"]["id"]))
                or Member(state=self._state, guild=guild, data=member)
            )
            self._permissions = int(member.get("permissions", 0))
        elif user := data.get("user"):
            self.author = self._state.store_user(user)

    @property
    def bot(self) -> AnyBot:
        """:class:`~disnake.ext.commands.Bot`: The bot handling the interaction.

        Only applicable when used with :class:`~disnake.ext.commands.Bot`.
        This is an alias for :attr:`.client`.
        """
        return self.client  # type: ignore

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: Returns the interaction's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def user(self) -> Union[User, Member]:
        """Union[:class:`.User`, :class:`.Member`]: The user or member that sent the interaction.
        There is an alias for this named :attr:`author`."""
        return self.author

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild the interaction was sent from."""
        return self._state._get_guild(self.guild_id)

    @utils.cached_slot_property("_cs_me")
    def me(self) -> Union[Member, ClientUser]:
        """Union[:class:`.Member`, :class:`.ClientUser`]:
        Similar to :attr:`.Guild.me` except it may return the :class:`.ClientUser` in private message contexts.
        """
        if self.guild is None:
            return None if self.bot is None else self.bot.user  # type: ignore
        return self.guild.me

    @utils.cached_slot_property("_cs_channel")
    def channel(self) -> Union[TextChannel, Thread, VoiceChannel]:
        """Union[:class:`abc.GuildChannel`, :class:`PartialMessageable`, :class:`Thread`]: The channel the interaction was sent from.

        Note that due to a Discord limitation, DM channels are not resolved since there is
        no data to complete them. These are :class:`PartialMessageable` instead.
        """
        # the actual typing of these is a bit complicated, we just leave it at text channels
        guild = self.guild
        channel = guild and guild._resolve_channel(self.channel_id)
        if channel is None:
            type = (
                None if self.guild_id is not None else ChannelType.private
            )  # could be a text, voice, or thread channel in a guild
            return PartialMessageable(state=self._state, id=self.channel_id, type=type)  # type: ignore
        return channel  # type: ignore

    @property
    def permissions(self) -> Permissions:
        """:class:`Permissions`: The resolved permissions of the member in the channel, including overwrites.

        In a non-guild context this will be an instance of :meth:`Permissions.private_channel`.
        """
        if self._permissions is not None:
            return Permissions(self._permissions)
        return Permissions.private_channel()

    @utils.cached_slot_property("_cs_response")
    def response(self) -> InteractionResponse:
        """:class:`InteractionResponse`: Returns an object responsible for handling responding to the interaction.

        A response can only be done once. If secondary messages need to be sent, consider using :attr:`followup`
        instead.
        """
        return InteractionResponse(self)

    @utils.cached_slot_property("_cs_followup")
    def followup(self) -> Webhook:
        """:class:`Webhook`: Returns the follow up webhook for follow up interactions."""
        payload = {
            "id": self.application_id,
            "type": WebhookType.application.value,
            "token": self.token,
        }
        return Webhook.from_state(data=payload, state=self._state)

    async def original_message(self) -> InteractionMessage:
        """|coro|

        Fetches the original interaction response message associated with the interaction.

        Here is a table with response types and their associated original message:

        .. csv-table::
            :header: "Response type", "Original message"

            :meth:`InteractionResponse.send_message`, "The message you sent"
            :meth:`InteractionResponse.edit_message`, "The message you edited"
            :meth:`InteractionResponse.defer`, "The message with thinking state (bot is thinking...)"
            "Other response types", "None"

        Repeated calls to this will return a cached value.

        Raises
        ------
        HTTPException
            Fetching the original response message failed.

        Returns
        -------
        InteractionMessage
            The original interaction response message.
        """
        if self._original_message is not None:
            return self._original_message

        adapter = async_context.get()
        data = await adapter.get_original_interaction_response(
            application_id=self.application_id,
            token=self.token,
            session=self._session,
        )
        state = _InteractionMessageState(self, self._state)
        message = InteractionMessage(state=state, channel=self.channel, data=data)  # type: ignore
        self._original_message = message
        return message

    async def edit_original_message(
        self,
        content: Optional[str] = MISSING,
        *,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: List[Attachment] = MISSING,
        view: Optional[View] = MISSING,
        components: Optional[Components] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the original, previously sent interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.edit` in case
        you do not want to fetch the message and save an HTTP request.

        This method is also the only way to edit the original message if
        the message sent was ephemeral.

        .. note::
            If the original message has embeds with images that were created from local files
            (using the ``file`` parameter with :meth:`Embed.set_image` or :meth:`Embed.set_thumbnail`),
            those images will be removed if the message's attachments are edited in any way
            (i.e. by setting ``file``/``files``/``attachments``, or adding an embed with local files).

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content to edit the message with, or ``None`` to clear it.
        embed: Optional[:class:`Embed`]
            The new embed to replace the original with. This cannot be mixed with the
            ``embeds`` parameter.
            Could be ``None`` to remove the embed.
        embeds: List[:class:`Embed`]
            The new embeds to replace the original with. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
            To remove all embeds ``[]`` should be passed.
        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.
        files: List[:class:`File`]
            A list of files to upload. This cannot be mixed with the ``file`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all existing attachments are removed.
            Keeps existing attachments if not provided.

            .. versionadded:: 2.2

        view: Optional[:class:`~disnake.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed. This can not be mixed with ``components``.
        components: Optional[|components_type|]
            A list of components to update this message with. This can not be mixed with ``view``.
            If ``None`` is passed then the components are removed.

            .. versionadded:: 2.4

        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.

        Raises
        ------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        -------
        :class:`InteractionMessage`
            The newly edited message.
        """
        # if no attachment list was provided but we're uploading new files,
        # use current attachments as the base
        if attachments is MISSING and (file or files):
            attachments = (await self.original_message()).attachments

        previous_mentions: Optional[AllowedMentions] = self._state.allowed_mentions
        params = handle_message_parameters(
            content=content,
            file=file,
            files=files,
            attachments=attachments,
            embed=embed,
            embeds=embeds,
            view=view,
            components=components,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_mentions,
        )
        adapter = async_context.get()
        try:
            data = await adapter.edit_original_interaction_response(
                self.application_id,
                self.token,
                session=self._session,
                payload=params.payload,
                multipart=params.multipart,
                files=params.files,
            )
        except NotFound as e:
            if e.code == 10015:
                raise InteractionNotResponded(self) from e
            raise
        finally:
            if params.files:
                for f in params.files:
                    f.close()

        # The message channel types should always match
        state = _InteractionMessageState(self, self._state)
        message = InteractionMessage(state=state, channel=self.channel, data=data)  # type: ignore
        if view and not view.is_finished():
            self._state.store_view(view, message.id)
        return message

    async def delete_original_message(self, *, delay: float = None) -> None:
        """|coro|

        Deletes the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.delete` in case
        you do not want to fetch the message and save an HTTP request.

        Parameters
        ----------
        delay: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the original message. If the deletion fails,
            then it is silently ignored.

        Raises
        ------
        HTTPException
            Deleting the message failed.
        Forbidden
            Deleted a message that is not yours.
        """
        adapter = async_context.get()
        deleter = adapter.delete_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
        )

        if delay is not None:

            async def delete(delay: float):
                await asyncio.sleep(delay)
                try:
                    await deleter
                except HTTPException:
                    pass

            asyncio.create_task(delete(delay))
            return

        try:
            await deleter
        except NotFound as e:
            if e.code == 10015:
                raise InteractionNotResponded(self) from e
            raise

    async def send(
        self,
        content: Optional[Any] = None,
        *,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        view: View = MISSING,
        components: Components = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        delete_after: float = MISSING,
    ) -> None:
        """|coro|

        Sends a message using either :meth:`response.send_message <InteractionResponse.send_message>`
        or :meth:`followup.send <Webhook.send>`.

        If the interaction hasn't been responded to yet, this method will call :meth:`response.send_message <InteractionResponse.send_message>`.
        Otherwise, it will call :meth:`followup.send <Webhook.send>`.

        .. note::
            This method does not return a :class:`Message` object. If you need a message object,
            use :meth:`original_message` to fetch it, or use :meth:`followup.send <Webhook.send>`
            directly instead of this method if you're sending a followup message.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with the
            ``embeds`` parameter.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
        files: List[:class:`File`]
            A list of files to upload. Must be a maximum of 10.
            This cannot be mixed with the ``file`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`Client.allowed_mentions <disnake.Client.allowed_mentions>`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`Client.allowed_mentions <disnake.Client.allowed_mentions>`.
            If no object is passed at all then the defaults given by :attr:`Client.allowed_mentions <disnake.Client.allowed_mentions>`
            are used instead.
        tts: :class:`bool`
            Whether the message should be sent using text-to-speech.
        view: :class:`disnake.ui.View`
            The view to send with the message. This can not be mixed with ``components``.
        components: |components_type|
            A list of components to send with the message. This can not be mixed with ``view``.

            .. versionadded:: 2.4

        ephemeral: :class:`bool`
            Whether the message should only be visible to the user who started the interaction.
            If a view is sent with an ephemeral message and it has no timeout set then the timeout
            is set to 15 minutes.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.

        Raises
        ------
        HTTPException
            Sending the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        ValueError
            The length of ``embeds`` was invalid.
        """
        if self.response._responded:
            sender = self.followup.send
        else:
            sender = self.response.send_message
        await sender(
            content=content,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            view=view,
            components=components,
            tts=tts,
            ephemeral=ephemeral,
            delete_after=delete_after,
        )


class InteractionResponse:
    """Represents a Discord interaction response.

    This type can be accessed through :attr:`Interaction.response`.

    .. versionadded:: 2.0
    """

    __slots__: Tuple[str, ...] = (
        "_responded",
        "_parent",
    )

    def __init__(self, parent: Interaction):
        self._parent: Interaction = parent
        self._responded: bool = False

    def is_done(self) -> bool:
        """Whether an interaction response has been done before.

        An interaction can only be responded to once.

        :return type: :class:`bool`
        """
        return self._responded

    async def defer(self, *, ephemeral: bool = False, with_message: bool = False) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        Parameters
        ----------
        ephemeral: :class:`bool`
            Whether the deferred message will eventually be ephemeral.
            This applies to interactions of type :attr:`InteractionType.application_command` and :attr:`InteractionType.modal_submit`
            or when the ``with_message`` parameter is ``True``.
        with_message: :class:`bool`
            Whether the response will be a message with thinking state (bot is thinking...).
            This only applies to interactions of type :attr:`InteractionType.component`.

            .. versionadded:: 2.4

        Raises
        ------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        data: Optional[Dict[str, Any]] = None
        parent = self._parent
        if (
            parent.type in (InteractionType.application_command, InteractionType.modal_submit)
            or with_message
        ):
            defer_type = InteractionResponseType.deferred_channel_message.value
            if ephemeral:
                data = {"flags": 64}
        elif parent.type is InteractionType.component:
            defer_type = InteractionResponseType.deferred_message_update.value

        if defer_type:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id, parent.token, session=parent._session, type=defer_type, data=data
            )
            self._responded = True

    async def pong(self) -> None:
        """|coro|

        Pongs the ping interaction.

        This should rarely be used.

        Raises
        ------
        HTTPException
            Ponging the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        if parent.type is InteractionType.ping:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                type=InteractionResponseType.pong.value,
            )
            self._responded = True

    async def send_message(
        self,
        content: Optional[Any] = None,
        *,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        view: View = MISSING,
        components: Components = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        delete_after: float = MISSING,
    ) -> None:
        """|coro|

        Responds to this interaction by sending a message.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with the
            ``embeds`` parameter.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
        files: List[:class:`File`]
            A list of files to upload. Must be a maximum of 10.
            This cannot be mixed with the ``file`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
        view: :class:`disnake.ui.View`
            The view to send with the message. This can not be mixed with ``components``.
        components: |components_type|
            A list of components to send with the message. This can not be mixed with ``view``.

            .. versionadded:: 2.4

        tts: :class:`bool`
            Whether the message should be sent using text-to-speech.
        ephemeral: :class:`bool`
            Whether the message should only be visible to the user who started the interaction.
            If a view is sent with an ephemeral message and it has no timeout set then the timeout
            is set to 15 minutes.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.

        Raises
        ------
        HTTPException
            Sending the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        ValueError
            The length of ``embeds`` was invalid.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        payload: Dict[str, Any] = {
            "tts": tts,
        }

        if delete_after is not MISSING and ephemeral:
            raise ValueError("ephemeral messages can not be deleted via endpoints")

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError("cannot mix embed and embeds keyword arguments")

        if file is not MISSING and files is not MISSING:
            raise TypeError("cannot mix file and files keyword arguments")

        if view is not MISSING and components is not MISSING:
            raise TypeError("cannot mix view and components keyword arguments")

        if file is not MISSING:
            files = [file]

        if embed is not MISSING:
            embeds = [embed]

        if embeds:
            if len(embeds) > 10:
                raise ValueError("embeds cannot exceed maximum of 10 elements")
            payload["embeds"] = [e.to_dict() for e in embeds]
            for embed in embeds:
                if embed._files:
                    files = files or []
                    files += embed._files

        if files is not MISSING and len(files) > 10:
            raise ValueError("files cannot exceed maximum of 10 elements")

        previous_mentions: Optional[AllowedMentions] = getattr(
            self._parent._state, "allowed_mentions", None
        )
        if allowed_mentions:
            if previous_mentions is not None:
                payload["allowed_mentions"] = previous_mentions.merge(allowed_mentions).to_dict()
            else:
                payload["allowed_mentions"] = allowed_mentions.to_dict()
        elif previous_mentions is not None:
            payload["allowed_mentions"] = previous_mentions.to_dict()

        if content is not None:
            payload["content"] = str(content)

        if ephemeral:
            payload["flags"] = 64

        if view is not MISSING:
            payload["components"] = view.to_components()

        if components is not MISSING:
            payload["components"] = components_to_dict(components)

        parent = self._parent
        adapter = async_context.get()
        try:
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                type=InteractionResponseType.channel_message.value,
                data=payload,
                files=files or None,
            )
        except NotFound as e:
            if e.code == 10062:
                raise InteractionTimedOut(self._parent) from e
            raise
        finally:
            if files:
                for f in files:
                    f.close()

        self._responded = True

        if view is not MISSING:
            if ephemeral and view.timeout is None:
                view.timeout = 15 * 60.0

            self._parent._state.store_view(view)

        if delete_after is not MISSING:
            await self._parent.delete_original_message(delay=delete_after)

    async def edit_message(
        self,
        content: Optional[Any] = MISSING,
        *,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: List[Attachment] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        view: Optional[View] = MISSING,
        components: Optional[Components] = MISSING,
    ) -> None:
        """|coro|

        Responds to this interaction by editing the original message of
        a component interaction.

        .. note::
            If the original message has embeds with images that were created from local files
            (using the ``file`` parameter with :meth:`Embed.set_image` or :meth:`Embed.set_thumbnail`),
            those images will be removed if the message's attachments are edited in any way
            (i.e. by setting ``file``/``files``/``attachments``, or adding an embed with local files).

        Parameters
        ----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the content.
        embed: Optional[:class:`Embed`]
            The new embed to replace the original with. This cannot be mixed with the
            ``embeds`` parameter.
            Could be ``None`` to remove the embed.
        embeds: List[:class:`Embed`]
            The new embeds to replace the original with. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
            To remove all embeds ``[]`` should be passed.
        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
            Files will be appended to the message.

            .. versionadded:: 2.2

        files: List[:class:`File`]
            A list of files to upload. This cannot be mixed with the ``file`` parameter.
            Files will be appended to the message.

            .. versionadded:: 2.2

        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all existing attachments are removed.
            Keeps existing attachments if not provided.

            .. versionadded:: 2.4

        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
        view: Optional[:class:`~disnake.ui.View`]
            The updated view to update this message with. This can not be mixed with ``components``.
            If ``None`` is passed then the view is removed.
        components: Optional[|components_type|]
            A list of components to update this message with. This can not be mixed with ``view``.
            If ``None`` is passed then the components are removed.

            .. versionadded:: 2.4

        Raises
        ------
        HTTPException
            Editing the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        msg: Optional[Message] = getattr(parent, "message", None)
        state = parent._state
        message_id = msg.id if msg else None
        if parent.type is not InteractionType.component:
            return
        parent = cast(MessageInteraction, parent)

        payload = {}
        if content is not MISSING:
            payload["content"] = None if content is None else str(content)
        if embed is not MISSING and embeds is not MISSING:
            raise TypeError("cannot mix both embed and embeds keyword arguments")

        if embed is not MISSING:
            embeds = [] if embed is None else [embed]
        if embeds is not MISSING:
            payload["embeds"] = [e.to_dict() for e in embeds]
            for embed in embeds:
                if embed._files:
                    raise NotImplementedError(
                        "Embed images in edit interaction responses are not supported"
                    )

        if file is not MISSING and files is not MISSING:
            raise TypeError("cannot mix file and files keyword arguments")

        if file is not MISSING:
            files = [file]

        if files is not MISSING and len(files) > 10:
            raise ValueError("files cannot exceed maximum of 10 elements")

        previous_mentions: Optional[AllowedMentions] = getattr(
            self._parent._state, "allowed_mentions", None
        )
        if allowed_mentions:
            if previous_mentions is not None:
                payload["allowed_mentions"] = previous_mentions.merge(allowed_mentions).to_dict()
            else:
                payload["allowed_mentions"] = allowed_mentions.to_dict()
        elif previous_mentions is not None:
            payload["allowed_mentions"] = previous_mentions.to_dict()

        # if no attachment list was provided but we're uploading new files,
        # use current attachments as the base
        if attachments is MISSING and (file or files):
            attachments = parent.message.attachments
        if attachments is not MISSING:
            payload["attachments"] = [a.to_dict() for a in attachments]

        if view is not MISSING and components is not MISSING:
            raise TypeError("cannot mix view and components keyword arguments")

        if view is not MISSING:
            if message_id:
                state.prevent_view_updates_for(message_id)
            payload["components"] = [] if view is None else view.to_components()

        if components is not MISSING:
            payload["components"] = [] if components is None else components_to_dict(components)

        adapter = async_context.get()
        try:
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                type=InteractionResponseType.message_update.value,
                data=payload,
                files=files,
            )
        finally:
            if files:
                for f in files:
                    f.close()

        if view and not view.is_finished():
            state.store_view(view, message_id)

        self._responded = True

    async def autocomplete(self, *, choices: Choices) -> None:
        """|coro|

        Responds to this interaction by displaying a list of possible autocomplete results.
        Only works for autocomplete interactions.

        Parameters
        ----------
        choices: Union[List[:class:`OptionChoice`], List[Union[:class:`str`, :class:`int`]], Dict[:class:`str`, Union[:class:`str`, :class:`int`]]]
            The list of choices to suggest.

        Raises
        ------
        HTTPException
            Autocomplete response has failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        choices_data: List[ApplicationCommandOptionChoicePayload]
        if isinstance(choices, Mapping):
            choices_data = [{"name": n, "value": v} for n, v in choices.items()]
        else:
            choices_data = []
            value: ApplicationCommandOptionChoicePayload
            for c in choices:
                if isinstance(c, OptionChoice):
                    value = c.to_dict()
                else:
                    value = {"name": str(c), "value": c}
                choices_data.append(value)

        parent = self._parent
        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            type=InteractionResponseType.application_command_autocomplete_result.value,
            data={"choices": choices_data},
        )

        self._responded = True

    @overload
    async def send_modal(self, modal: Modal) -> None:
        ...

    @overload
    async def send_modal(
        self,
        *,
        title: str,
        custom_id: str,
        components: Components,
    ) -> None:
        ...

    async def send_modal(
        self,
        modal: Modal = None,
        *,
        title: str = None,
        custom_id: str = None,
        components: Components = None,
    ) -> None:
        """|coro|

        Responds to this interaction by displaying a modal.

        .. versionadded:: 2.4

        .. note::

            Not passing the ``modal`` parameter here will not register a callback, and a :func:`on_modal_submit`
            interaction will need to be handled manually.

        Parameters
        ----------
        modal: :class:`~.ui.Modal`
            The modal to display. This cannot be mixed with the ``title``, ``custom_id`` and ``components`` parameters.
        title: :class:`str`
            The title of the modal. This cannot be mixed with the ``modal`` parameter.
        custom_id: :class:`str`
            The ID of the modal that gets received during an interaction.
            This cannot be mixed with the ``modal`` parameter.
        components: |components_type|
            The components to display in the modal. A maximum of 5.
            This cannot be mixed with the ``modal`` parameter.

        Raises
        ------
        TypeError
            Cannot mix the ``modal`` parameter and the ``title``, ``custom_id``, ``components`` parameters.
        ValueError
            Maximum number of components (5) exceeded.
        HTTPException
            Displaying the modal failed.
        ModalChainNotSupported
            This interaction cannot be responded with a modal.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if modal is not None and any((title, components, custom_id)):
            raise TypeError(f"Cannot mix modal argument and title, custom_id, components arguments")

        parent = self._parent

        if parent.type is InteractionType.modal_submit:
            raise ModalChainNotSupported(parent)  # type: ignore

        if self._responded:
            raise InteractionResponded(parent)

        modal_data: ModalPayload

        if modal is not None:
            modal_data = modal.to_components()
        elif title and components and custom_id:

            rows = components_to_dict(components)
            if len(rows) > 5:
                raise ValueError("Maximum number of components exceeded.")

            modal_data = {
                "title": title,
                "custom_id": custom_id,
                "components": rows,
            }
        else:
            raise TypeError("Either modal or title, custom_id, components must be provided")

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            type=InteractionResponseType.modal.value,
            data=modal_data,  # type: ignore
        )
        self._responded = True

        if modal is not None:
            parent._state.store_modal(parent.author.id, modal)


class _InteractionMessageState:
    __slots__ = ("_parent", "_interaction")

    def __init__(self, interaction: Interaction, parent: ConnectionState):
        self._interaction: Interaction = interaction
        self._parent: ConnectionState = parent

    def _get_guild(self, guild_id):
        return self._parent._get_guild(guild_id)

    def store_user(self, data):
        return self._parent.store_user(data)

    def create_user(self, data):
        return self._parent.create_user(data)

    @property
    def http(self):
        return self._parent.http

    def __getattr__(self, attr):
        return getattr(self._parent, attr)


class InteractionMessage(Message):
    """Represents the original interaction response message.

    This allows you to edit or delete the message associated with
    the interaction response. To retrieve this object see :meth:`Interaction.original_message`.

    This inherits from :class:`disnake.Message` with changes to
    :meth:`edit` and :meth:`delete` to work.

    .. versionadded:: 2.0
    """

    __slots__ = ()
    _state: _InteractionMessageState

    async def edit(
        self,
        content: Optional[str] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: List[Attachment] = MISSING,
        view: Optional[View] = MISSING,
        components: Optional[Components] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the message.

        .. note::
            If the original message has embeds with images that were created from local files
            (using the ``file`` parameter with :meth:`Embed.set_image` or :meth:`Embed.set_thumbnail`),
            those images will be removed if the message's attachments are edited in any way
            (i.e. by setting ``file``/``files``/``attachments``, or adding an embed with local files).

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content to edit the message with, or ``None`` to clear it.
        embed: Optional[:class:`Embed`]
            The new embed to replace the original with. This cannot be mixed with the
            ``embeds`` parameter.
            Could be ``None`` to remove the embed.
        embeds: List[:class:`Embed`]
            The new embeds to replace the original with. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
            To remove all embeds ``[]`` should be passed.
        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.
        files: List[:class:`File`]
            A list of files to upload. This cannot be mixed with the ``file`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all existing attachments are removed.
            Keeps existing attachments if not provided.

            .. versionadded:: 2.2

        view: Optional[:class:`~disnake.ui.View`]
            The updated view to update this message with. This can not be mixed with ``components``.
            If ``None`` is passed then the view is removed.
        components: Optional[|components_type|]
            A list of components to update this message with. This can not be mixed with ``view``.
            If ``None`` is passed then the components are removed.

            .. versionadded:: 2.4

        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.

        Raises
        ------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        -------
        :class:`InteractionMessage`
            The newly edited message.
        """
        # if no attachment list was provided but we're uploading new files,
        # use current attachments as the base
        if attachments is MISSING and (file or files):
            attachments = self.attachments

        return await self._state._interaction.edit_original_message(
            content=content,
            embeds=embeds,
            embed=embed,
            file=file,
            files=files,
            attachments=attachments,
            view=view,
            components=components,
            allowed_mentions=allowed_mentions,
        )

    async def delete(self, *, delay: Optional[float] = None) -> None:
        """|coro|

        Deletes the message.

        Parameters
        ----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the message.
            The waiting is done in the background and deletion failures are ignored.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the message.
        NotFound
            The message was deleted already.
        HTTPException
            Deleting the message failed.
        """
        if delay is not None:

            async def inner_call(delay: float = delay):
                await asyncio.sleep(delay)
                try:
                    await self._state._interaction.delete_original_message()
                except HTTPException:
                    pass

            asyncio.create_task(inner_call())
        else:
            await self._state._interaction.delete_original_message()
