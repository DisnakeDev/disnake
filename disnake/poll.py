# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .enums import PollType, try_enum
from .message import Message
from .partial_emoji import PartialEmoji

if TYPE_CHECKING:
    from .abc import MessageableChannel
    from .state import ConnectionState
    from .types.poll import (
        Poll as PollPayload,
        PollAnswer as PollAnswerPayload,
        PollAnswerCount as PollAnswerCountPayload,
        PollMedia as PollMediaPayload,
        PollResult as PollResultPayload,
    )


class PollAnswerCount:
    def __init__(self, data: PollAnswerCountPayload) -> None:
        self.id: int = int(data["id"])
        self.count: int = int(data["count"])
        self.me_voted: bool = data["me_voted"]


class PollResult:
    def __init__(self, data: PollResultPayload) -> None:
        self.is_finalized: bool = data["is_finalized"]
        self.answer_counts: List[PollAnswerCount] = [
            PollAnswerCount(answer) for answer in data["answer_counts"]
        ]


class PollMedia:
    def __init__(self, data: PollMediaPayload) -> None:
        self.text: Optional[str] = data.get("text")

        emoji = None
        if _emoji := data.get("emoji"):
            emoji = PartialEmoji.from_dict(_emoji)
        self.emoji: Optional[PartialEmoji] = emoji


class PollAnswer:
    def __init__(self, data: PollAnswerPayload) -> None:
        self.answer_id: Optional[int] = int(data.get("answer_id", 0)) or None
        self.poll_media = PollMedia(data["poll_media"])


class Poll:
    def __init__(
        self,
        channel: MessageableChannel,
        message: Message,
        state: ConnectionState,
        data: PollPayload,
    ) -> None:
        self._state: ConnectionState = state
        self.channel = channel
        self.message = message
        self.question: str = data["question"]
        self.answers: List[PollAnswer] = [PollAnswer(answer) for answer in data["answers"]]
        self.expiry = data["expiry"]
        self.allow_multiselect: bool = data["allow_multiselect"]
        self.layout_type: PollType = try_enum(PollType, data["layout_type"])
        self.results: PollResult = PollResult(data["results"])

    async def expire(self) -> Message:
        await self._state.http.expire_poll(self.channel.id, self.message.id)
