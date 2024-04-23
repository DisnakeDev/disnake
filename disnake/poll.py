# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, List, Optional, Union

from . import message, utils
from .emoji import Emoji
from .enums import PollType, try_enum
from .partial_emoji import PartialEmoji
from .user import User

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import MessageableChannel
    from .state import ConnectionState
    from .types.poll import (
        Poll as PollPayload,
        PollAnswer as PollAnswerPayload,
        PollAnswerCount as PollAnswerCountPayload,
        PollCreateAnswerPayload,
        PollCreateMediaPayload,
        PollCreatePayload,
        PollMedia as PollMediaPayload,
        PollResult as PollResultPayload,
    )

__all__ = (
    "PollResult",
    "PollAnswerCount",
    "PollMedia",
    "PollAnswer",
    "Poll",
)


class PollAnswerCount:
    """Represents a poll answer count from discord.

    Attributes
    ----------
    id: :class:`int`
        The ID of the answer the counts are of.
    count: :class:`int`
        The number of votes for this answer.
    me_voted: :class:`bool`
        Whether the current user voted for this answer.
    """

    __slots__ = (
        "id",
        "count",
        "me_voted",
    )

    def __init__(self, data: PollAnswerCountPayload) -> None:
        self.id: int = int(data["id"])
        self.count: int = int(data["count"])
        self.me_voted: bool = data["me_voted"]

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id} count={self.count} me_voted={self.me_voted}>"
        )


class PollResult:
    """Represents a poll result from discord.

    Attributes
    ----------
    is_finalized: :class:`bool`
        Whether the votes have been precisely counted.
    answer_counts: List[:class:`PollAnswerCount`]
        The counts for each answer.
    """

    __slots__ = (
        "is_finalized",
        "answer_counts",
    )

    def __init__(self, data: PollResultPayload) -> None:
        self.is_finalized: bool = data["is_finalized"]
        self.answer_counts: List[PollAnswerCount] = [
            PollAnswerCount(answer) for answer in data["answer_counts"]
        ]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} is_finalized={self.is_finalized}>"


class PollMedia:
    """Represents data of a poll's question/answers.
    
    You must specify at least one of the parameters when creating an instance.

    Parameters
    ----------
    text: Optional[:class:`str`]
        The text of this media.
    emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`, :class:`str`]]
        The emoji of this media.

    Attributes
    ----------
    text: Optional[:class:`str`]
        The text of this media.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji of this media.
    """

    __slots__ = ("text", "emoji")

    def __init__(
        self, text: Optional[str] = None, *, emoji: Optional[Union[Emoji, PartialEmoji, str]] = None
    ) -> None:
        if text is None and emoji is None:
            raise ValueError("Either one of text or emoji must be not none.")

        self.text = text
        self.emoji = emoji

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} text={self.text} emoji={self.emoji!r}>"

    @classmethod
    def from_payload(cls, data: PollMediaPayload) -> PollMedia:
        text = data.get("text")

        emoji = None
        if _emoji := data.get("emoji"):
            emoji = PartialEmoji.from_dict(_emoji)

        return cls(text=text, emoji=emoji)

    def _to_dict(self) -> PollCreateMediaPayload:
        payload: PollCreateMediaPayload = {}
        if self.text:
            payload["text"] = self.text
        if self.emoji:
            if isinstance(self.emoji, (Emoji, PartialEmoji)):
                if self.emoji.id:
                    payload["emoji"] = {"id": self.emoji.id}
                else:
                    payload["emoji"] = {"name": self.emoji.name}
            elif isinstance(self.emoji, str):
                payload["emoji"] = {"name": self.emoji}
        return payload


class PollAnswer:
    """Represents a poll answer from discord.

    Parameters
    ----------
    text: Optional[:class:`str`]
        The text of the answer.
    emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`, :class:`str`]]
        The emoji of the answer.

        .. note::

            If this is str you are expected to pass the name of the emoji. This works only for discord default emojis. For custom emojis you need to use an Emoji or PartialEmoji object.

    Attributes
    ----------
    answer_id: :class:`int`
        The ID of the answer that this object represents.
    poll_media: :class:`PollMedia`
        The media fields linked to this answer.
    """

    __slots__ = ("_state", "_channel_id", "_message_id", "answer_id", "poll_media")

    def __init__(
        self, text: Optional[str] = None, *, emoji: Optional[Union[Emoji, PartialEmoji, str]] = None
    ) -> None:
        self._state: ConnectionState
        self._channel_id: int
        self._message_id: int
        self.answer_id: int

        self.poll_media = PollMedia(text, emoji=emoji)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} poll_media={self.poll_media!r}>"

    @classmethod
    def from_payload(
        cls, state: ConnectionState, channel_id: int, message_id: int, data: PollAnswerPayload
    ) -> PollAnswer:
        poll_media_payload = data["poll_media"]
        answer = cls(poll_media_payload.get("text"), emoji=poll_media_payload.get("text"))
        answer.answer_id = int(data["answer_id"])
        answer._state = state
        answer._channel_id = channel_id
        answer._message_id = message_id

        return answer

    def _to_dict(self) -> PollCreateAnswerPayload:
        return {"poll_media": self.poll_media._to_dict()}

    async def get_voters(self) -> List[User]:
        """|coro|

        Get a list of users that voted for this specific answer.

        .. note::

            This method works only on PollAnswer(s) objects that are fetched from the API and not on the ones built manually.

        Raises
        ------
        HTTPException
            Getting the voters for this answer failed.
        Forbidden
            Tried to get the voters for this answer without the required permissions.
        ValueError
            You tried to invoke this method on an incomplete object, most likely one that wasn't fetched from the API.

        Returns
        -------
        List[:class:`User`]
            The users that voted for this answer.
        """
        if not all(
            hasattr(self, member)
            for member in (
                "_state",
                "_channel_id",
                "_message_id",
                "answer_id",
            )
        ):
            raise ValueError(
                "This object was manually builded. To use this method you need to get a poll from the discord API!"
            )

        data = await self._state.http.get_poll_answer_voters(
            self._channel_id, self._message_id, self.answer_id
        )
        return [User(state=self._state, data=user) for user in data["users"]]


class Poll:
    """Represents a poll from Discord.

    Parameters
    ----------
    question: :class:`str`
        The question text of the poll.
    answers: List[:class:`PollAnswer`]
        The answers for this poll.
    duration: :class:`datetime.timedelta`
        The total duration of the poll. Defaults to 1 day.
    allow_multiselect: :class:`bool`
        Whether users will be able to pick more than one answer. Defaults to ``False``.
    layout_type: :class:`PollType`
        The layout type of the poll. Defaults to :attr:`PollType.default`.

    Attributes
    ----------
    channel: Union[:class:`TextChannel`, :class:`VoiceChannel`, :class:`StageChannel`, :class:`Thread`, :class:`DMChannel`, :class:`GroupChannel`, :class:`PartialMessageable`]
        The channel that the poll was sent from.

        .. note::

            This attribute is available only if you fetched the Poll object from the API.

    message: :class:`Message`
        The message which contain this poll.

        .. note::

            This attribute is available only if you fetched the Poll object from the API.

    question: :class:`str`
        The question text of the poll.
    answers: List[:class:`PollAnswer`]
        The available answers for this poll.
    expiry: :class:`datetime.datetime`
        The expiration date till users will be able to vote for this poll.

        .. note::

            This attribute is not None only if you fetched the Poll object from the API.

    allow_multiselect: :class:`bool`
        Whether users are able to pick more than one answer.
    layout_type: :class:`PollType`
        The type of the layout of the poll.
    results: Optional[:class:`PollResult`]
        The results of the poll.

        .. note::

            This attribute is not None only if you fetched the Poll object from the API.
    """

    __slots__ = (
        "_state",
        "channel",
        "message",
        "question",
        "answers",
        "duration",
        "expiry",
        "allow_multiselect",
        "layout_type",
        "results",
    )

    def __init__(
        self,
        question: str,
        *,
        answers: List[PollAnswer],
        duration: Optional[timedelta] = timedelta(hours=24),
        allow_multiselect: bool = False,
        layout_type: PollType = PollType.default,
    ) -> None:
        self._state: ConnectionState
        self.channel: MessageableChannel
        self.message: message.Message
        self.expiry: datetime

        self.question: str = question
        self.answers: List[PollAnswer] = answers
        self.results: Optional[PollResult] = None

        self.duration: Optional[timedelta] = duration
        if not duration:
            self.duration = timedelta(hours=0)

        self.allow_multiselect: bool = allow_multiselect
        self.layout_type: PollType = layout_type

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} question={self.question} answers={self.answers!r}>"

    @classmethod
    def from_payload(
        cls,
        channel: MessageableChannel,
        message: message.Message,
        state: ConnectionState,
        data: Optional[PollPayload] = None,
    ) -> Optional[Poll]:
        if data is None:
            return None

        poll = cls(
            question=data["question"],
            answers=[
                PollAnswer.from_payload(state, channel.id, message.id, answer)
                for answer in data["answers"]
            ],
            duration=None,
            allow_multiselect=data["allow_multiselect"],
            layout_type=try_enum(PollType, data["layout_type"]),
        )
        poll._state = state
        poll.channel = channel
        poll.message = message
        poll.expiry = utils.parse_time(data["expiry"])
        poll.results = None
        if results := data["results"]:
            poll.results = PollResult(results)

        return poll

    def _to_dict(self) -> PollCreatePayload:
        # pyright is not able to tell that we are adding a keyword later,
        # so we build answers first and then pass directly the list, building
        # the dict object in one go
        answers: List[PollCreateAnswerPayload] = []
        for answer in self.answers:
            answers.append(answer._to_dict())

        payload: PollCreatePayload = {
            "question": {"text": self.question},
            "duration": (int(self.duration.total_seconds()) // 3600),  # type: ignore
            "allow_multiselect": self.allow_multiselect,
            "layout_type": self.layout_type.value,
            "answers": answers,
        }
        return payload

    async def expire(self) -> message.Message:
        """|coro|

        Immediately ends a poll.

        .. note::

            This method works only on Poll(s) objects that are
            fetched from the API and not on the ones built manually.

        Raises
        ------
        HTTPException
            Expiring the poll failed.
        Forbidden
            Tried to expire a poll without the required permissions.
        ValueError
            You tried to invoke this method on an incomplete object, most likely one that wasn't fetched from the API.

        Returns
        -------
        :class:`Message`
            The message which contains the expired `Poll`.
        """
        if not all(hasattr(self, member) for member in ("_state", "channel", "message")):
            raise ValueError(
                "This object was manually builded. To use this method you need to get a poll from the discord API!"
            )

        data = await self._state.http.expire_poll(self.channel.id, self.message.id)
        return message.Message(state=self._state, channel=self.channel, data=data)
