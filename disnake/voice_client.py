# SPDX-License-Identifier: MIT

"""Some documentation to refer to:

- Our main web socket (mWS) sends opcode 4 with a guild ID and channel ID.
- The mWS receives VOICE_STATE_UPDATE and VOICE_SERVER_UPDATE.
- We pull the session_id from VOICE_STATE_UPDATE.
- We pull the token, endpoint and server_id from VOICE_SERVER_UPDATE.
- Then we initiate the voice web socket (vWS) pointing to the endpoint.
- We send opcode 0 with the user_id, server_id, session_id and token using the vWS.
- The vWS sends back opcode 2 with an ssrc, port, modes(array) and hearbeat_interval.
- We send a UDP discovery packet to endpoint:port and receive our IP and our port in LE.
- Then we send our IP and port via vWS with opcode 1.
- When that's all done, we receive opcode 4 from the vWS.
- Finally we can transmit data to endpoint:port.
"""

from __future__ import annotations

import asyncio
import logging
import socket
import struct
import threading
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final, Literal

from . import opus, utils
from .backoff import ExponentialBackoff
from .errors import ClientException, ConnectionClosed
from .gateway import DiscordVoiceWebSocket
from .player import AudioPlayer, AudioSource
from .utils import MISSING

if TYPE_CHECKING:
    from . import abc
    from .client import Client
    from .guild import Guild
    from .opus import Encoder
    from .state import ConnectionState
    from .types.gateway import VoiceServerUpdateEvent
    from .types.voice import GuildVoiceState as GuildVoiceStatePayload, SupportedModes
    from .user import ClientUser


has_nacl: bool
has_dave: bool

try:
    import nacl.secret

    has_nacl = True
except ImportError:
    has_nacl = False

if TYPE_CHECKING:
    import dave
else:
    try:
        import dave

        has_dave = True
    except ImportError:
        has_dave = False


__all__ = (
    "VoiceProtocol",
    "VoiceClient",
)


_log = logging.getLogger(__name__)


class VoiceProtocol:
    """A class that represents the Discord voice protocol.

    This is an abstract class. The library provides a concrete implementation
    under :class:`VoiceClient`.

    This class allows you to implement a protocol to allow for an external
    method of sending voice, such as Lavalink_ or a native library implementation.

    These classes are passed to :meth:`abc.Connectable.connect <VoiceChannel.connect>`.

    .. _Lavalink: https://github.com/freyacodes/Lavalink

    Parameters
    ----------
    client: :class:`Client`
        The client (or its subclasses) that started the connection request.
    channel: :class:`abc.Connectable`
        The voice channel that is being connected to.
    """

    def __init__(self, client: Client, channel: abc.Connectable) -> None:
        self.client: Client = client
        self.channel: abc.Connectable = channel

    async def on_voice_state_update(self, data: GuildVoiceStatePayload) -> None:
        """|coro|

        An abstract method that is called when the client's voice state
        has changed. This corresponds to ``VOICE_STATE_UPDATE``.

        Parameters
        ----------
        data: :class:`dict`
            The raw :ddocs:`voice state payload <resources/voice#voice-state-object>`.
        """
        raise NotImplementedError

    async def on_voice_server_update(self, data: VoiceServerUpdateEvent) -> None:
        """|coro|

        An abstract method that is called when initially connecting to voice.
        This corresponds to ``VOICE_SERVER_UPDATE``.

        Parameters
        ----------
        data: :class:`dict`
            The raw :ddocs:`voice server update payload <events/gateway-events#voice-server-update>`.
        """
        raise NotImplementedError

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """|coro|

        An abstract method called when the client initiates the connection request.

        When a connection is requested initially, the library calls the constructor
        under ``__init__`` and then calls :meth:`connect`. If :meth:`connect` fails at
        some point then :meth:`disconnect` is called.

        Within this method, to start the voice connection flow it is recommended to
        use :meth:`Guild.change_voice_state` to start the flow. After which,
        :meth:`on_voice_server_update` and :meth:`on_voice_state_update` will be called.
        The order that these two are called is unspecified.

        Parameters
        ----------
        timeout: :class:`float`
            The timeout for the connection.
        reconnect: :class:`bool`
            Whether reconnection is expected.
        """
        raise NotImplementedError

    async def disconnect(self, *, force: bool) -> None:
        """|coro|

        An abstract method called when the client terminates the connection.

        See :meth:`cleanup`.

        Parameters
        ----------
        force: :class:`bool`
            Whether the disconnection was forced.
        """
        raise NotImplementedError

    def cleanup(self) -> None:
        """Cleans up the internal state.

        **This method *must* be called to ensure proper clean-up during a disconnect.**

        It is advisable to call this from within :meth:`disconnect` when you are
        completely done with the voice protocol instance.

        This method removes it from the internal state cache that keeps track of
        currently alive voice clients. Failure to clean-up will cause subsequent
        connections to report that it's still connected.
        """
        key_id, _ = self.channel._get_voice_client_key()
        self.client._connection._remove_voice_client(key_id)


class VoiceClient(VoiceProtocol):
    """Represents a Discord voice connection.

    You do not create these, you typically get them from
    e.g. :meth:`VoiceChannel.connect`.

    Warning
    -------
    In order to use PCM based AudioSources, you must have the opus library
    installed on your system and loaded through :func:`opus.load_opus`.
    Otherwise, your AudioSources must be opus encoded (e.g. using :class:`FFmpegOpusAudio`)
    or the library will not be able to transmit audio.

    Attributes
    ----------
    session_id: :class:`str`
        The voice connection session ID.
    token: :class:`str`
        The voice connection token.
    endpoint: :class:`str`
        The endpoint we are connecting to.
    channel: :class:`abc.Connectable`
        The voice channel connected to.
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop that the voice client is running on.
    """

    endpoint_ip: str
    voice_port: int
    secret_key: list[int]
    ssrc: int
    ip: str
    port: int

    def __init__(self, client: Client, channel: abc.Connectable) -> None:
        if not has_nacl:
            msg = "PyNaCl library needed in order to use voice"
            raise RuntimeError(msg)

        super().__init__(client, channel)
        state = client._connection
        self.token: str = MISSING
        self.socket: socket.socket = MISSING
        self.loop: asyncio.AbstractEventLoop = state.loop
        self._state: ConnectionState = state
        # this will be used in the AudioPlayer thread
        self._connected: threading.Event = threading.Event()

        self._handshaking: bool = False
        self._potentially_reconnecting: bool = False
        self._voice_state_complete: asyncio.Event = asyncio.Event()
        self._voice_server_complete: asyncio.Event = asyncio.Event()

        self.mode: str = MISSING
        self._connections: int = 0
        self.sequence: int = 0
        self.timestamp: int = 0
        self.timeout: float = 0
        self._runner: asyncio.Task = MISSING
        self._player: AudioPlayer | None = None
        self.encoder: Encoder = MISSING
        self._lite_nonce: int = 0
        self.ws: DiscordVoiceWebSocket = MISSING
        self.dave: DaveState | None = DaveState(self) if has_dave else None

    warn_nacl = not has_nacl
    supported_modes: tuple[SupportedModes, ...] = ("aead_xchacha20_poly1305_rtpsize",)

    @property
    def guild(self) -> Guild:
        """:class:`Guild`: The guild we're connected to."""
        return self.channel.guild

    @property
    def user(self) -> ClientUser:
        """:class:`ClientUser`: The user connected to voice (i.e. ourselves)."""
        return self._state.user

    def checked_add(self, attr: str, value: int, limit: int) -> None:
        val = getattr(self, attr)
        if val + value > limit:
            setattr(self, attr, 0)
        else:
            setattr(self, attr, val + value)

    # connection related

    async def on_voice_state_update(self, data: GuildVoiceStatePayload) -> None:
        self.session_id = data["session_id"]
        channel_id = data["channel_id"]

        if not self._handshaking or self._potentially_reconnecting:
            # If we're done handshaking then we just need to update ourselves
            # If we're potentially reconnecting due to a 4014, then we need to differentiate
            # a channel move and an actual force disconnect
            if channel_id is None:
                # We're being disconnected so cleanup
                await self.disconnect()
            elif self.guild is None:  # pyright: ignore[reportUnnecessaryComparison]
                self.channel = None  # pyright: ignore[reportAttributeAccessIssue]
            else:
                self.channel = self.guild.get_channel(int(channel_id))  # pyright: ignore[reportAttributeAccessIssue]
        else:
            self._voice_state_complete.set()

    async def on_voice_server_update(self, data: VoiceServerUpdateEvent) -> None:
        if self._voice_server_complete.is_set():
            _log.info("Ignoring extraneous voice server update.")
            return

        self.token = data["token"]
        self.server_id = int(data["guild_id"])
        endpoint = data.get("endpoint")

        if endpoint is None or not self.token:
            _log.warning(
                "Awaiting endpoint... This requires waiting. "
                "If timeout occurred considering raising the timeout and reconnecting."
            )
            return

        self.endpoint = endpoint.removeprefix("wss://")

        # This gets set later
        self.endpoint_ip = MISSING

        if self.socket:
            self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)

        if not self._handshaking:
            # If we're not handshaking then we need to terminate our previous connection in the websocket
            if self.ws:
                await self.ws.close(4000)
            return

        self._voice_server_complete.set()

    async def voice_connect(self) -> None:
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def voice_disconnect(self) -> None:
        _log.info(
            "The voice handshake is being terminated for Channel ID %s (Guild ID %s)",
            self.channel.id,
            self.guild.id,
        )
        await self.channel.guild.change_voice_state(channel=None)

    def prepare_handshake(self) -> None:
        self._voice_state_complete.clear()
        self._voice_server_complete.clear()
        self._handshaking = True
        _log.info("Starting voice handshake... (connection attempt %d)", self._connections + 1)
        self._connections += 1

    def finish_handshake(self) -> None:
        _log.info("Voice handshake complete. Endpoint found %s", self.endpoint)
        self._handshaking = False
        self._voice_server_complete.clear()
        self._voice_state_complete.clear()

    async def connect_websocket(self, *, resume: bool = False) -> None:
        seq = self.ws.sequence if resume and self.ws is not MISSING else None
        self.ws = ws = await DiscordVoiceWebSocket.from_client(self, sequence=seq, resume=resume)

        self._connected.clear()
        event = ws._resumed if resume else ws._ready
        while not event.is_set():
            await ws.poll_event()
        self._connected.set()

    async def connect(self, *, reconnect: bool, timeout: float) -> None:
        _log.info("Connecting to voice...")
        self.timeout = timeout

        for i in range(5):
            self.prepare_handshake()

            # This has to be created before we start the flow.
            futures = [
                self._voice_state_complete.wait(),
                self._voice_server_complete.wait(),
            ]

            # Start the connection flow
            await self.voice_connect()

            try:
                await utils.sane_wait_for(futures, timeout=timeout)
            except asyncio.TimeoutError:
                await self.disconnect(force=True)
                raise

            self.finish_handshake()

            try:
                await self.connect_websocket()
                break
            except (ConnectionClosed, asyncio.TimeoutError):
                if reconnect:
                    _log.exception("Failed to connect to voice... Retrying...")
                    await asyncio.sleep(1 + i * 2.0)
                    await self.voice_disconnect()
                    continue
                raise

        if self._runner is MISSING:
            self._runner = self.loop.create_task(self.poll_voice_ws(reconnect))

    async def potential_reconnect(self) -> bool:
        # Attempt to stop the player thread from playing early
        self._connected.clear()
        self.prepare_handshake()
        self._potentially_reconnecting = True
        try:
            # We only care about VOICE_SERVER_UPDATE since VOICE_STATE_UPDATE can come before we get disconnected
            await asyncio.wait_for(self._voice_server_complete.wait(), timeout=self.timeout)
        except asyncio.TimeoutError:
            self._potentially_reconnecting = False
            await self.disconnect(force=True)
            return False

        self.finish_handshake()
        self._potentially_reconnecting = False
        try:
            await self.connect_websocket()
        except (ConnectionClosed, asyncio.TimeoutError):
            return False
        else:
            return True

    @property
    def latency(self) -> float:
        """:class:`float`: Latency between a HEARTBEAT and a HEARTBEAT_ACK in seconds.

        This could be referred to as the Discord Voice WebSocket latency and is
        an analogue of user's voice latencies as seen in the Discord client.

        .. versionadded:: 1.4
        """
        ws = self.ws
        return float("inf") if not ws else ws.latency

    @property
    def average_latency(self) -> float:
        """:class:`float`: Average of most recent 20 HEARTBEAT latencies in seconds.

        .. versionadded:: 1.4
        """
        ws = self.ws
        return float("inf") if not ws else ws.average_latency

    async def poll_voice_ws(self, reconnect: bool) -> None:
        backoff = ExponentialBackoff()
        while True:
            try:
                await self.ws.poll_event()
            except (ConnectionClosed, asyncio.TimeoutError) as exc:
                # Ensure the keep alive handler is closed
                if self.ws._keep_alive:
                    self.ws._keep_alive.stop()
                    self.ws._keep_alive = None

                if isinstance(exc, ConnectionClosed):
                    # 1000 - normal closure (obviously)
                    # 4014 - voice channel has been deleted.
                    # 4015 - voice server has crashed
                    if exc.code == 1000:
                        _log.info("Disconnecting from voice normally, close code %d.", exc.code)
                        await self.disconnect()
                        break
                    if exc.code == 4014:
                        _log.info("Disconnected from voice by force... potentially reconnecting.")
                        successful = await self.potential_reconnect()
                        if not successful:
                            _log.info(
                                "Reconnect was unsuccessful, disconnecting from voice normally..."
                            )
                            await self.disconnect()
                            break
                        continue
                    # only attempt to resume if the session is valid/established
                    if exc.code == 4015 and self.ws._ready.is_set():
                        _log.info("Disconnected from voice, trying to resume session...")
                        self._connected.clear()
                        try:
                            await self.connect_websocket(resume=True)
                        except (ConnectionClosed, asyncio.TimeoutError) as e:
                            # .connect() re-raises errors, fall back to reconnecting (or disconnecting) below as usual
                            if isinstance(e, ConnectionClosed):
                                msg = f"Received {e!r} error"
                            else:
                                msg = "Timed out"

                            _log.error(
                                "%s trying to resume voice connection, %s normally...",
                                msg,
                                "reconnecting" if reconnect else "disconnecting",
                            )
                        else:
                            _log.info("Successfully resumed voice session")
                            continue

                if not reconnect:
                    await self.disconnect()
                    raise

                retry = backoff.delay()
                _log.exception("Disconnected from voice... Reconnecting in %.2fs.", retry)
                self._connected.clear()
                await asyncio.sleep(retry)
                await self.voice_disconnect()
                try:
                    await self.connect(reconnect=True, timeout=self.timeout)
                except asyncio.TimeoutError:
                    # at this point we've retried 5 times... let's continue the loop.
                    _log.warning("Could not connect to voice... Retrying...")
                    continue
            except Exception:
                _log.exception("Error occurred while polling voice websocket:")
                # at this point we can't do much else, just re-raise the exception into the aether
                raise

    async def disconnect(self, *, force: bool = False) -> None:
        """|coro|

        Disconnects this voice client from voice.
        """
        if not force and not self.is_connected():
            return

        self.stop()
        self._connected.clear()

        try:
            if self.ws:
                await self.ws.close()

            await self.voice_disconnect()
        finally:
            self.cleanup()
            if self.socket:
                self.socket.close()

    async def move_to(self, channel: abc.Snowflake) -> None:
        """|coro|

        Moves you to a different voice channel.

        Parameters
        ----------
        channel: :class:`abc.Snowflake`
            The channel to move to. Must be a voice channel.
        """
        await self.channel.guild.change_voice_state(channel=channel)

    def is_connected(self) -> bool:
        """Indicates if the voice client is connected to voice."""
        return self._connected.is_set()

    # audio related

    def _get_voice_packet(self, data: bytes) -> bytes:
        if self.dave is not None and self.dave.can_encrypt():
            frame = self.dave.encrypt(data)
            if frame is None:
                # There isn't really a way to recover from this, so just raise at this point
                msg = "Failed to encrypt voice packet for DAVE"
                raise RuntimeError(msg)
        else:
            # non-e2ee voice connections
            frame = data

        header = bytearray(12)

        # Formulate rtp header
        header[0] = 0x80  # version = 2
        header[1] = 0x78  # payload type = 120 (opus)
        struct.pack_into(">H", header, 2, self.sequence)
        struct.pack_into(">I", header, 4, self.timestamp)
        struct.pack_into(">I", header, 8, self.ssrc)

        encrypt_packet = getattr(self, f"_encrypt_{self.mode}")
        return encrypt_packet(header, frame)

    def _get_nonce(self, pad: int) -> tuple[bytes, bytes]:
        # returns (nonce, padded_nonce).
        # n.b. all currently implemented modes use the same nonce size (192 bits / 24 bytes)
        nonce = struct.pack(">I", self._lite_nonce)

        self._lite_nonce += 1
        if self._lite_nonce > 4294967295:
            self._lite_nonce = 0

        return (nonce, nonce.ljust(pad, b"\0"))

    def _encrypt_aead_xchacha20_poly1305_rtpsize(self, header: bytes, data) -> bytes:
        box = nacl.secret.Aead(bytes(self.secret_key))  # pyright: ignore[reportPossiblyUnboundVariable]
        nonce, padded_nonce = self._get_nonce(nacl.secret.Aead.NONCE_SIZE)  # pyright: ignore[reportPossiblyUnboundVariable]

        return (
            header
            + box.encrypt(bytes(data), aad=bytes(header), nonce=padded_nonce).ciphertext
            + nonce
        )

    def play(
        self, source: AudioSource, *, after: Callable[[Exception | None], Any] | None = None
    ) -> None:
        r"""Plays an :class:`AudioSource`.

        The finalizer, ``after`` is called after the source has been exhausted
        or an error occurred.

        If an error happens while the audio player is running, the exception is
        caught and the audio player is then stopped.  If no after callback is
        passed, any caught exception will be displayed as if it were raised.

        Parameters
        ----------
        source: :class:`AudioSource`
            The audio source we're reading from.
        after: :class:`~collections.abc.Callable`\[[:class:`Exception` | :data:`None`], :data:`~typing.Any`]
            The finalizer that is called after the stream is exhausted.
            This function must have a single parameter, ``error``, that
            denotes an optional exception that was raised during playing.

        Raises
        ------
        ClientException
            Already playing audio or not connected.
        TypeError
            Source is not a :class:`AudioSource` or after is not a callable.
        OpusNotLoaded
            Source is not opus encoded and opus is not loaded.
        """
        if not self.is_connected():
            msg = "Not connected to voice."
            raise ClientException(msg)

        if self.is_playing():
            msg = "Already playing audio."
            raise ClientException(msg)

        if not isinstance(source, AudioSource):
            msg = f"source must be an AudioSource not {source.__class__.__name__}"
            raise TypeError(msg)

        if not self.encoder and not source.is_opus():
            self.encoder = opus.Encoder()

        self._player = AudioPlayer(source, self, after=after)
        self._player.start()

    def is_playing(self) -> bool:
        """Indicates if we're currently playing audio."""
        return self._player is not None and self._player.is_playing()

    def is_paused(self) -> bool:
        """Indicates if we're playing audio, but if we're paused."""
        return self._player is not None and self._player.is_paused()

    def stop(self) -> None:
        """Stops playing audio."""
        if self._player:
            self._player.stop()
            self._player = None

    def pause(self) -> None:
        """Pauses the audio playing."""
        if self._player:
            self._player.pause()

    def resume(self) -> None:
        """Resumes the audio playing."""
        if self._player:
            self._player.resume()

    @property
    def source(self) -> AudioSource | None:
        """:class:`AudioSource` | :data:`None`: The audio source being played, if playing.

        This property can also be used to change the audio source currently being played.
        """
        return self._player.source if self._player else None

    @source.setter
    def source(self, value: AudioSource) -> None:
        if not isinstance(value, AudioSource):
            msg = f"expected AudioSource not {value.__class__.__name__}."
            raise TypeError(msg)

        if self._player is None:
            msg = "Not playing anything."
            raise ValueError(msg)

        self._player._set_source(value)

    def send_audio_packet(self, data: bytes, *, encode: bool = True) -> None:
        """Sends an audio packet composed of the data.

        You must be connected to play audio.

        Parameters
        ----------
        data: :class:`bytes`
            The :term:`py:bytes-like object` denoting PCM or Opus voice data.
        encode: :class:`bool`
            Indicates if ``data`` should be encoded into Opus.

        Raises
        ------
        ClientException
            You are not connected.
        opus.OpusError
            Encoding the data failed.
        """
        self.checked_add("sequence", 1, 65535)
        if encode:
            encoded_data = self.encoder.encode(data, self.encoder.SAMPLES_PER_FRAME)
        else:
            encoded_data = data
        packet = self._get_voice_packet(encoded_data)
        try:
            self.socket.sendto(packet, (self.endpoint_ip, self.voice_port))
        except BlockingIOError:
            _log.warning(
                "A packet has been dropped (seq: %s, timestamp: %s)", self.sequence, self.timestamp
            )

        self.checked_add("timestamp", opus.Encoder.SAMPLES_PER_FRAME, 4294967295)

    @property
    def dave_max_version(self) -> int:
        if not has_dave:
            return 0

        return min(
            DaveState.MAX_SUPPORTED_VERSION,
            dave.get_max_supported_protocol_version(),
        )


class DaveState:
    # this implementation currently only supports DAVE v1, even if the native component may be newer
    MAX_SUPPORTED_VERSION: Final[int] = 1

    DISABLED_VERSION: Final[Literal[0]] = 0
    INIT_TRANSITION_ID: Final[Literal[0]] = 0
    NEW_MLS_GROUP_EPOCH: Final[Literal[1]] = 1

    # NOTE: all instantiations of this should be gated by `has_dave`,
    # everything in this class assumes the dependency is installed.
    def __init__(self, vc: VoiceClient) -> None:
        self.vc: VoiceClient = vc
        self._session: dave.Session = dave.Session(
            lambda source, reason: _log.error("MLS failure: %s - %s", source, reason)
        )
        self._encryptor: dave.Encryptor | None = None

        # we should always recognize ourselves (...cue existential crisis?)
        self._recognized_users: set[int] = {self._self_id}
        """Set of user IDs expected to be in media session"""

        self._prepared_transitions: dict[int, int] = {}
        """{transition_id: protocol_version}"""

        self._transient_keys: dict[int, dave.SignatureKeyPair] = {}
        """{protocol_version: keypair}"""

    @property
    def _self_id(self) -> int:
        return self.vc.user.id

    def _setup_ratchet_for_user(self, user_id: int, version: int) -> None:
        if user_id != self._self_id:
            return  # decryption is not implemented, ignore

        if self._session.has_established_group():
            ratchet = self._session.get_key_ratchet(str(user_id))
        else:
            ratchet = None

        _log.debug("updating encryption ratchet to %r", ratchet)
        if self._encryptor is None:
            # should never happen
            _log.error("attempted to set new ratchet without encryptor")
            return
        self._encryptor.set_key_ratchet(ratchet)

    def _get_transient_key(self, version: int) -> dave.SignatureKeyPair:
        if (key := self._transient_keys.get(version)) is None:
            self._transient_keys[version] = key = dave.SignatureKeyPair.generate(version)
        return key

    async def reinit_state(self, version: int) -> None:
        max_version = self.vc.dave_max_version
        if version > max_version:
            msg = f"DAVE version {version} requested, maximum supported version is {max_version}"
            raise RuntimeError(msg)

        _log.debug("re-initializing with DAVE version %d", version)

        if version > self.DISABLED_VERSION:
            await self.prepare_epoch(self.NEW_MLS_GROUP_EPOCH, version)
            self._encryptor = dave.Encryptor()
            self._encryptor.assign_ssrc_to_codec(self.vc.ssrc, dave.Codec.opus)
            _log.debug("created new encryptor")
        else:
            # `INIT_TRANSITION_ID` is executed immediately, no need to `.execute_transition()` here
            await self.prepare_transition(self.INIT_TRANSITION_ID, self.DISABLED_VERSION)

    def add_recognized_user(self, user_id: int) -> None:
        self._recognized_users.add(user_id)

    def remove_recognized_user(self, user_id: int) -> None:
        if user_id == self._self_id:
            return  # in case the gateway ever messes up, ignore CLIENT_DISCONNECT for our own user
        self._recognized_users.discard(user_id)

    # TODO: should be publicly accessible/documented on VoiceClient
    @property
    def voice_privacy_code(self) -> str | None:
        if not self._session.has_established_group():
            return None

        authenticator = self._session.get_last_epoch_authenticator()
        return dave.generate_displayable_code(authenticator, 30, 5)

    # TODO: see voice_privacy_code
    async def get_user_verification_code(self, user_id: int) -> str | None:
        if not self._session.has_established_group():
            return None

        # version is currently always 0
        d = await self._session.get_pairwise_fingerprint(0, str(user_id))
        return dave.generate_displayable_code(d, 45, 5)

    def can_encrypt(self) -> bool:
        return self._encryptor is not None and self._encryptor.has_key_ratchet()

    def encrypt(self, data: bytes) -> bytes | None:
        if not self._encryptor:
            msg = "Cannot encrypt audio frame, encryptor is not initialized"
            raise RuntimeError(msg)
        return self._encryptor.encrypt(dave.MediaType.audio, self.vc.ssrc, data)

    def handle_mls_external_sender(self, data: bytes) -> None:
        _log.debug("received MLS external sender")
        self._session.set_external_sender(data)

    async def handle_mls_proposals(self, data: bytes) -> None:
        commit_welcome = self._session.process_proposals(
            data,
            {str(u) for u in self._recognized_users},
        )
        if commit_welcome is not None:
            _log.debug("sending commit + welcome message")
            await self.vc.ws.send_dave_mls_commit_welcome(commit_welcome)

    async def handle_mls_announce_commit_transition(self, transition_id: int, data: bytes) -> None:
        _log.debug("group participants are changing with transition ID %d", transition_id)
        maybe_roster = self._session.process_commit(data)

        if maybe_roster is dave.RejectType.ignored:
            _log.debug("ignored commit for unexpected group ID")
            return
        elif maybe_roster is dave.RejectType.failed:
            # "If the client receives a welcome or commit they cannot process, they send the dave_mls_invalid_commit_welcome opcode (31) to the voice gateway to flag the invalid message."
            # "The client receiving the invalid commit or welcome locally resets their MLS state and generates a new key package to be delivered to the voice gateway via dave_mls_key_package opcode (26)."
            _log.error("failed to process commit")
            await self.vc.ws.send_dave_mls_invalid_commit_welcome(transition_id)
            await self.reinit_state(self._session.get_protocol_version())
        else:
            # joined group
            _log.debug("processed commit, roster: %r", list(maybe_roster.keys()))
            await self.prepare_transition(transition_id, self._session.get_protocol_version())

    # very similar to mls_announce_commit_transition, just slightly different error handling
    async def handle_mls_welcome(self, transition_id: int, data: bytes) -> None:
        _log.debug("received welcome, transition ID %d", transition_id)
        roster = self._session.process_welcome(
            data,
            {str(u) for u in self._recognized_users},
        )

        if roster is None:
            _log.error("failed to process welcome")
            await self.vc.ws.send_dave_mls_invalid_commit_welcome(transition_id)
            await self.reinit_state(self._session.get_protocol_version())
        else:
            # joined group
            _log.debug("processed welcome, roster: %r", list(roster.keys()))
            await self.prepare_transition(transition_id, self._session.get_protocol_version())

    async def prepare_epoch(self, epoch: int, version: int) -> None:
        _log.debug("preparing epoch %d, version %d", epoch, version)

        # "When the epoch ID is equal to 1, this message indicates that a new MLS group is to be created for the given protocol version."
        if epoch == self.NEW_MLS_GROUP_EPOCH:
            _log.info(
                "re-initializing MLS session with version %d, group ID %d",
                version,
                self.vc.channel.id,
            )
            self._session.init(
                version,
                self.vc.channel.id,
                str(self._self_id),
                self._get_transient_key(version),
            )

            # "The client must send a new key package after any of the following events:
            #  - The voice gateway sends a select_protocol_ack opcode (4) that includes a non-zero protocol version [in which case we call `prepare_epoch(1)`]
            #  - The voice gateway announces that a group is being created or re-created via the dave_protocol_prepare_epoch opcode (24) with epoch_id = 1"
            key_package = self._session.get_marshalled_key_package()
            await self.vc.ws.send_dave_mls_key_package(key_package)

            _log.debug("finished re-initializing MLS session")

    async def prepare_transition(self, transition_id: int, version: int) -> None:
        # since we don't currently implement decryption, no need to reset ratchets for other members here
        _log.debug("preparing transition ID %d to version %d", transition_id, version)

        self._prepared_transitions[transition_id] = version
        if transition_id == self.INIT_TRANSITION_ID:
            # "Upon receiving dave_protocol_prepare_transition opcode (21) with transition_id = 0, the client immediately executes the transition."
            self.execute_transition(transition_id)
        else:
            _log.debug("sending ready for transition ID %d", transition_id)
            await self.vc.ws.send_dave_transition_ready(transition_id)

    def execute_transition(self, transition_id: int) -> None:
        if (version := self._prepared_transitions.pop(transition_id, None)) is None:
            _log.error(
                "transition ID %d was requested to be executed, but was not prepared?",
                transition_id,
            )
            return
        _log.debug("executing transition ID %d to version %d", transition_id, version)

        # https://daveprotocol.com/#downgrade-to-transport-only-encryption
        if version == self.DISABLED_VERSION:
            self._session.reset()

        self._setup_ratchet_for_user(self._self_id, version)
