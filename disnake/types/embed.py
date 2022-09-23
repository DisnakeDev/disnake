# SPDX-License-Identifier: MIT

from typing import List, Literal, TypedDict


class _EmbedFooterOptional(TypedDict, total=False):
    icon_url: str
    proxy_icon_url: str


class EmbedFooter(_EmbedFooterOptional):
    text: str


class _EmbedFieldOptional(TypedDict, total=False):
    inline: bool


class EmbedField(_EmbedFieldOptional):
    name: str
    value: str


class EmbedThumbnail(TypedDict, total=False):
    url: str
    proxy_url: str
    height: int
    width: int


class EmbedVideo(TypedDict, total=False):
    url: str
    proxy_url: str
    height: int
    width: int


class EmbedImage(TypedDict, total=False):
    url: str
    proxy_url: str
    height: int
    width: int


class EmbedProvider(TypedDict, total=False):
    name: str
    url: str


class EmbedAuthor(TypedDict, total=False):
    name: str
    url: str
    icon_url: str
    proxy_icon_url: str


EmbedType = Literal["rich", "image", "video", "gifv", "article", "link"]


class Embed(TypedDict, total=False):
    title: str
    type: EmbedType
    description: str
    url: str
    timestamp: str
    color: int
    footer: EmbedFooter
    image: EmbedImage
    thumbnail: EmbedThumbnail
    video: EmbedVideo
    provider: EmbedProvider
    author: EmbedAuthor
    fields: List[EmbedField]
