# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import logging
import re
from contextvars import ContextVar
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
)
from urllib.parse import quote as urlquote

import aiohttp

from .. import utils
from ..asset import Asset
from ..channel import PartialMessageable
from ..enums import WebhookType, try_enum
from ..errors import DiscordServerError, Forbidden, HTTPException, NotFound, WebhookTokenMissing
from ..flags import MessageFlags
from ..http import Route, set_attachments, to_multipart, to_multipart_with_attachments
from ..message import Message
from ..mixins import Hashable
from ..ui.action_row import MessageUIComponent, components_to_dict
from ..user import BaseUser, User

__all__ = (
    "Webhook",
    "WebhookMessage",
    "PartialWebhookChannel",
    "PartialWebhookGuild",
)

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    import datetime

    from ..abc import Snowflake
    from ..asset import AssetBytes
    from ..channel import ForumChannel, TextChannel, VoiceChannel
    from ..embeds import Embed
    from ..file import File
    from ..guild import Guild
    from ..http import Response
    from ..mentions import AllowedMentions
    from ..message import Attachment
    from ..state import ConnectionState
    from ..sticker import GuildSticker, StickerItem
    from ..types.message import Message as MessagePayload
    from ..types.webhook import Webhook as WebhookPayload
    from ..ui.action_row import Components
    from ..ui.view import View

MISSING = utils.MISSING


class AsyncDeferredLock:
    def __init__(self, lock: asyncio.Lock):
        self.lock = lock
        self.delta: Optional[float] = None

    async def __aenter__(self):
        await self.lock.acquire()
        return self

    def delay_by(self, delta: float) -> None:
        self.delta = delta

    async def __aexit__(self, type, value, traceback):
        if self.delta:
            await asyncio.sleep(self.delta)
        self.lock.release()


class AsyncWebhookAdapter:
    def __init__(self):
        self._locks: Dict[Any, asyncio.Lock] = {}

    async def request(
        self,
        route: Route,
        session: aiohttp.ClientSession,
        *,
        payload: Optional[Dict[str, Any]] = None,
        multipart: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[File]] = None,
        reason: Optional[str] = None,
        auth_token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        headers: Dict[str, str] = {}
        files = files or []
        to_send: Optional[Union[str, aiohttp.FormData]] = None
        bucket = (route.webhook_id, route.webhook_token)

        try:
            lock = self._locks[bucket]
        except KeyError:
            self._locks[bucket] = lock = asyncio.Lock()

        if payload is not None:
            headers["Content-Type"] = "application/json"
            to_send = utils._to_json(payload)

        if auth_token is not None:
            headers["Authorization"] = f"Bot {auth_token}"

        if reason is not None:
            headers["X-Audit-Log-Reason"] = urlquote(reason, safe="/ ")

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None
        method = route.method
        url = route.url
        webhook_id = route.webhook_id

        async with AsyncDeferredLock(lock) as lock:
            for attempt in range(5):
                for file in files:
                    file.reset(seek=attempt)

                if multipart:
                    # NOTE: for `quote_fields`, see https://github.com/aio-libs/aiohttp/issues/4012
                    form_data = aiohttp.FormData(quote_fields=False)
                    for p in multipart:
                        # manually escape chars, just in case
                        name = re.sub(
                            r"[^\x21\x23-\x5b\x5d-\x7e]", lambda m: f"\\{m.group(0)}", p["name"]
                        )
                        form_data.add_field(
                            name=name, **{k: v for k, v in p.items() if k != "name"}
                        )
                    to_send = form_data

                try:
                    async with session.request(
                        method, url, data=to_send, headers=headers, params=params
                    ) as response:
                        _log.debug(
                            "Webhook ID %s with %s %s with %s has returned status code %s",
                            webhook_id,
                            method,
                            url,
                            to_send,
                            response.status,
                        )
                        data = (await response.text(encoding="utf-8")) or None
                        if data and response.headers["Content-Type"] == "application/json":
                            data = utils._from_json(data)

                        remaining = response.headers.get("X-Ratelimit-Remaining")
                        if remaining == "0" and response.status != 429:
                            delta = utils._parse_ratelimit_header(response)
                            _log.debug(
                                "Webhook ID %s has been pre-emptively rate limited, waiting %.2f seconds",
                                webhook_id,
                                delta,
                            )
                            lock.delay_by(delta)

                        if 300 > response.status >= 200:
                            _log.debug("%s %s has received %s", method, url, data)
                            return data

                        if response.status == 429:
                            if not response.headers.get("Via"):
                                raise HTTPException(response, data)

                            retry_after: float = data["retry_after"]  # type: ignore
                            _log.warning(
                                "Webhook ID %s is rate limited. Retrying in %.2f seconds",
                                webhook_id,
                                retry_after,
                            )
                            await asyncio.sleep(retry_after)
                            continue

                        if response.status >= 500:
                            await asyncio.sleep(1 + attempt * 2)
                            continue

                        if response.status == 403:
                            raise Forbidden(response, data)
                        elif response.status == 404:
                            raise NotFound(response, data)
                        else:
                            raise HTTPException(response, data)

                except OSError as e:
                    if attempt < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + attempt * 2)
                        continue
                    raise

            if response:
                if response.status >= 500:
                    raise DiscordServerError(response, data)
                raise HTTPException(response, data)

            raise RuntimeError("Unreachable code in HTTP handling.")

    def delete_webhook(
        self,
        webhook_id: int,
        *,
        token: Optional[str] = None,
        session: aiohttp.ClientSession,
        reason: Optional[str] = None,
    ) -> Response[None]:
        route = Route("DELETE", "/webhooks/{webhook_id}", webhook_id=webhook_id)
        return self.request(route, session, reason=reason, auth_token=token)

    def delete_webhook_with_token(
        self,
        webhook_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
        reason: Optional[str] = None,
    ) -> Response[None]:
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}",
            webhook_id=webhook_id,
            webhook_token=token,
        )
        return self.request(route, session, reason=reason)

    def edit_webhook(
        self,
        webhook_id: int,
        token: str,
        payload: Dict[str, Any],
        *,
        session: aiohttp.ClientSession,
        reason: Optional[str] = None,
    ) -> Response[WebhookPayload]:
        route = Route("PATCH", "/webhooks/{webhook_id}", webhook_id=webhook_id)
        return self.request(route, session, reason=reason, payload=payload, auth_token=token)

    def edit_webhook_with_token(
        self,
        webhook_id: int,
        token: str,
        payload: Dict[str, Any],
        *,
        session: aiohttp.ClientSession,
        reason: Optional[str] = None,
    ) -> Response[WebhookPayload]:
        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}",
            webhook_id=webhook_id,
            webhook_token=token,
        )
        return self.request(route, session, reason=reason, payload=payload)

    def execute_webhook(
        self,
        webhook_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
        payload: Optional[Dict[str, Any]] = None,
        multipart: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[File]] = None,
        thread_id: Optional[int] = None,
        wait: bool = False,
    ) -> Response[Optional[MessagePayload]]:
        params = {"wait": int(wait)}
        if thread_id:
            params["thread_id"] = thread_id
        route = Route(
            "POST",
            "/webhooks/{webhook_id}/{webhook_token}",
            webhook_id=webhook_id,
            webhook_token=token,
        )
        return self.request(
            route, session, payload=payload, multipart=multipart, files=files, params=params
        )

    def get_webhook_message(
        self,
        webhook_id: int,
        token: str,
        message_id: int,
        *,
        session: aiohttp.ClientSession,
    ) -> Response[MessagePayload]:
        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=token,
            message_id=message_id,
        )
        return self.request(route, session)

    def edit_webhook_message(
        self,
        webhook_id: int,
        token: str,
        message_id: int,
        *,
        session: aiohttp.ClientSession,
        payload: Optional[Dict[str, Any]] = None,
        multipart: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[File]] = None,
    ) -> Response[Message]:
        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=token,
            message_id=message_id,
        )
        return self.request(route, session, payload=payload, multipart=multipart, files=files)

    def delete_webhook_message(
        self,
        webhook_id: int,
        token: str,
        message_id: int,
        *,
        session: aiohttp.ClientSession,
    ) -> Response[None]:
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=token,
            message_id=message_id,
        )
        return self.request(route, session)

    def fetch_webhook(
        self,
        webhook_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
    ) -> Response[WebhookPayload]:
        route = Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id)
        return self.request(route, session=session, auth_token=token)

    def fetch_webhook_with_token(
        self,
        webhook_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
    ) -> Response[WebhookPayload]:
        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}",
            webhook_id=webhook_id,
            webhook_token=token,
        )
        return self.request(route, session=session)

    def create_interaction_response(
        self,
        interaction_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
        type: int,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[List[File]] = None,
    ) -> Response[None]:
        route = Route(
            "POST",
            "/interactions/{webhook_id}/{webhook_token}/callback",
            webhook_id=interaction_id,
            webhook_token=token,
        )

        payload: Dict[str, Any] = {
            "type": type,
        }

        if data is not None:
            if files:
                set_attachments(data, files)
            payload["data"] = data

        if files:
            multipart = to_multipart(payload, files)
            return self.request(route, session=session, multipart=multipart, files=files)
        return self.request(route, session=session, payload=payload)

    def get_original_interaction_response(
        self,
        application_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
    ) -> Response[MessagePayload]:
        r = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=application_id,
            webhook_token=token,
        )
        return self.request(r, session=session)

    def edit_original_interaction_response(
        self,
        application_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
        payload: Optional[Dict[str, Any]] = None,
        multipart: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[File]] = None,
    ) -> Response[MessagePayload]:
        r = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=application_id,
            webhook_token=token,
        )
        return self.request(r, session, payload=payload, multipart=multipart, files=files)

    def delete_original_interaction_response(
        self,
        application_id: int,
        token: str,
        *,
        session: aiohttp.ClientSession,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{wehook_token}/messages/@original",
            webhook_id=application_id,
            wehook_token=token,
        )
        return self.request(r, session=session)


class DictPayloadParameters(NamedTuple):
    payload: Dict[str, Any]
    files: Optional[List[File]]


class PayloadParameters(NamedTuple):
    payload: Optional[Dict[str, Any]]
    multipart: Optional[List[Dict[str, Any]]]
    files: Optional[List[File]]


def handle_message_parameters_dict(
    content: Optional[str] = MISSING,
    *,
    username: str = MISSING,
    avatar_url: Any = MISSING,
    tts: bool = False,
    ephemeral: Optional[bool] = None,
    suppress_embeds: Optional[bool] = None,
    file: File = MISSING,
    files: List[File] = MISSING,
    attachments: Optional[List[Attachment]] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: List[Embed] = MISSING,
    view: Optional[View] = MISSING,
    components: Optional[Components[MessageUIComponent]] = MISSING,
    allowed_mentions: Optional[AllowedMentions] = MISSING,
    previous_allowed_mentions: Optional[AllowedMentions] = None,
    stickers: Sequence[Union[GuildSticker, StickerItem]] = MISSING,
    thread_name: Optional[str] = None,
) -> DictPayloadParameters:
    if files is not MISSING and file is not MISSING:
        raise TypeError("Cannot mix file and files keyword arguments.")
    if embeds is not MISSING and embed is not MISSING:
        raise TypeError("Cannot mix embed and embeds keyword arguments.")
    if view is not MISSING and components is not MISSING:
        raise TypeError("Cannot mix view and components keyword arguments.")

    if file is not MISSING:
        files = [file]

    payload = {}
    if embed is not MISSING:
        embeds = [embed] if embed else []
    if embeds is not MISSING:
        if len(embeds) > 10:
            raise ValueError("embeds has a maximum of 10 elements.")
        payload["embeds"] = [e.to_dict() for e in embeds]
        for embed in embeds:
            if embed._files:
                files = files or []
                files.extend(embed._files.values())

    if content is not MISSING:
        payload["content"] = str(content) if content is not None else None
    if view is not MISSING:
        payload["components"] = view.to_components() if view is not None else []
    if components is not MISSING:
        payload["components"] = [] if components is None else components_to_dict(components)

    if attachments is not MISSING:
        payload["attachments"] = [] if attachments is None else [a.to_dict() for a in attachments]

    payload["tts"] = tts
    if avatar_url:
        payload["avatar_url"] = str(avatar_url)
    if username:
        payload["username"] = username

    if ephemeral is not None or suppress_embeds is not None:
        payload["flags"] = 0
        if suppress_embeds:
            payload["flags"] |= MessageFlags.suppress_embeds.flag
        if ephemeral:
            payload["flags"] |= MessageFlags.ephemeral.flag

    if allowed_mentions:
        if previous_allowed_mentions is not None:
            payload["allowed_mentions"] = previous_allowed_mentions.merge(
                allowed_mentions
            ).to_dict()
        else:
            payload["allowed_mentions"] = allowed_mentions.to_dict()
    elif previous_allowed_mentions is not None:
        payload["allowed_mentions"] = previous_allowed_mentions.to_dict()

    if stickers is not MISSING:
        payload["sticker_ids"] = [s.id for s in stickers]

    if thread_name is not None:
        payload["thread_name"] = thread_name

    return DictPayloadParameters(payload=payload, files=files)


def handle_message_parameters(
    content: Optional[str] = MISSING,
    *,
    username: str = MISSING,
    avatar_url: Any = MISSING,
    tts: bool = False,
    ephemeral: Optional[bool] = None,
    suppress_embeds: Optional[bool] = None,
    file: File = MISSING,
    files: List[File] = MISSING,
    attachments: Optional[List[Attachment]] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: List[Embed] = MISSING,
    view: Optional[View] = MISSING,
    components: Optional[Components[MessageUIComponent]] = MISSING,
    allowed_mentions: Optional[AllowedMentions] = MISSING,
    previous_allowed_mentions: Optional[AllowedMentions] = None,
    stickers: Sequence[Union[GuildSticker, StickerItem]] = MISSING,
    thread_name: Optional[str] = None,
) -> PayloadParameters:
    params = handle_message_parameters_dict(
        content=content,
        username=username,
        avatar_url=avatar_url,
        tts=tts,
        ephemeral=ephemeral,
        suppress_embeds=suppress_embeds,
        file=file,
        files=files,
        attachments=attachments,
        embed=embed,
        embeds=embeds,
        view=view,
        components=components,
        allowed_mentions=allowed_mentions,
        previous_allowed_mentions=previous_allowed_mentions,
        stickers=stickers,
        thread_name=thread_name,
    )

    if params.files:
        multipart = to_multipart_with_attachments(params.payload, params.files)
        return PayloadParameters(payload=None, multipart=multipart, files=params.files)

    return PayloadParameters(payload=params.payload, multipart=None, files=params.files)


async_context: ContextVar[AsyncWebhookAdapter] = ContextVar(
    "async_webhook_context", default=AsyncWebhookAdapter()
)


class PartialWebhookChannel(Hashable):
    """Represents a partial channel for webhooks.

    These are typically given for channel follower webhooks.

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The partial channel's ID.
    name: :class:`str`
        The partial channel's name.
    """

    __slots__ = ("id", "name")

    def __init__(self, *, data):
        self.id = int(data["id"])
        self.name = data["name"]

    def __repr__(self):
        return f"<PartialWebhookChannel name={self.name!r} id={self.id}>"


class PartialWebhookGuild(Hashable):
    """Represents a partial guild for webhooks.

    These are typically given for channel follower webhooks.

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The partial guild's ID.
    name: :class:`str`
        The partial guild's name.
    """

    __slots__ = ("id", "name", "_icon", "_state")

    def __init__(self, *, data, state):
        self._state = state
        self.id = int(data["id"])
        self.name = data["name"]
        self._icon = data["icon"]

    def __repr__(self):
        return f"<PartialWebhookGuild name={self.name!r} id={self.id}>"

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild's icon asset, if available."""
        if self._icon is None:
            return None
        return Asset._from_guild_icon(self._state, self.id, self._icon)


class _FriendlyHttpAttributeErrorHelper:
    __slots__ = ()

    def __getattr__(self, attr):
        raise AttributeError("PartialWebhookState does not support http methods.")


WebhookT = TypeVar("WebhookT", bound="BaseWebhook")


class _WebhookState(Generic[WebhookT]):
    __slots__ = ("_parent", "_webhook")

    def __init__(self, webhook: WebhookT, parent: Optional[Union[ConnectionState, _WebhookState]]):
        self._webhook: WebhookT = webhook

        self._parent: Optional[ConnectionState]
        if isinstance(parent, _WebhookState):
            self._parent = None
        else:
            self._parent = parent

    def _get_guild(self, guild_id):
        if self._parent is not None:
            return self._parent._get_guild(guild_id)
        return None

    def store_user(self, data):
        if self._parent is not None:
            return self._parent.store_user(data)
        # state parameter is artificial
        return BaseUser(state=self, data=data)  # type: ignore

    def create_user(self, data):
        # state parameter is artificial
        return BaseUser(state=self, data=data)  # type: ignore

    @property
    def http(self):
        if self._parent is not None:
            return self._parent.http

        # Some data classes assign state.http and that should be kosher
        # however, using it should result in a late-binding error.
        return _FriendlyHttpAttributeErrorHelper()

    def __getattr__(self, attr):
        if self._parent is not None:
            return getattr(self._parent, attr)

        raise AttributeError(f"PartialWebhookState does not support {attr!r}.")


class WebhookMessage(Message):
    """Represents a message sent from your webhook.

    This allows you to edit or delete a message sent by your
    webhook.

    This inherits from :class:`disnake.Message` with changes to
    :meth:`edit` and :meth:`delete` to work.

    .. versionadded:: 1.6
    """

    _state: _WebhookState[Webhook]

    async def edit(
        self,
        content: Optional[str] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: Optional[List[Attachment]] = MISSING,
        view: Optional[View] = MISSING,
        components: Optional[Components[MessageUIComponent]] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> WebhookMessage:
        """|coro|

        Edits the message.

        .. versionadded:: 1.6

        .. versionchanged:: 2.0
            The edit is no longer in-place, instead the newly edited message is returned.

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
            The new embed to replace the original with. This cannot be mixed with the ``embeds`` parameter.
            Could be ``None`` to remove the embed.
        embeds: List[:class:`Embed`]
            The new embeds to replace the original with. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
            To remove all embeds ``[]`` should be passed.
        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.

            .. versionadded:: 2.0

        files: List[:class:`File`]
            A list of files to upload. This cannot be mixed with the ``file`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.

            .. versionadded:: 2.0

        attachments: Optional[List[:class:`Attachment`]]
            A list of attachments to keep in the message.
            If ``[]`` or ``None`` is passed then all existing attachments are removed.
            Keeps existing attachments if not provided.

            .. versionadded:: 2.2

            .. versionchanged:: 2.5
                Supports passing ``None`` to clear attachments.

        view: Optional[:class:`~disnake.ui.View`]
            The view to update this message with. This cannot be mixed with ``components``.
            If ``None`` is passed then the view is removed.

            .. versionadded:: 2.0

        components: Optional[|components_type|]
            A list of components to update the message with. This cannot be mixed with ``view``.
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
            The length of ``embeds`` was invalid
        WebhookTokenMissing
            There was no token associated with this webhook.

        Returns
        -------
        :class:`WebhookMessage`
            The newly edited message.
        """
        # if no attachment list was provided but we're uploading new files,
        # use current attachments as the base
        if attachments is MISSING and (file or files):
            attachments = self.attachments

        return await self._state._webhook.edit_message(
            self.id,
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
                    await self._state._webhook.delete_message(self.id)
                except HTTPException:
                    pass

            asyncio.create_task(inner_call())
        else:
            await self._state._webhook.delete_message(self.id)


class BaseWebhook(Hashable):
    __slots__: Tuple[str, ...] = (
        "id",
        "type",
        "guild_id",
        "channel_id",
        "token",
        "auth_token",
        "user",
        "name",
        "_avatar",
        "source_channel",
        "source_guild",
        "application_id",
        "_state",
    )

    def __init__(
        self,
        data: WebhookPayload,
        token: Optional[str] = None,
        state: Optional[ConnectionState] = None,
    ):
        self.auth_token: Optional[str] = token
        self._state: Union[ConnectionState, _WebhookState] = state or _WebhookState(
            self, parent=state
        )
        self._update(data)

    def _update(self, data: WebhookPayload):
        self.id = int(data["id"])
        self.type = try_enum(WebhookType, int(data["type"]))
        self.channel_id = utils._get_as_snowflake(data, "channel_id")
        self.guild_id = utils._get_as_snowflake(data, "guild_id")
        self.name = data.get("name")
        self._avatar = data.get("avatar")
        self.token = data.get("token")

        user = data.get("user")
        self.user: Optional[Union[BaseUser, User]] = None
        if user is not None:
            # state parameter may be _WebhookState
            self.user = User(state=self._state, data=user)  # type: ignore

        source_channel = data.get("source_channel")
        if source_channel:
            source_channel = PartialWebhookChannel(data=source_channel)

        self.source_channel: Optional[PartialWebhookChannel] = source_channel

        source_guild = data.get("source_guild")
        if source_guild:
            source_guild = PartialWebhookGuild(data=source_guild, state=self._state)

        self.source_guild: Optional[PartialWebhookGuild] = source_guild

        self.application_id: Optional[int] = utils._get_as_snowflake(data, "application_id")

    def is_partial(self) -> bool:
        """Whether the webhook is a "partial" webhook.

        .. versionadded:: 2.0

        :return type: :class:`bool`
        """
        return self.channel_id is None

    def is_authenticated(self) -> bool:
        """Whether the webhook is authenticated with a bot token.

        .. versionadded:: 2.0

        :return type: :class:`bool`
        """
        return self.auth_token is not None

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild this webhook belongs to.

        If this is a partial webhook, then this will always return ``None``.
        """
        return self._state and self._state._get_guild(self.guild_id)

    @property
    def channel(self) -> Optional[Union[TextChannel, VoiceChannel, ForumChannel]]:
        """Optional[Union[:class:`TextChannel`, :class:`VoiceChannel`, :class:`ForumChannel`]]: The channel this webhook belongs to.

        If this is a partial webhook, then this will always return ``None``.

        Webhooks in :class:`ForumChannel`\\s can not send messages directly,
        they can only create new threads (see ``thread_name`` for :attr:`Webhook.send`)
        and interact with existing threads.
        """
        guild = self.guild
        return guild and guild.get_channel(self.channel_id)  # type: ignore

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the webhook's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def avatar(self) -> Asset:
        """:class:`Asset`: Returns an :class:`Asset` for the avatar the webhook has.

        If the webhook does not have a traditional avatar, an asset for
        the default avatar is returned instead.
        """
        if self._avatar is None:
            # Default is always blurple apparently
            return Asset._from_default_avatar(self._state, 0)
        return Asset._from_avatar(self._state, self.id, self._avatar)


class Webhook(BaseWebhook):
    """Represents an asynchronous Discord webhook.

    Webhooks are a form to send messages to channels in Discord without a
    bot user or authentication.

    There are two main ways to use Webhooks. The first is through the ones
    received by the library such as :meth:`.Guild.webhooks`, :meth:`.TextChannel.webhooks`,
    and :meth:`.VoiceChannel.webhooks`. The ones received by the library will
    automatically be bound using the library's internal HTTP session.

    The second form involves creating a webhook object manually using the
    :meth:`~.Webhook.from_url` or :meth:`~.Webhook.partial` classmethods.

    For example, creating a webhook from a URL and using :doc:`aiohttp <aio:index>`:

    .. code-block:: python3

        from disnake import Webhook
        import aiohttp

        async def foo():
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url('url-here', session=session)
                await webhook.send('Hello World', username='Foo')

    For a synchronous counterpart, see :class:`SyncWebhook`.

    .. container:: operations

        .. describe:: x == y

            Checks if two webhooks are equal.

        .. describe:: x != y

            Checks if two webhooks are not equal.

        .. describe:: hash(x)

            Returns the webhooks's hash.

    .. versionchanged:: 1.4
        Webhooks are now comparable and hashable.

    Attributes
    ----------
    id: :class:`int`
        The webhook's ID
    type: :class:`WebhookType`
        The webhook's type.

        .. versionadded:: 1.3

    token: Optional[:class:`str`]
        The authentication token of the webhook. If this is ``None``
        then the webhook cannot be used to make requests.
    guild_id: Optional[:class:`int`]
        The guild ID this webhook belongs to.
    channel_id: Optional[:class:`int`]
        The channel ID this webhook belongs to.
    user: Optional[:class:`abc.User`]
        The user this webhook was created by. If the webhook was
        received without authentication then this will be ``None``.
    name: Optional[:class:`str`]
        The default name of the webhook.
    source_guild: Optional[:class:`PartialWebhookGuild`]
        The guild of the channel that this webhook is following.
        Only given if :attr:`type` is :attr:`WebhookType.channel_follower`.

        .. versionadded:: 2.0

    source_channel: Optional[:class:`PartialWebhookChannel`]
        The channel that this webhook is following.
        Only given if :attr:`type` is :attr:`WebhookType.channel_follower`.

        .. versionadded:: 2.0

    application_id: Optional[:class:`int`]
        The ID of the application associated with this webhook, if it was created by an application.

        .. versionadded:: 2.6
    """

    __slots__: Tuple[str, ...] = ("session",)

    def __init__(
        self,
        data: WebhookPayload,
        session: aiohttp.ClientSession,
        token: Optional[str] = None,
        state=None,
    ):
        super().__init__(data, token, state)
        self.session = session

    def __repr__(self):
        return f"<Webhook id={self.id!r}>"

    @property
    def url(self) -> str:
        """:class:`str` : Returns the webhook's url."""
        return f"https://discord.com/api/webhooks/{self.id}/{self.token}"

    @classmethod
    def partial(
        cls, id: int, token: str, *, session: aiohttp.ClientSession, bot_token: Optional[str] = None
    ) -> Webhook:
        """Creates a partial :class:`Webhook`.

        Parameters
        ----------
        id: :class:`int`
            The webhook's ID.
        token: :class:`str`
            The webhook's authentication token.
        session: :class:`aiohttp.ClientSession`
            The session to use to send requests with. Note
            that the library does not manage the session and
            will not close it.

            .. versionadded:: 2.0

        bot_token: Optional[:class:`str`]
            The bot authentication token for authenticated requests
            involving the webhook.

            .. versionadded:: 2.0

        Returns
        -------
        :class:`Webhook`
            A partial :class:`Webhook`.
            A partial webhook is just a webhook object with an ID and a token.
        """
        data: WebhookPayload = {
            "id": id,
            "type": 1,
            "token": token,
        }

        return cls(data, session, token=bot_token)

    @classmethod
    def from_url(
        cls, url: str, *, session: aiohttp.ClientSession, bot_token: Optional[str] = None
    ) -> Webhook:
        """Creates a partial :class:`Webhook` from a webhook URL.

        .. versionchanged:: 2.6
            Raises :exc:`ValueError` instead of ``InvalidArgument``.

        Parameters
        ----------
        url: :class:`str`
            The webhook's URL.
        session: :class:`aiohttp.ClientSession`
            The session to use to send requests with. Note
            that the library does not manage the session and
            will not close it.

            .. versionadded:: 2.0

        bot_token: Optional[:class:`str`]
            The bot authentication token for authenticated requests
            involving the webhook.

            .. versionadded:: 2.0

        Raises
        ------
        ValueError
            The URL is invalid.

        Returns
        -------
        :class:`Webhook`
            A partial :class:`Webhook`.
            A partial webhook is just a webhook object with an ID and a token.
        """
        m = re.search(
            r"discord(?:app)?.com/api/webhooks/(?P<id>[0-9]{17,19})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})",
            url,
        )
        if m is None:
            raise ValueError("Invalid webhook URL given.")

        data: Dict[str, Any] = m.groupdict()
        data["type"] = 1
        return cls(data, session, token=bot_token)  # type: ignore

    @classmethod
    def _as_follower(cls, data, *, channel, user) -> Webhook:
        name = f"{channel.guild} #{channel}"
        feed: WebhookPayload = {
            "id": data["webhook_id"],
            "type": 2,
            "name": name,
            "channel_id": channel.id,
            "guild_id": channel.guild.id,
            "user": {
                "username": user.name,
                "discriminator": user.discriminator,
                "id": user.id,
                "avatar": user._avatar,
            },
        }

        state = channel._state
        session = channel._state.http._HTTPClient__session
        return cls(feed, session=session, state=state, token=state.http.token)

    @classmethod
    def from_state(cls, data, state) -> Webhook:
        session = state.http._HTTPClient__session
        return cls(data, session=session, state=state, token=state.http.token)

    async def fetch(self, *, prefer_auth: bool = True) -> Webhook:
        """|coro|

        Fetches the current webhook.

        This could be used to get a full webhook from a partial webhook.

        .. versionadded:: 2.0

        .. note::

            When fetching with an unauthenticated webhook, i.e.
            :meth:`is_authenticated` returns ``False``, then the
            returned webhook does not contain any user information.

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        prefer_auth: :class:`bool`
            Whether to use the bot token over the webhook token,
            if available. Defaults to ``True``.

        Raises
        ------
        HTTPException
            Could not fetch the webhook
        NotFound
            Could not find the webhook by this ID
        WebhookTokenMissing
            This webhook does not have a token associated with it.

        Returns
        -------
        :class:`Webhook`
            The fetched webhook.
        """
        adapter = async_context.get()

        if prefer_auth and self.auth_token:
            data = await adapter.fetch_webhook(self.id, self.auth_token, session=self.session)
        elif self.token:
            data = await adapter.fetch_webhook_with_token(self.id, self.token, session=self.session)
        else:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        return Webhook(data, self.session, token=self.auth_token, state=self._state)

    async def delete(self, *, reason: Optional[str] = None, prefer_auth: bool = True):
        """|coro|

        Deletes this Webhook.

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this webhook. Shows up on the audit log.

            .. versionadded:: 1.4

        prefer_auth: :class:`bool`
            Whether to use the bot token over the webhook token,
            if available. Defaults to ``True``.

            .. versionadded:: 2.0

        Raises
        ------
        HTTPException
            Deleting the webhook failed.
        NotFound
            This webhook does not exist.
        Forbidden
            You do not have permissions to delete this webhook.
        WebhookTokenMissing
            This webhook does not have a token associated with it.
        """
        if self.token is None and self.auth_token is None:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        adapter = async_context.get()

        if prefer_auth and self.auth_token:
            await adapter.delete_webhook(
                self.id, token=self.auth_token, session=self.session, reason=reason
            )
        elif self.token:
            await adapter.delete_webhook_with_token(
                self.id, self.token, session=self.session, reason=reason
            )

    async def edit(
        self,
        *,
        reason: Optional[str] = None,
        name: Optional[str] = MISSING,
        avatar: Optional[AssetBytes] = MISSING,
        channel: Optional[Snowflake] = None,
        prefer_auth: bool = True,
    ) -> Webhook:
        """|coro|

        Edits this Webhook.

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The webhook's new default name.
        avatar: Optional[|resource_type|]
            The webhook's new default avatar.

            .. versionchanged:: 2.5
                Now accepts various resource types in addition to :class:`bytes`.

        channel: Optional[:class:`abc.Snowflake`]
            The webhook's new channel. This requires an authenticated webhook.

            .. versionadded:: 2.0

        prefer_auth: :class:`bool`
            Whether to use the bot token over the webhook token
            if available. Defaults to ``True``.

            .. versionadded:: 2.0

        reason: Optional[:class:`str`]
            The reason for editing this webhook. Shows up on the audit log.

            .. versionadded:: 1.4

        Raises
        ------
        HTTPException
            Editing the webhook failed.
        NotFound
            This webhook does not exist or the ``avatar`` asset couldn't be found.
        TypeError
            The ``avatar`` asset is a lottie sticker (see :func:`Sticker.read`).
        WebhookTokenMissing
            This webhook does not have a token associated with it
            or it tried editing a channel without authentication.

        Returns
        -------
        :class:`Webhook`
            The newly edited webhook.
        """
        if self.token is None and self.auth_token is None:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        payload = {}
        if name is not MISSING:
            payload["name"] = str(name) if name is not None else None

        if avatar is not MISSING:
            payload["avatar"] = await utils._assetbytes_to_base64_data(avatar)

        adapter = async_context.get()

        data: Optional[WebhookPayload] = None
        # If a channel is given, always use the authenticated endpoint
        if channel is not None:
            if self.auth_token is None:
                raise WebhookTokenMissing("Editing channel requires authenticated webhook")

            payload["channel_id"] = channel.id
            data = await adapter.edit_webhook(
                self.id, self.auth_token, payload=payload, session=self.session, reason=reason
            )

        if prefer_auth and self.auth_token:
            data = await adapter.edit_webhook(
                self.id, self.auth_token, payload=payload, session=self.session, reason=reason
            )
        elif self.token:
            data = await adapter.edit_webhook_with_token(
                self.id, self.token, payload=payload, session=self.session, reason=reason
            )

        if data is None:
            raise RuntimeError("Unreachable code hit: data was not assigned")

        return Webhook(data=data, session=self.session, token=self.auth_token, state=self._state)

    def _create_message(self, data):
        state = _WebhookState(self, parent=self._state)
        # state may be artificial (unlikely at this point...)
        channel_id = int(data["channel_id"])
        # if the channel ID does not match, a new thread was created
        if self.channel_id != channel_id:
            guild = self.guild
            msg_channel = guild and guild.get_channel_or_thread(channel_id)
        else:
            msg_channel = self.channel
        if not msg_channel:
            # state may be artificial (unlikely at this point...)
            msg_channel = PartialMessageable(state=self._state, id=channel_id)  # type: ignore
        # state is artificial
        return WebhookMessage(data=data, state=state, channel=msg_channel)  # type: ignore

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        username: str = ...,
        avatar_url: Any = ...,
        tts: bool = ...,
        ephemeral: bool = ...,
        suppress_embeds: bool = ...,
        file: File = ...,
        files: List[File] = ...,
        embed: Embed = ...,
        embeds: List[Embed] = ...,
        allowed_mentions: AllowedMentions = ...,
        view: View = ...,
        components: Components[MessageUIComponent] = ...,
        thread: Snowflake = ...,
        thread_name: str = ...,
        wait: Literal[True],
        delete_after: float = ...,
    ) -> WebhookMessage:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        username: str = ...,
        avatar_url: Any = ...,
        tts: bool = ...,
        ephemeral: bool = ...,
        suppress_embeds: bool = ...,
        file: File = ...,
        files: List[File] = ...,
        embed: Embed = ...,
        embeds: List[Embed] = ...,
        allowed_mentions: AllowedMentions = ...,
        view: View = ...,
        components: Components[MessageUIComponent] = ...,
        thread: Snowflake = ...,
        thread_name: str = ...,
        wait: Literal[False] = ...,
        delete_after: float = ...,
    ) -> None:
        ...

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        username: str = MISSING,
        avatar_url: Any = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        suppress_embeds: bool = False,
        file: File = MISSING,
        files: List[File] = MISSING,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        view: View = MISSING,
        components: Components[MessageUIComponent] = MISSING,
        thread: Snowflake = MISSING,
        thread_name: Optional[str] = None,
        wait: bool = False,
        delete_after: float = MISSING,
    ) -> Optional[WebhookMessage]:
        """|coro|

        Sends a message using the webhook.

        The content must be a type that can convert to a string through ``str(content)``.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`File` object.

        If the ``embed`` parameter is provided, it must be of type :class:`Embed` and
        it must be a rich embed type. You cannot mix the ``embed`` parameter with the
        ``embeds`` parameter, which must be a :class:`list` of :class:`Embed` objects to send.

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message to send.
        username: :class:`str`
            The username to send with this message. If no username is provided
            then the default username for the webhook is used.
        avatar_url: :class:`str`
            The avatar URL to send with this message. If no avatar URL is provided
            then the default avatar for the webhook is used. If this is not a
            string then it is explicitly cast using ``str``.
        tts: :class:`bool`
            Whether the message should be sent using text-to-speech.
        ephemeral: :class:`bool`
            Whether the message should only be visible to the user.
            This is only available to :attr:`WebhookType.application` webhooks.
            If a view is sent with an ephemeral message and it has no timeout set
            then the timeout is set to 15 minutes.

            .. versionadded:: 2.0

        file: :class:`File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
        files: List[:class:`File`]
            A list of files to upload. Must be a maximum of 10.
            This cannot be mixed with the ``file`` parameter.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with the ``embeds`` parameter.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`Client.allowed_mentions <disnake.Client.allowed_mentions>`, if applicable.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`Client.allowed_mentions <disnake.Client.allowed_mentions>`.
            If no object is passed at all then the defaults given by :attr:`Client.allowed_mentions <disnake.Client.allowed_mentions>`
            are used instead.

            .. versionadded:: 1.4

        view: :class:`disnake.ui.View`
            The view to send with the message. You can only send a view
            if this webhook is not partial and has state attached. A
            webhook has state attached if the webhook is managed by the
            library. This cannot be mixed with ``components``.

            .. versionadded:: 2.0

        components: |components_type|
            A list of components to include in the message. This cannot be mixed with ``view``.

            .. versionadded:: 2.4

        thread: :class:`~disnake.abc.Snowflake`
            The thread to send this webhook to.

            .. versionadded:: 2.0

        thread_name: :class:`str`
            If in a forum channel, and ``thread`` is not specified,
            the name of the newly created thread.

            .. note::
                If this is set, the returned message's ``channel`` (assuming ``wait=True``),
                representing the created thread, may be a :class:`PartialMessageable`.

            .. versionadded:: 2.6

        wait: :class:`bool`
            Whether the server should wait before sending a response. This essentially
            means that the return type of this function changes from ``None`` to
            a :class:`WebhookMessage` if set to ``True``. If the type of webhook
            is :attr:`WebhookType.application` then this is always set to ``True``.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.

            .. versionadded:: 2.1

        suppress_embeds: :class:`bool`
            Whether to suppress embeds for the message. This hides
            all embeds from the UI if set to ``True``.

            .. versionadded:: 2.5

        Raises
        ------
        HTTPException
            Sending the message failed.
        NotFound
            This webhook was not found.
        Forbidden
            The authorization token for the webhook is incorrect.
        TypeError
            Raised by any of the following:
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``.
            ``ephemeral`` was passed with the improper webhook type.
            There was no state attached with this webhook when giving it a view.
            Both ``thread`` and ``thread_name`` were provided.
        WebhookTokenMissing
            There was no token associated with this webhook.
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        -------
        Optional[:class:`WebhookMessage`]
            If ``wait`` is ``True`` then the message that was sent, otherwise ``None``.
        """
        if self.token is None:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        previous_mentions: Optional[AllowedMentions] = getattr(
            self._state, "allowed_mentions", None
        )
        if content is None:
            content = MISSING

        application_webhook = self.type is WebhookType.application
        if ephemeral and not application_webhook:
            raise TypeError("ephemeral messages can only be sent from application webhooks")

        if delete_after is not MISSING and ephemeral:
            raise TypeError("ephemeral messages can not be deleted via endpoints")

        if application_webhook or delete_after is not MISSING:
            wait = True

        if view is not MISSING:
            if isinstance(self._state, _WebhookState):
                raise TypeError("Webhook views require an associated state with the webhook")
            if ephemeral is True and view.timeout is None:
                view.timeout = 15 * 60.0

        thread_id: Optional[int] = None
        if thread is not MISSING and thread_name is not None:
            raise TypeError("only one of thread and thread_name can be provided.")
        elif thread is not MISSING:
            thread_id = thread.id

        params = handle_message_parameters(
            content=content,
            username=username,
            avatar_url=avatar_url,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            ephemeral=ephemeral,
            suppress_embeds=suppress_embeds,
            view=view,
            components=components,
            thread_name=thread_name,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_mentions,
        )

        adapter = async_context.get()

        try:
            data = await adapter.execute_webhook(
                self.id,
                self.token,
                session=self.session,
                payload=params.payload,
                multipart=params.multipart,
                files=params.files,
                thread_id=thread_id,
                wait=wait,
            )
        finally:
            if params.files:
                for f in params.files:
                    f.close()

        msg = None
        if wait:
            msg = self._create_message(data)
            if delete_after is not MISSING:
                await msg.delete(delay=delete_after)

        if view is not MISSING and not view.is_finished():
            message_id = None if msg is None else msg.id
            self._state.store_view(view, message_id)

        return msg

    async def fetch_message(self, id: int) -> WebhookMessage:
        """|coro|

        Retrieves a single :class:`WebhookMessage` owned by this webhook.

        .. versionadded:: 2.0

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        id: :class:`int`
            The message ID to look for.

        Raises
        ------
        NotFound
            The specified message was not found.
        Forbidden
            You do not have the permissions required to get a message.
        HTTPException
            Retrieving the message failed.
        WebhookTokenMissing
            There was no token associated with this webhook.

        Returns
        -------
        :class:`WebhookMessage`
            The message asked for.
        """
        if self.token is None:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        adapter = async_context.get()
        data = await adapter.get_webhook_message(
            self.id,
            self.token,
            id,
            session=self.session,
        )
        return self._create_message(data)

    async def edit_message(
        self,
        message_id: int,
        *,
        content: Optional[str] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: Optional[List[Attachment]] = MISSING,
        view: Optional[View] = MISSING,
        components: Optional[Components[MessageUIComponent]] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> WebhookMessage:
        """|coro|

        Edits a message owned by this webhook.

        This is a lower level interface to :meth:`WebhookMessage.edit` in case
        you only have an ID.

        .. note::
            If the original message has embeds with images that were created from local files
            (using the ``file`` parameter with :meth:`Embed.set_image` or :meth:`Embed.set_thumbnail`),
            those images will be removed if the message's attachments are edited in any way
            (i.e. by setting ``file``/``files``/``attachments``, or adding an embed with local files).

        .. versionadded:: 1.6

        .. versionchanged:: 2.0
            The edit is no longer in-place, instead the newly edited message is returned.

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        message_id: :class:`int`
            The ID of the message to edit.
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

            .. versionadded:: 2.0

        files: List[:class:`File`]
            A list of files to upload. This cannot be mixed with the ``file`` parameter.
            Files will be appended to the message, see the ``attachments`` parameter
            to remove/replace existing files.

            .. versionadded:: 2.0

        attachments: Optional[List[:class:`Attachment`]]
            A list of attachments to keep in the message.
            If ``[]`` or ``None`` is passed then all existing attachments are removed.
            Keeps existing attachments if not provided.

            .. versionadded:: 2.2

            .. versionchanged:: 2.5
                Supports passing ``None`` to clear attachments.

        view: Optional[:class:`~disnake.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed. The webhook must have state attached, similar to
            :meth:`send`. This cannot be mixed with ``components``.

            .. versionadded:: 2.0

        components: |components_type|
            A list of components to update this message with. This cannot be mixed with ``view``.

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
            or there is no associated state when sending a view.
        WebhookTokenMissing
            There was no token associated with this webhook.
        ValueError
            The length of ``embeds`` was invalid

        Returns
        -------
        :class:`WebhookMessage`
            The newly edited webhook message.
        """
        if self.token is None:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        if view is not MISSING:
            if isinstance(self._state, _WebhookState):
                raise TypeError("This webhook does not have state associated with it")

            self._state.prevent_view_updates_for(message_id)

        # if no attachment list was provided but we're uploading new files,
        # use current attachments as the base
        if attachments is MISSING and (file or files):
            attachments = (await self.fetch_message(message_id)).attachments

        previous_mentions: Optional[AllowedMentions] = getattr(
            self._state, "allowed_mentions", None
        )
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
            data = await adapter.edit_webhook_message(
                self.id,
                self.token,
                message_id,
                session=self.session,
                payload=params.payload,
                multipart=params.multipart,
                files=params.files,
            )
        finally:
            if params.files:
                for f in params.files:
                    f.close()

        message = self._create_message(data)
        if view and not view.is_finished():
            self._state.store_view(view, message_id)
        return message

    async def delete_message(self, message_id: int, /) -> None:
        """|coro|

        Deletes a message owned by this webhook.

        This is a lower level interface to :meth:`WebhookMessage.delete` in case
        you only have an ID.

        .. versionadded:: 1.6

        .. versionchanged:: 2.6
            Raises :exc:`WebhookTokenMissing` instead of ``InvalidArgument``.

        Parameters
        ----------
        message_id: :class:`int`
            The ID of the message to delete.

        Raises
        ------
        HTTPException
            Deleting the message failed.
        Forbidden
            Deleted a message that is not yours.
        WebhookTokenMissing
            There was no token associated with this webhook
        """
        if self.token is None:
            raise WebhookTokenMissing("This webhook does not have a token associated with it")

        adapter = async_context.get()
        await adapter.delete_webhook_message(
            self.id,
            self.token,
            message_id,
            session=self.session,
        )
