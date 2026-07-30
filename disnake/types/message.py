# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .channel import ChannelType
from .components import MessageTopLevelComponent
from .embed import Embed
from .emoji import PartialEmoji
from .interactions import InteractionDataResolved, InteractionMessageReference, InteractionMetadata
from .member import Member, UserWithMember
from .poll import Poll
from .snowflake import Snowflake, SnowflakeList
from .sticker import StickerItem
from .threads import Thread, ThreadMember
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


class Attachment(TypedDict):
    id: Snowflake
    filename: str
    title: NotRequired[str]
    description: NotRequired[str]
    content_type: NotRequired[str]
    size: int
    url: str
    proxy_url: str
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    ephemeral: NotRequired[bool]
    duration_secs: NotRequired[float]
    waveform: NotRequired[str]
    flags: NotRequired[int]


MessageActivityType = Literal[1, 2, 3, 5]


class MessageActivity(TypedDict):
    type: MessageActivityType
    party_id: NotRequired[str]


class MessageApplication(TypedDict):
    id: Snowflake
    description: str
    icon: str | None
    name: str
    cover_image: NotRequired[str]


MessageReferenceType = Literal[0, 1]


class MessageReference(TypedDict):
    type: MessageReferenceType
    message_id: NotRequired[Snowflake]
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    fail_if_not_exists: NotRequired[bool]


class ForwardedMessage(TypedDict):
    type: MessageType
    content: str
    embeds: list[Embed]
    attachments: list[Attachment]
    timestamp: str
    edited_timestamp: str | None
    flags: NotRequired[int]
    mentions: list[User] | list[UserWithMember]
    # apparently mention_roles list is not sent if the msg
    # is not forwarded in the same guild
    mention_roles: NotRequired[SnowflakeList]
    sticker_items: NotRequired[list[StickerItem]]
    components: NotRequired[list[MessageTopLevelComponent]]


class MessageSnapshot(TypedDict):
    message: ForwardedMessage


class RoleSubscriptionData(TypedDict):
    role_subscription_listing_id: Snowflake
    tier_name: str
    total_months_subscribed: int
    is_renewal: bool


# fmt: off
MessageType = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 36, 37, 38, 39, 46]
# fmt: on


class Message(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    author: User
    content: str
    timestamp: str
    edited_timestamp: str | None
    tts: bool
    mention_everyone: bool
    # this only contains (partial) member data in gateway events
    mentions: list[User] | list[UserWithMember]
    mention_roles: SnowflakeList
    mention_channels: NotRequired[list[ChannelMention]]
    attachments: list[Attachment]
    embeds: list[Embed]
    reactions: NotRequired[list[Reaction]]
    nonce: NotRequired[int | str]
    pinned: bool
    webhook_id: NotRequired[Snowflake]
    type: MessageType
    activity: NotRequired[MessageActivity]
    application: NotRequired[MessageApplication]
    application_id: NotRequired[Snowflake]
    message_reference: NotRequired[MessageReference]
    message_snapshots: NotRequired[list[MessageSnapshot]]
    flags: NotRequired[int]
    referenced_message: NotRequired[Message | None]
    interaction: NotRequired[InteractionMessageReference]  # deprecated
    interaction_metadata: NotRequired[InteractionMetadata]
    thread: NotRequired[Thread]
    components: NotRequired[list[MessageTopLevelComponent]]
    sticker_items: NotRequired[list[StickerItem]]
    position: NotRequired[int]
    role_subscription_data: NotRequired[RoleSubscriptionData]
    poll: NotRequired[Poll]
    call: NotRequired[MessageCall]
    # contains resolved objects for `default_values` of select menus in this message; we currently don't have a use for this
    resolved: NotRequired[InteractionDataResolved]

    # specific to MESSAGE_CREATE/MESSAGE_UPDATE events
    guild_id: NotRequired[Snowflake]
    member: NotRequired[Member]


AllowedMentionType = Literal["roles", "users", "everyone"]


class AllowedMentions(TypedDict):
    parse: list[AllowedMentionType]
    roles: SnowflakeList
    users: SnowflakeList
    replied_user: bool


class MessagePin(TypedDict):
    pinned_at: str
    message: Message


class MessageCall(TypedDict):
    participants: SnowflakeList
    ended_timestamp: NotRequired[str | None]


class MessageSearchQuery(TypedDict, total=False):
    # pagination
    limit: int
    offset: int
    max_id: Snowflake
    min_id: Snowflake
    # query
    slop: int
    content: str
    channel_id: Sequence[Snowflake]
    author_type: Sequence[str]
    author_id: Sequence[Snowflake]
    mentions: Sequence[Snowflake]
    mentions_role: Sequence[Snowflake]
    mentions_everyone: bool
    replied_to_user_id: Sequence[Snowflake]
    replied_to_message_id: Sequence[Snowflake]
    pinned: bool
    has: Sequence[str]
    embed_type: Sequence[str]
    embed_provider: Sequence[str]
    link_hostname: Sequence[str]
    attachment_filename: Sequence[str]
    attachment_extension: Sequence[str]
    sort_by: str
    sort_order: str
    include_nsfw: bool


class MessageSearchResult(TypedDict):
    doing_deep_historical_index: bool
    documents_indexed: NotRequired[int]
    total_results: int
    messages: list[list[Message]]
    threads: NotRequired[list[Thread]]
    members: NotRequired[list[ThreadMember]]


class MessageSearchNotIndexedResult(TypedDict):
    message: str
    code: int
    documents_indexed: int
    retry_after: int
