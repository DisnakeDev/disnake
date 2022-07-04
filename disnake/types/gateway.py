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

from typing import Any, List, Literal, Optional, Sequence, Tuple, TypedDict, Union

from .activity import SendableActivity
from .snowflake import Snowflake, SnowflakeList
from .voice import SupportedModes


class SessionStartLimit(TypedDict):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class Gateway(TypedDict):
    url: str


class GatewayBot(Gateway):
    shards: int
    session_start_limit: SessionStartLimit


# websocket payloads (receive)


class GatewayPayload(TypedDict):
    op: Literal[0, 1, 7, 9, 10, 11]
    d: Any  # event data
    s: Optional[int]  # sequence number
    t: Optional[str]  # event name


# websocket payloads (send)

# opcode 1


class HeartbeatCommand(TypedDict):
    op: Literal[1, 3]  # normal ws and voice ws have different heartbeat opcodes
    d: Optional[int]


# opcode 2


class IdentifyProperties(TypedDict):
    os: str
    browser: str
    device: str


class _IdentifyDataOptional(TypedDict, total=False):
    compress: bool
    large_threshold: int
    shard: Tuple[int, int]
    presence: PresenceUpdateData


class IdentifyData(_IdentifyDataOptional):
    token: str
    properties: IdentifyProperties
    intents: int


class IdentifyCommand(TypedDict):
    op: Literal[2]
    d: IdentifyData


# opcode 3


class PresenceUpdateData(TypedDict):
    since: Optional[int]
    activities: Sequence[SendableActivity]
    status: str
    afk: bool


class PresenceUpdateCommand(TypedDict):
    op: Literal[3]
    d: PresenceUpdateData


# opcode 4


class VoiceStateData(TypedDict):
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
    self_mute: bool
    self_deaf: bool


class VoiceStateCommand(TypedDict):
    op: Literal[4]
    d: VoiceStateData


# opcode 6


class ResumeData(TypedDict):
    token: str
    session_id: str
    seq: int


class ResumeCommand(TypedDict):
    op: Literal[6]
    d: ResumeData


# opcode 8


class _RequestMembersDataOptional(TypedDict, total=False):
    query: str
    presences: bool
    user_ids: Union[Snowflake, SnowflakeList]
    nonce: str


class RequestMembersData(_RequestMembersDataOptional):
    guild_id: Snowflake
    limit: int


class RequestMembersCommand(TypedDict):
    op: Literal[8]
    d: RequestMembersData


# voice payloads (receive)


class VoicePayload(TypedDict):
    op: Literal[2, 4, 6, 8, 9]
    d: Any


class VoiceReadyPayload(TypedDict):
    ssrc: int
    ip: str
    port: int
    modes: List[str]


class VoiceSessionDescriptionPayload(TypedDict):
    mode: SupportedModes
    secret_key: List[int]


# voice payloads (send)

# voice opcode 0


class VoiceIdentifyData(TypedDict):
    server_id: str
    user_id: str
    session_id: str
    token: str


class VoiceIdentifyCommand(TypedDict):
    op: Literal[0]
    d: VoiceIdentifyData


# voice opcode 1


class _VoiceSelectProtocolInnerData(TypedDict):
    address: str
    port: int
    mode: SupportedModes


class VoiceSelectProtocolData(TypedDict):
    protocol: Literal["udp"]
    data: _VoiceSelectProtocolInnerData


class VoiceSelectProtocolCommand(TypedDict):
    op: Literal[1]
    d: VoiceSelectProtocolData


# voice opcode 5


class VoiceSpeakingData(TypedDict):
    speaking: int  # bitfield of 3 bits
    delay: int
    ssrc: int


class VoiceSpeakingCommand(TypedDict):
    op: Literal[5]
    d: VoiceSpeakingData


# voice opcode 7


class VoiceResumeData(TypedDict):
    server_id: str
    session_id: str
    token: str


class VoiceResumeCommand(TypedDict):
    op: Literal[7]
    d: VoiceResumeData
