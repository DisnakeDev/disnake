# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from . import utils
from .abc import Snowflake
from .emoji import Emoji, _EmojiTag
from .enums import PollLayoutType, try_enum
from .iterators import PollAnswerIterator
from .partial_emoji import PartialEmoji

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import MessageableChannel
    from .message import Message
    from .state import ConnectionState
    from .types.poll import (
        Poll as PollPayload,
        PollAnswer as PollAnswerPayload,
        PollAnswerCount as PollAnswerCountPayload,
        PollCreateAnswerPayload,
        PollCreateMediaPayload,
        PollCreatePayload,
        PollMedia as PollMediaPayload,
    )

__all__ = (
    "PollAnswerCount",
    "PollMedia",
    "PollAnswer",
    "Poll",
)


class PollAnswerCount:
    """Represents a poll answer count from discord.

    .. versionadded:: 2.10

    Attributes
    ----------
    id: :class:`int`
        The ID of the answer the counts are of.
    count: :class:`int`
        The number of votes for this answer.
    self_voted: :class:`bool`
        Whether the current user voted for this answer.
    """

    __slots__ = (
        "id",
        "count",
        "self_voted",
    )

    def __init__(self, data: PollAnswerCountPayload) -> None:
        self.id: int = int(data["id"])
        self.count: int = int(data["count"])
        self.self_voted: bool = data["me_voted"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} count={self.count} self_voted={self.self_voted}>"


class PollMedia:
    """Represents data of a poll's question/answers.

    You must specify at least one of the parameters when creating an instance.

    .. versionadded:: 2.10

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
            raise ValueError("At least one of `text` or `emoji` must not be None")

        self.text = text
        self.emoji: Optional[Union[Emoji, PartialEmoji]] = None
        if emoji is None:
            self.emoji = None
        elif isinstance(emoji, str):
            self.emoji = PartialEmoji.from_str(emoji)
        elif isinstance(emoji, _EmojiTag):
            self.emoji = emoji
        else:
            raise TypeError("emoji must be None, a str, PartialEmoji, or Emoji instance.")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} text={self.text!r} emoji={self.emoji!r}>"

    @classmethod
    def from_dict(cls, state: ConnectionState, data: PollMediaPayload) -> PollMedia:
        text = data.get("text")

        emoji = None
        if emoji_data := data.get("emoji"):
            emoji = state._get_emoji_from_data(emoji_data)

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
            else:
                payload["emoji"] = {"name": self.emoji}
        return payload


class PollAnswer:
    """Represents a poll answer from discord.

    .. versionadded:: 2.10

    Parameters
    ----------
    media: :class:`PollMedia`
        The media object to set the text and/or emoji for this answer.

    Attributes
    ----------
    id: Optional[:class:`int`]
        The ID of the answer that this object represents. This will be None only when the object
        is builded manually. The library always provide this attribute.
    media: :class:`PollMedia`
        The media fields linked to this answer.
    poll: Optional[:class:`Poll`]
        The poll that contain this answer. This will be None only when the object
        is builded manually. The library always provide this attribute.
    count: :class:`int`
        The number of votes for this answer.
    self_voted: :class:`bool`
        Whether the current user voted for this answer.
    """

    __slots__ = ("_state", "id", "media", "poll", "count", "self_voted")

    def __init__(self, media: PollMedia) -> None:
        self._state: Optional[ConnectionState] = None
        self.id: Optional[int] = None
        self.poll: Optional[Poll] = None
        self.media = media
        self.count: int = 0
        self.self_voted: bool = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} poll_media={self.media!r}>"

    @classmethod
    def from_dict(cls, state: ConnectionState, data: PollAnswerPayload) -> PollAnswer:
        answer = cls(PollMedia.from_dict(state, data["poll_media"]))
        answer.id = int(data["answer_id"])
        answer._state = state

        return answer

    def _to_dict(self) -> PollCreateAnswerPayload:
        return {"poll_media": self.media._to_dict()}

    def voters(
        self, *, limit: Optional[int] = 100, after: Optional[Snowflake] = None
    ) -> PollAnswerIterator:
        """Returns an :class:`AsyncIterator` representing the users that have voted for this answer.

        The ``after`` parameter must represent a member and meet the :class:`abc.Snowflake` abc.

        .. note::

            This method works only on PollAnswer(s) objects that are fetched from the API and not on the ones built manually.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The maximum number of results to return.
            If ``None``, retrieves every user who voted for this answer.
            Note, however, that this would make it a slow operation.
            Defaults to ``100``.
        after: Optional[:class:`abc.Snowflake`]
            For pagination, votes are sorted by member.

        Raises
        ------
        HTTPException
            Getting the voters for this answer failed.
        Forbidden
            Tried to get the voters for this answer without the required permissions.
        ValueError
            You tried to invoke this method on an incomplete object, most likely one that wasn't fetched from the API.

        Yields
        ------
        Union[:class:`User`, :class:`Member`]
            The member (if retrievable) or the user that has voted
            for this answer. The case where it can be a :class:`Member` is
            in a guild message context. Sometimes it can be a :class:`User`
            if the member has left the guild.
        """
        if not (self.id is not None and self.poll and self.poll.message):
            raise ValueError(
                "This object was manually builded. To use this method you need to get a poll from the discord API!"
            )

        return PollAnswerIterator(self.poll.message, self.id, limit=limit, after=after)


class Poll:
    """Represents a poll from Discord.

    .. versionadded:: 2.10

    Parameters
    ----------
    question: :class:`PollMedia`
        The question of the poll.
    answers: List[:class:`PollAnswer`]
        The answers for this poll, up to 10.
    duration: :class:`datetime.timedelta`
        The total duration of the poll, up to 32 days. Defaults to 1 day.
        Note that this gets rounded down to the closest hour.
    allow_multiselect: :class:`bool`
        Whether users will be able to pick more than one answer. Defaults to ``False``.
    layout_type: :class:`PollLayoutType`
        The layout type of the poll. Defaults to :attr:`PollLayoutType.default`.

    Attributes
    ----------
    channel: Optional[Union[:class:`TextChannel`, :class:`VoiceChannel`, :class:`StageChannel`, :class:`Thread`, :class:`DMChannel`, :class:`GroupChannel`, :class:`PartialMessageable`]]
        The channel that the poll was sent from. This will be None only when the object
        is builded manually. The library always provide this attribute.

        .. note::

            This attribute is available only if you fetched the Poll object from the API.

    message: Optional[:class:`Message`]
        The message which contain this poll. This will be None only when the object
        is builded manually. The library always provide this attribute.

        .. note::

            This attribute is available only if you fetched the Poll object from the API.

    question: Union[:class:`str`, :class:`PollMedia`]
        The question of the poll.
    duration: Optional[:class:`datetime.timedelta`]
        The remaining duration for this poll. ``None`` if already expired.
    allow_multiselect: :class:`bool`
        Whether users are able to pick more than one answer.
    layout_type: :class:`PollLayoutType`
        The type of the layout of the poll.
    is_finalized: :class:`bool`
        Whether the votes have been precisely counted.
    answer_counts: Optional[List[:class:`PollAnswerCount`]]
        The counts for each answer.
    """

    __slots__ = (
        "_state",
        "channel",
        "message",
        "question",
        "_answers",
        "duration",
        "allow_multiselect",
        "layout_type",
        "is_finalized",
        "answer_counts",
    )

    def __init__(
        self,
        question: Union[str, PollMedia],
        *,
        answers: List[PollAnswer],
        duration: timedelta = timedelta(hours=24),
        allow_multiselect: bool = False,
        layout_type: PollLayoutType = PollLayoutType.default,
    ) -> None:
        self._state: Optional[ConnectionState] = None
        self.channel: Optional[MessageableChannel] = None
        self.message: Optional[Message] = None

        if isinstance(question, str):
            self.question = PollMedia(question)
        else:
            self.question: PollMedia = question

        self._answers: Dict[int, PollAnswer] = {}
        for answer in answers:
            self._answers[len(self._answers) + 1] = answer

        self.duration: Optional[timedelta] = duration
        self.allow_multiselect: bool = allow_multiselect
        self.layout_type: PollLayoutType = layout_type
        self.is_finalized: bool = False
        self.answer_counts: Optional[List[PollAnswerCount]] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} question={self.question} answers={self.answers!r}>"

    @property
    def answers(self) -> List[PollAnswer]:
        """List[:class:`PollAnswer`]: return the list of answers for this poll."""
        return list(self._answers.values())

    @property
    def expires_at(self) -> Optional[datetime]:
        """Optional[:class:`datetime`]: the expiration date for this poll, if available."""
        if not self.duration or not self.message:
            return
        return self.message.created_at + self.duration

    def get_answer(self, answer_id: int, /) -> Optional[PollAnswer]:
        """Return the requested poll answer.

        Parameters
        ----------
        answer_id: :class:`int`
            The answer id.

        Returns
        -------
        Optional[:class:`PollAnswer`]
            The requested answer.
        """
        return self._answers.get(answer_id)

    @classmethod
    def from_dict(
        cls,
        channel: MessageableChannel,
        message: Message,
        state: ConnectionState,
        data: PollPayload,
    ) -> Poll:
        poll = cls(
            question=PollMedia.from_dict(state, data["question"]),
            answers=[],
            allow_multiselect=data["allow_multiselect"],
            layout_type=try_enum(PollLayoutType, data["layout_type"]),
        )
        for answer in data["answers"]:
            poll._answers[answer["answer_id"]] = PollAnswer.from_dict(state, answer)

        poll._state = state
        poll.channel = channel
        poll.message = message

        # this should always be not None but we check
        # for a null value anyway
        if results := data.get("results"):
            poll.is_finalized = results["is_finalized"]
            poll.answer_counts = [PollAnswerCount(answer) for answer in results["answer_counts"]]

        if poll.is_finalized:
            poll.duration = None
        else:
            poll.duration = (
                (utils.parse_time(data["expiry"]) - message.created_at) if data["expiry"] else None
            )

        return poll

    def _to_dict(self) -> PollCreatePayload:
        payload: PollCreatePayload = {
            "question": self.question._to_dict(),
            "duration": (int(self.duration.total_seconds()) // 3600),  # type: ignore
            "allow_multiselect": self.allow_multiselect,
            "layout_type": self.layout_type.value,
            "answers": [answer._to_dict() for answer in self._answers.values()],
        }
        return payload

    async def expire(self) -> Message:
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
        if not self._state or not self.channel or not self.message:
            raise ValueError(
                "This object was manually builded. To use this method you need to get a poll from the discord API!"
            )

        data = await self._state.http.expire_poll(self.channel.id, self.message.id)
        return self._state.create_message(channel=self.channel, data=data)
