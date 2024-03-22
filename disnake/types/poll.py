# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, TypedDict

from typing_extensions import NotRequired

from .emoji import PartialEmoji
from .snowflake import Snowflake


class PollMedia(TypedDict):
    text: NotRequired[str]
    emoji: NotRequired[PartialEmoji]


class PollAnswer(TypedDict):
    # sent only as part of responses from Discord's API/Gateway
    answer_id: Snowflake
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
    question: str
    answers: List[PollAnswer]
    expiry: str
    allow_multiselect: bool
    layout_type: PollType
    # sent only as part of responses from Discord's API/Gateway
    results: PollResult
