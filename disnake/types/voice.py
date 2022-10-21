# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .member import MemberWithUser
from .snowflake import Snowflake

SupportedModes = Literal["xsalsa20_poly1305_lite", "xsalsa20_poly1305_suffix", "xsalsa20_poly1305"]


class _VoiceState(TypedDict):
    user_id: Snowflake
    member: NotRequired[MemberWithUser]
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_stream: NotRequired[bool]
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: Optional[str]


class GuildVoiceState(_VoiceState):
    channel_id: Optional[Snowflake]


class VoiceState(_VoiceState, total=False):
    channel_id: Optional[Snowflake]
    guild_id: Snowflake


class VoiceRegion(TypedDict):
    id: str
    name: str
    optimal: bool
    deprecated: bool
    custom: bool


class VoiceIdentify(TypedDict):
    server_id: Snowflake
    user_id: Snowflake
    session_id: str
    token: str


class VoiceReady(TypedDict):
    ssrc: int
    ip: str
    port: int
    modes: List[SupportedModes]
    heartbeat_interval: int
