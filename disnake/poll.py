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

    from .message import Message
    from .state import ConnectionState
    from .types.poll import (
        Poll as PollPayload,
        PollAnswer as PollAnswerPayload,
        PollCreateAnswerPayload,
        PollCreateMediaPayload,
        PollCreatePayload,
        PollMedia as PollMediaPayload,
    )

__all__ = (
    "PollMedia",
    "PollAnswer",
    "Poll",
)


class PollMedia:
    """Represents data of a poll's question/answers.

    .. versionadded:: 2.10

    Parameters
    ----------
    text: :class:`str`
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
        self, text: Optional[str], *, emoji: Optional[Union[Emoji, PartialEmoji, str]] = None
    ) -> None:
        if text is None and emoji is None:
            raise ValueError("At least one of `text` or `emoji` must be not None")

        self.text = text
        self.emoji: Optional[Union[Emoji, PartialEmoji]] = None
        if isinstance(emoji, str):
            self.emoji = PartialEmoji.from_str(emoji)
        elif isinstance(emoji, _EmojiTag):
            self.emoji = emoji
        else:
            if emoji is not None:
                raise TypeError("Emoji must be None, a str, PartialEmoji, or Emoji instance.")

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
            if self.emoji.id:
                payload["emoji"] = {"id": self.emoji.id}
            else:
                payload["emoji"] = {"name": self.emoji.name}
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
        The ID of this answer. This will be ``None`` only if this object was created manually
        and did not originate from the API.
    media: :class:`PollMedia`
        The media fields of this answer.
    poll: Optional[:class:`Poll`]
        The poll associated with this answer. This will be ``None`` only if this object was created manually
        and did not originate from the API.
    vote_count: :class:`int`
        The number of votes for this answer.
    self_voted: :class:`bool`
        Whether the current user voted for this answer.
    """

    __slots__ = ("id", "media", "poll", "vote_count", "self_voted")

    def __init__(self, media: PollMedia) -> None:
        self.id: Optional[int] = None
        self.poll: Optional[Poll] = None
        self.media = media
        self.vote_count: int = 0
        self.self_voted: bool = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} media={self.media!r}>"

    @classmethod
    def from_dict(cls, state: ConnectionState, poll: Poll, data: PollAnswerPayload) -> PollAnswer:
        answer = cls(PollMedia.from_dict(state, data["poll_media"]))
        answer.id = int(data["answer_id"])
        answer.poll = poll

        return answer

    def _to_dict(self) -> PollCreateAnswerPayload:
        return {"poll_media": self.media._to_dict()}

    def voters(
        self, *, limit: Optional[int] = 100, after: Optional[Snowflake] = None
    ) -> PollAnswerIterator:
        """Returns an :class:`AsyncIterator` representing the users that have voted for this answer.

        The ``after`` parameter must represent a member and meet the :class:`abc.Snowflake` abc.

        .. note::

            This method works only on PollAnswer(s) objects that originate from the API and not on the ones built manually.

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
            You tried to invoke this method on an object that didn't originate from the API.

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
                "This object was manually built. To use this method, you need to use a poll object retrieved from the Discord API."
            )

        return PollAnswerIterator(self.poll.message, self.id, limit=limit, after=after)


class Poll:
    """Represents a poll from Discord.

    .. versionadded:: 2.10

    Parameters
    ----------
    question: Union[:class:`str`, :class:`PollMedia`]
        The question of the poll. Currently, emojis are not supported in poll questions.
    answers: List[Union[:class:`str`, :class:`PollAnswer`]]
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
    message: Optional[:class:`Message`]
        The message which contains this poll. This will be ``None`` only if this object was created manually
        and did not originate from the API.
    question: :class:`PollMedia`
        The question of the poll.
    duration: Optional[:class:`datetime.timedelta`]
        The original duration for this poll. ``None`` if the poll is a non-expiring poll.
    allow_multiselect: :class:`bool`
        Whether users are able to pick more than one answer.
    layout_type: :class:`PollLayoutType`
        The type of the layout of the poll.
    is_finalized: :class:`bool`
        Whether the votes have been precisely counted.
    """

    __slots__ = (
        "message",
        "question",
        "_answers",
        "duration",
        "allow_multiselect",
        "layout_type",
        "is_finalized",
    )

    def __init__(
        self,
        question: Union[str, PollMedia],
        *,
        answers: List[Union[str, PollAnswer]],
        duration: timedelta = timedelta(hours=24),
        allow_multiselect: bool = False,
        layout_type: PollLayoutType = PollLayoutType.default,
    ) -> None:
        self.message: Optional[Message] = None

        if isinstance(question, str):
            self.question = PollMedia(question)
        elif isinstance(question, PollMedia):
            self.question: PollMedia = question
        else:
            raise TypeError(
                f"Expected 'str' or 'PollMedia' for 'question', got {question.__class__.__name__!r}."
            )

        self._answers: Dict[int, PollAnswer] = {}
        for i, answer in enumerate(answers, 1):
            if isinstance(answer, PollAnswer):
                self._answers[i] = answer
            elif isinstance(answer, str):
                self._answers[i] = PollAnswer(PollMedia(answer))
            else:
                raise TypeError(
                    f"Expected 'List[str]' or 'List[PollAnswer]' for 'answers', got List[{answer.__class__.__name__!r}]."
                )

        self.duration: Optional[timedelta] = duration
        self.allow_multiselect: bool = allow_multiselect
        self.layout_type: PollLayoutType = layout_type
        self.is_finalized: bool = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} question={self.question!r} answers={self.answers!r}>"

    @property
    def answers(self) -> List[PollAnswer]:
        """List[:class:`PollAnswer`]: The list of answers for this poll.

        See also :meth:`get_answer` to get specific answers by ID.
        """
        return list(self._answers.values())

    @property
    def created_at(self) -> Optional[datetime]:
        """Optional[:class:`datetime.datetime`]: When this poll was created.

        ``None`` if this poll does not originate from the discord API.
        """
        if not self.message:
            return
        return utils.snowflake_time(self.message.id)

    @property
    def expires_at(self) -> Optional[datetime]:
        """Optional[:class:`datetime.datetime`]: The date when this poll will expire.

        ``None`` if this poll does not originate from the discord API or if this
        poll is non-expiring.
        """
        # non-expiring poll
        if not self.duration:
            return

        created_at = self.created_at
        # manually built object
        if not created_at:
            return
        return created_at + self.duration

    @property
    def remaining_duration(self) -> Optional[timedelta]:
        """Optional[:class:`datetime.timedelta`]: The remaining duration for this poll.
        If this poll is finalized this property will arbitrarily return a
        zero valued timedelta.

        ``None`` if this poll does not originate from the discord API.
        """
        if self.is_finalized:
            return timedelta(hours=0)
        if not self.expires_at or not self.message:
            return

        return self.expires_at - utils.utcnow()

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
        message: Message,
        data: PollPayload,
    ) -> Poll:
        state = message._state
        poll = cls(
            question=PollMedia.from_dict(state, data["question"]),
            answers=[],
            allow_multiselect=data["allow_multiselect"],
            layout_type=try_enum(PollLayoutType, data["layout_type"]),
        )
        for answer in data["answers"]:
            answer_obj = PollAnswer.from_dict(state, poll, answer)
            poll._answers[int(answer["answer_id"])] = answer_obj

        poll.message = message
        if expiry := data["expiry"]:
            poll.duration = utils.parse_time(expiry) - utils.snowflake_time(poll.message.id)
        else:
            # future support for non-expiring polls
            # read the foot note https://discord.com/developers/docs/resources/poll#poll-object-poll-object-structure
            poll.duration = None

        if results := data.get("results"):
            poll.is_finalized = results["is_finalized"]

            for answer_count in results["answer_counts"]:
                try:
                    answer = poll._answers[int(answer_count["id"])]
                except KeyError:
                    # this should never happen
                    continue
                answer.vote_count = answer_count["count"]
                answer.self_voted = answer_count["me_voted"]

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

            This method works only on Poll(s) objects that originate
            from the API and not on the ones built manually.

        Raises
        ------
        HTTPException
            Expiring the poll failed.
        Forbidden
            Tried to expire a poll without the required permissions.
        ValueError
            You tried to invoke this method on an object that didn't originate from the API.```

        Returns
        -------
        :class:`Message`
            The message which contains the expired `Poll`.
        """
        if not self.message:
            raise ValueError(
                "This object was manually built. To use this method, you need to use a poll object retrieved from the Discord API."
            )

        data = await self.message._state.http.expire_poll(self.message.channel.id, self.message.id)
        return self.message._state.create_message(channel=self.message.channel, data=data)
