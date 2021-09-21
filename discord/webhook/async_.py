"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz, 2021-present EQUENOS

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

from disnake.webhook.async_ import Any, Asset, AsyncDeferredLock, AsyncWebhookAdapter, BaseUser, BaseWebhook, ContextVar, Dict, DiscordServerError, ExecuteWebhookParameters, Forbidden, HTTPException, Hashable, InvalidArgument, List, Literal, MISSING, Message, NamedTuple, NotFound, Optional, PartialMessageable, PartialWebhookChannel, PartialWebhookGuild, Route, TYPE_CHECKING, Tuple, Union, User, Webhook, WebhookMessage, WebhookType, _FriendlyHttpAttributeErrorHelper, _WebhookState, _log, aiohttp, annotations, async_context, asyncio, handle_message_parameters, json, logging, overload, re, try_enum, urlquote, utils
__all__ = ('Webhook', 'WebhookMessage', 'PartialWebhookChannel', 'PartialWebhookGuild')