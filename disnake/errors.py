# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse, ClientWebSocketResponse
    from requests import Response

    from .client import SessionStartLimit
    from .interactions import Interaction, ModalInteraction

    _ResponseType = Union[ClientResponse, Response]

__all__ = (
    "DiscordException",
    "ClientException",
    "NoMoreItems",
    "GatewayNotFound",
    "HTTPException",
    "Forbidden",
    "NotFound",
    "DiscordServerError",
    "InvalidData",
    "WebhookTokenMissing",
    "LoginFailure",
    "SessionStartLimitReached",
    "ConnectionClosed",
    "PrivilegedIntentsRequired",
    "InteractionException",
    "InteractionTimedOut",
    "InteractionResponded",
    "InteractionNotResponded",
    "ModalChainNotSupported",
    "InteractionNotEditable",
    "LocalizationKeyError",
)


class DiscordException(Exception):
    """Base exception class for disnake.

    Ideally speaking, this could be caught to handle any exceptions raised from this library.
    """

    pass


class ClientException(DiscordException):
    """Exception that's raised when an operation in the :class:`Client` fails.

    These are usually for exceptions that happened due to user input.
    """

    pass


class NoMoreItems(DiscordException):
    """Exception that is raised when an async iteration operation has no more items."""

    pass


class GatewayNotFound(DiscordException):
    """An exception that is raised when the gateway for Discord could not be found"""

    def __init__(self) -> None:
        message = "The gateway to connect to Discord was not found."
        super().__init__(message)


def _flatten_error_dict(d: Dict[str, Any], key: str = "") -> Dict[str, str]:
    items: List[Tuple[str, str]] = []
    for k, v in d.items():
        new_key = f"{key}.{k}" if key else k

        if isinstance(v, dict):
            try:
                _errors: List[Dict[str, Any]] = v["_errors"]
            except KeyError:
                items.extend(_flatten_error_dict(v, new_key).items())
            else:
                items.append((new_key, " ".join(x.get("message", "") for x in _errors)))
        else:
            items.append((new_key, v))

    return dict(items)


class HTTPException(DiscordException):
    """Exception that's raised when an HTTP request operation fails.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`. In some cases
        this could also be a :class:`requests.Response`.

    text: :class:`str`
        The text of the error. Could be an empty string.
    status: :class:`int`
        The status code of the HTTP request.
    code: :class:`int`
        The Discord specific error code for the failure.
    """

    def __init__(
        self, response: _ResponseType, message: Optional[Union[str, Dict[str, Any]]]
    ) -> None:
        self.response: _ResponseType = response
        self.status: int = response.status  # type: ignore
        self.code: int
        self.text: str
        if isinstance(message, dict):
            self.code = message.get("code", 0)
            base = message.get("message", "")
            errors = message.get("errors")
            if errors:
                errors = _flatten_error_dict(errors)
                helpful = "\n".join(f"In {k}: {m}" for k, m in errors.items())
                self.text = base + "\n" + helpful
            else:
                self.text = base
        else:
            self.text = message or ""
            self.code = 0

        fmt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            fmt += ": {2}"

        super().__init__(fmt.format(self.response, self.code, self.text))


class Forbidden(HTTPException):
    """Exception that's raised for when status code 403 occurs.

    Subclass of :exc:`HTTPException`.
    """

    pass


class NotFound(HTTPException):
    """Exception that's raised for when status code 404 occurs.

    Subclass of :exc:`HTTPException`.
    """

    pass


class DiscordServerError(HTTPException):
    """Exception that's raised for when a 500 range status code occurs.

    Subclass of :exc:`HTTPException`.

    .. versionadded:: 1.5
    """

    pass


class InvalidData(ClientException):
    """Exception that's raised when the library encounters unknown
    or invalid data from Discord.
    """

    pass


class WebhookTokenMissing(DiscordException):
    """Exception that's raised when a :class:`Webhook` or :class:`SyncWebhook` is missing a token to make requests with.

    .. versionadded:: 2.6
    """

    pass


class LoginFailure(ClientException):
    """Exception that's raised when the :meth:`Client.login` function
    fails to log you in from improper credentials or some other misc.
    failure.
    """

    pass


class SessionStartLimitReached(ClientException):
    """Exception that's raised when :meth:`Client.connect` function
    fails to connect to Discord due to the session start limit being reached.

    .. versionadded:: 2.6

    Attributes
    ----------
    session_start_limit: :class:`.SessionStartLimit`
        The current state of the session start limit.

    """

    def __init__(self, session_start_limit: SessionStartLimit, requested: int = 1) -> None:
        self.session_start_limit: SessionStartLimit = session_start_limit
        super().__init__(
            f"Daily session start limit has been reached, resets at {self.session_start_limit.reset_time} "
            f"Requested {requested} shards, have only {session_start_limit.remaining} remaining."
        )


class ConnectionClosed(ClientException):
    """Exception that's raised when the gateway connection is
    closed for reasons that could not be handled internally.

    Attributes
    ----------
    code: :class:`int`
        The close code of the websocket.
    reason: :class:`str`
        The reason provided for the closure.
    shard_id: Optional[:class:`int`]
        The shard ID that got closed if applicable.
    """

    # https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-close-event-codes
    GATEWAY_CLOSE_EVENT_REASONS: Dict[int, str] = {
        4000: "Unknown error",
        4001: "Unknown opcode",
        4002: "Decode error",
        4003: "Not authenticated",
        4004: "Authentication failed",
        4005: "Already authenticated",
        4007: "Invalid sequence",
        4008: "Rate limited",
        4009: "Session timed out",
        4010: "Invalid Shard",
        4011: "Sharding required - you are required to shard your connection in order to connect.",
        4012: "Invalid API version",
        4013: "Invalid intents",
        4014: "Disallowed intents - you tried to specify an intent that you have not enabled or are not approved for.",
    }

    # https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes
    GATEWAY_VOICE_CLOSE_EVENT_REASONS: Dict[int, str] = {
        **GATEWAY_CLOSE_EVENT_REASONS,
        4002: "Failed to decode payload",
        4006: "Session no longer valid",
        4011: "Server not found",
        4012: "Unknown protocol",
        4014: "Disconnected, channel was deleted, you were kicked, voice server changed, or the main gateway session was dropped.",
        4015: "Voice server crashed",
        4016: "Unknown encryption mode",
    }

    def __init__(
        self,
        socket: ClientWebSocketResponse,
        *,
        shard_id: Optional[int],
        code: Optional[int] = None,
        voice: bool = False,
    ) -> None:
        # This exception is just the same exception except
        # reconfigured to subclass ClientException for users
        self.code: int = code or socket.close_code or -1
        # aiohttp doesn't seem to consistently provide close reason
        self.reason: str = self.GATEWAY_CLOSE_EVENT_REASONS.get(self.code, "Unknown reason")
        if voice:
            self.reason = self.GATEWAY_VOICE_CLOSE_EVENT_REASONS.get(self.code, "Unknown reason")

        self.shard_id: Optional[int] = shard_id
        super().__init__(
            f"Shard ID {self.shard_id} WebSocket closed with {self.code}: {self.reason}"
        )


class PrivilegedIntentsRequired(ClientException):
    """Exception that's raised when the gateway is requesting privileged intents
    but they're not ticked in the developer page yet.

    Go to https://discord.com/developers/applications/ and enable the intents
    that are required. Currently these are as follows:

    - :attr:`Intents.members`
    - :attr:`Intents.presences`
    - :attr:`Intents.message_content`

    Attributes
    ----------
    shard_id: Optional[:class:`int`]
        The shard ID that got closed if applicable.
    """

    def __init__(self, shard_id: Optional[int]) -> None:
        self.shard_id: Optional[int] = shard_id
        msg = (
            f"Shard ID {shard_id} is requesting privileged intents that have not been explicitly enabled in the "
            "developer portal. It is recommended to go to https://discord.com/developers/applications/ "
            "and explicitly enable the privileged intents within your application's page. If this is not "
            "possible, then consider disabling the privileged intents instead."
        )
        super().__init__(msg)


class InteractionException(ClientException):
    """Exception that's raised when an interaction operation fails

    .. versionadded:: 2.0

    Attributes
    ----------
    interaction: :class:`Interaction`
        The interaction that was responded to.
    """

    interaction: Interaction


class InteractionTimedOut(InteractionException):
    """Exception that's raised when an interaction takes more than 3 seconds
    to respond but is not deferred.

    .. versionadded:: 2.0

    Attributes
    ----------
    interaction: :class:`Interaction`
        The interaction that was responded to.
    """

    def __init__(self, interaction: Interaction) -> None:
        self.interaction: Interaction = interaction

        msg = (
            "Interaction took more than 3 seconds to be responded to. "
            'Please defer it using "interaction.response.defer" on the start of your command. '
            "Later you may send a response by editing the deferred message "
            'using "interaction.edit_original_response"'
            "\n"
            "Note: This might also be caused by a misconfiguration in the components "
            "make sure you do not respond twice in case this is a component."
        )
        super().__init__(msg)


class InteractionResponded(InteractionException):
    """Exception that's raised when sending another interaction response using
    :class:`InteractionResponse` when one has already been done before.

    An interaction can only be responded to once.

    .. versionadded:: 2.0

    Attributes
    ----------
    interaction: :class:`Interaction`
        The interaction that's already been responded to.
    """

    def __init__(self, interaction: Interaction) -> None:
        self.interaction: Interaction = interaction
        super().__init__("This interaction has already been responded to before")


class InteractionNotResponded(InteractionException):
    """Exception that's raised when editing an interaction response without
    sending a response message first.

    An interaction must be responded to exactly once.

    .. versionadded:: 2.0

    Attributes
    ----------
    interaction: :class:`Interaction`
        The interaction that hasn't been responded to.
    """

    def __init__(self, interaction: Interaction) -> None:
        self.interaction: Interaction = interaction
        super().__init__("This interaction hasn't been responded to yet")


class ModalChainNotSupported(InteractionException):
    """Exception that's raised when responding to a modal with another modal.

    .. versionadded:: 2.4

    Attributes
    ----------
    interaction: :class:`ModalInteraction`
        The interaction that was responded to.
    """

    def __init__(self, interaction: ModalInteraction) -> None:
        self.interaction: ModalInteraction = interaction
        super().__init__("You cannot respond to a modal with another modal.")


class InteractionNotEditable(InteractionException):
    """Exception that's raised when trying to use :func:`InteractionResponse.edit_message`
    on an interaction without an associated message (which is thus non-editable).

    .. versionadded:: 2.5

    Attributes
    ----------
    interaction: :class:`Interaction`
        The interaction that was responded to.
    """

    def __init__(self, interaction: Interaction) -> None:
        self.interaction: Interaction = interaction
        super().__init__("This interaction does not have a message to edit.")


class LocalizationKeyError(DiscordException):
    """Exception that's raised when a localization key lookup fails.

    .. versionadded:: 2.5

    Attributes
    ----------
    key: :class:`str`
        The localization key that couldn't be found.
    """

    def __init__(self, key: str) -> None:
        self.key: str = key
        super().__init__(f"No localizations were found for the key '{key}'.")
