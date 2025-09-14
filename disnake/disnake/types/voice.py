# SPDX-License-Identifier: MIT

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .emoji import PartialEmoji
from .member import MemberWithUser
from .snowflake import Snowflake

SupportedModes = Literal[
    # "aead_aes256_gcm_rtpsize",  # supported in libsodium, but not exposed by pynacl
    "aead_xchacha20_poly1305_rtpsize",
]

VoiceChannelEffectAnimationType = Literal[0, 1]


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


class VoiceChannelEffect(TypedDict, total=False):
    emoji: Optional[PartialEmoji]
    animation_type: Optional[VoiceChannelEffectAnimationType]
    animation_id: int
    sound_id: Snowflake
    sound_volume: float
