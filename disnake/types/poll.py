# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
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
    answer_counts: list[PollAnswerCount]


class PollVoters(TypedDict):
    users: list[User]


class Poll(TypedDict):
    question: PollMedia
    answers: list[PollAnswer]
    expiry: str | None
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
    answers: list[PollCreateAnswerPayload]
    duration: int
    allow_multiselect: bool
    layout_type: NotRequired[int]
