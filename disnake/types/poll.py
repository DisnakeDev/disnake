# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from .emoji import PartialEmoji
from .snowflake import Snowflake
from .user import User


class PollMedia(TypedDict):
    text: NotRequired[str]
    emoji: NotRequired[PartialEmoji]


class PollAnswer(TypedDict):
    # sent only as part of responses from Discord's API/Gateway
    answer_id: Snowflake
    poll_media: PollMedia


PollLayoutType = Literal[1]


class PollAnswerCount(TypedDict):
    id: Snowflake
    count: int
    me_voted: bool


class PollResult(TypedDict):
    is_finalized: bool
    answer_counts: List[PollAnswerCount]


class PollVoters(TypedDict):
    users: List[User]


class Poll(TypedDict):
    question: PollMedia
    answers: List[PollAnswer]
    expiry: Optional[str]
    allow_multiselect: bool
    layout_type: PollLayoutType
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
