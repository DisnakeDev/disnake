# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict, Union

from .channel import ChannelType
from .components import Component
from .embed import Embed
from .emoji import PartialEmoji
from .interactions import InteractionMessageReference
from .member import Member, UserWithMember
from .snowflake import Snowflake, SnowflakeList
from .sticker import StickerItem
from .threads import Thread
from .user import User


class ChannelMention(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    type: ChannelType
    name: str


class Reaction(TypedDict):
    count: int
    me: bool
    emoji: PartialEmoji


class _AttachmentOptional(TypedDict, total=False):
    height: Optional[int]
    width: Optional[int]
    content_type: str
    ephemeral: bool
    description: str


class Attachment(_AttachmentOptional):
    id: Snowflake
    filename: str
    size: int
    url: str
    proxy_url: str


MessageActivityType = Literal[1, 2, 3, 5]


class MessageActivity(TypedDict):
    type: MessageActivityType
    party_id: str


class _MessageApplicationOptional(TypedDict, total=False):
    cover_image: str


class MessageApplication(_MessageApplicationOptional):
    id: Snowflake
    description: str
    icon: Optional[str]
    name: str


class MessageReference(TypedDict, total=False):
    message_id: Snowflake
    channel_id: Snowflake
    guild_id: Snowflake
    fail_if_not_exists: bool


class _MessageOptional(TypedDict, total=False):
    guild_id: Snowflake
    member: Member
    mention_channels: List[ChannelMention]
    reactions: List[Reaction]
    nonce: Union[int, str]
    webhook_id: Snowflake
    activity: MessageActivity
    application: MessageApplication
    application_id: Snowflake
    message_reference: MessageReference
    flags: int
    sticker_items: List[StickerItem]
    referenced_message: Optional[Message]
    position: int
    interaction: InteractionMessageReference
    components: List[Component]
    thread: Thread


MessageType = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 18, 19, 20, 21]


class Message(_MessageOptional):
    id: Snowflake
    channel_id: Snowflake
    author: User
    content: str
    timestamp: str
    edited_timestamp: Optional[str]
    tts: bool
    mention_everyone: bool
    mentions: List[UserWithMember]
    mention_roles: SnowflakeList
    attachments: List[Attachment]
    embeds: List[Embed]
    pinned: bool
    type: MessageType


AllowedMentionType = Literal["roles", "users", "everyone"]


class AllowedMentions(TypedDict):
    parse: List[AllowedMentionType]
    roles: SnowflakeList
    users: SnowflakeList
    replied_user: bool
