# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, List, Optional, Union

from . import utils
from .emoji import Emoji, _EmojiTag
from .enums import PollLayoutType, try_enum
from .partial_emoji import PartialEmoji
from .user import User

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

    .. versionadded:: 2.10

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

    .. versionadded:: 2.10

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
    text: Optional[:class:`str`]
        The text of the answer.
    emoji: Optional[Union[:class:`Emoji`, :class:`PartialEmoji`, :class:`str`]]
        The emoji of the answer.

        .. note::

            If this is str you are expected to pass the name of the emoji. This works only for discord default emojis. For custom emojis you need to use an Emoji or PartialEmoji object.
    poll: :class:`Poll`
        The poll that contain this answer.

    Attributes
    ----------
    id: :class:`int`
        The ID of the answer that this object represents.
    media: :class:`PollMedia`
        The media fields linked to this answer.
    """

    __slots__ = ("_state", "_channel_id", "_message_id", "id", "media", "poll")

    def __init__(
        self, text: Optional[str] = None, *, emoji: Optional[Union[Emoji, PartialEmoji, str]] = None
    ) -> None:
        self._state: ConnectionState
        self._channel_id: int
        self._message_id: int
        self.id: int
        self.poll: Poll

        self.media = PollMedia(text, emoji=emoji)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} poll_media={self.media!r}>"

    @classmethod
    def from_dict(
        cls, state: ConnectionState, channel_id: int, message_id: int, data: PollAnswerPayload
    ) -> PollAnswer:
        poll_media_payload = data["poll_media"]
        answer = cls(poll_media_payload.get("text"), emoji=poll_media_payload.get("text"))
        answer.id = int(data["answer_id"])
        answer._state = state
        answer._channel_id = channel_id
        answer._message_id = message_id

        return answer

    def _to_dict(self) -> PollCreateAnswerPayload:
        return {"poll_media": self.media._to_dict()}

    async def get_voters(self, after: Optional[int] = None, *, limit: int = 25) -> List[User]:
        """|coro|

        Get a list of users that voted for this specific answer.

        .. note::

            This method works only on PollAnswer(s) objects that are fetched from the API and not on the ones built manually.

        Parameters
        ----------
        after: Optional[:class:`int`]
            Get users who votes for this answer after this user ID.
        limit: :class:`int`
            The maximum number of users to return. Must be between 1 and 100.

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
            self._channel_id, self._message_id, self.id, after=after, limit=limit
        )
        return [User(state=self._state, data=user) for user in data["users"]]


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
        The total duration of the poll, up to 7 days. Defaults to 1 day.
        Note that this gets rounded down to the closest hour.
    allow_multiselect: :class:`bool`
        Whether users will be able to pick more than one answer. Defaults to ``False``.
    layout_type: :class:`PollLayoutType`
        The layout type of the poll. Defaults to :attr:`PollLayoutType.default`.

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

    question: :class:`PollMedia`
        The question of the poll.
    answers: List[:class:`PollAnswer`]
        The available answers for this poll.
    expiry: :class:`datetime.datetime`
        The expiration date till users will be able to vote for this poll.

        .. note::

            This attribute is not None only if you fetched the Poll object from the API.

    allow_multiselect: :class:`bool`
        Whether users are able to pick more than one answer.
    layout_type: :class:`PollLayoutType`
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
        question: PollMedia,
        *,
        answers: List[PollAnswer],
        duration: timedelta = timedelta(hours=24),
        allow_multiselect: bool = False,
        layout_type: PollLayoutType = PollLayoutType.default,
    ) -> None:
        self._state: ConnectionState
        self.channel: MessageableChannel
        self.message: Message

        self.question: PollMedia = question
        self.answers: List[PollAnswer] = answers
        self.results: Optional[PollResult] = None

        self.duration: Optional[timedelta] = duration

        self.allow_multiselect: bool = allow_multiselect
        self.layout_type: PollLayoutType = layout_type

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} question={self.question} answers={self.answers!r}>"

    @property
    def expires_at(self) -> Optional[datetime]:
        if not hasattr(self, "message"):
            return
        if self.duration is None:
            return
        return self.message.created_at + self.duration

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
            answers=[
                PollAnswer.from_dict(state, channel.id, message.id, answer)
                for answer in data["answers"]
            ],
            duration=(
                (utils.parse_time(data["expiry"]) - message.created_at)
                if data["expiry"]
                else None  # type: ignore
            ),
            allow_multiselect=data["allow_multiselect"],
            layout_type=try_enum(PollLayoutType, data["layout_type"]),
        )
        for answer in poll.answers:
            answer.poll = poll
        poll._state = state
        poll.channel = channel
        poll.message = message
        poll.results = None
        if results := data.get("results"):
            poll.results = PollResult(results)

        return poll

    def _to_dict(self) -> PollCreatePayload:
        payload: PollCreatePayload = {
            "question": self.question._to_dict(),
            "duration": (int(self.duration.total_seconds()) // 3600),  # type: ignore
            "allow_multiselect": self.allow_multiselect,
            "layout_type": self.layout_type.value,
            "answers": [answer._to_dict() for answer in self.answers],
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
        if not all(hasattr(self, member) for member in ("_state", "channel", "message")):
            raise ValueError(
                "This object was manually builded. To use this method you need to get a poll from the discord API!"
            )

        data = await self._state.http.expire_poll(self.channel.id, self.message.id)
        return self._state.create_message(channel=self.channel, data=data)
