# SPDX-License-Identifier: MIT

from typing import Literal, TypedDict

from typing_extensions import NotRequired, Required


class EmbedFooter(TypedDict):
    text: str
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedField(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class EmbedMedia(TypedDict, total=False):
    url: Required[str]
    proxy_url: str
    height: int
    width: int
    content_type: str
    placeholder: str
    placeholder_version: int
    description: str
    flags: int


EmbedThumbnail = EmbedImage = EmbedVideo = EmbedMedia


class EmbedProvider(TypedDict, total=False):
    name: str
    url: str


class EmbedAuthor(TypedDict):
    name: str
    url: NotRequired[str]
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


EmbedType = Literal["rich", "image", "video", "gifv", "article", "link", "poll_result"]


class Embed(TypedDict, total=False):
    title: str
    type: EmbedType
    description: str
    url: str
    timestamp: str
    color: int
    footer: EmbedFooter
    image: EmbedMedia
    thumbnail: EmbedMedia
    video: EmbedMedia
    provider: EmbedProvider
    author: EmbedAuthor
    fields: list[EmbedField]
    flags: int
