# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .emoji import PartialEmoji


class PollMedia(TypedDict):
    text: NotRequired[str]
    emoji: NotRequired[PartialEmoji]


class PollAnswer(TypedDict):
    # sent only as part of responses from Discord's API/Gateway
    answer_id: int
    poll_media: PollMedia


PollType = Literal[1]


class PollAnswerCount(TypedDict):
    id: int
    count: int
    me_voted: bool


class PollResult(TypedDict):
    is_finalized: bool
    answer_counts: List[PollAnswerCount]


class Poll(TypedDict):
    question: PollMedia
    answers: List[PollAnswer]
    expiry: Optional[str]
    allow_multiselect: bool
    layout_type: PollType
    # sent only as part of responses from Discord's API/Gateway
    results: NotRequired[PollResult]


class EmojiPayload(TypedDict):
    id: NotRequired[int]
    name: NotRequired[str]


class PollCreateMediaPayload(TypedDict):
    text: NotRequired[str]
    emoji: NotRequired[EmojiPayload]


class PollCreateAnswerPayload(TypedDict):
    poll_media: PollCreateMediaPayload


class PollCreatePayload(TypedDict):
    question: PollCreateMediaPayload
    answers: List[PollCreateAnswerPayload]
    duration: int
    allow_multiselect: bool
    layout_type: NotRequired[int]