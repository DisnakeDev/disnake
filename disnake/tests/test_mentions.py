# SPDX-License-Identifier: MIT

from typing import Dict, Union
from unittest import mock

import pytest

from disnake import AllowedMentions, Message, MessageType, Object


def test_classmethod_none() -> None:
    none = AllowedMentions.none()
    assert none.everyone is False
    assert none.roles is False
    assert none.users is False
    assert none.replied_user is False


def test_classmethod_all() -> None:
    all_mentions = AllowedMentions.all()
    assert all_mentions.everyone is True
    assert all_mentions.roles is True
    assert all_mentions.users is True
    assert all_mentions.replied_user is True


@pytest.mark.parametrize(
    ("am", "expected"),
    [
        (AllowedMentions(), {"parse": ["everyone", "users", "roles"], "replied_user": True}),
        (AllowedMentions.all(), {"parse": ["everyone", "users", "roles"], "replied_user": True}),
        (AllowedMentions(everyone=False), {"parse": ["users", "roles"], "replied_user": True}),
        (
            AllowedMentions(users=[Object(x) for x in [123, 456, 789]]),
            {"parse": ["everyone", "roles"], "replied_user": True, "users": [123, 456, 789]},
        ),
        (
            AllowedMentions(
                users=[Object(x) for x in [123, 456, 789]],
                roles=[Object(x) for x in [123, 456, 789]],
            ),
            {
                "parse": ["everyone"],
                "replied_user": True,
                "users": [123, 456, 789],
                "roles": [123, 456, 789],
            },
        ),
        (AllowedMentions.none(), {"parse": []}),
    ],
)
def test_to_dict(am: AllowedMentions, expected: Dict[str, Union[bool, list]]) -> None:
    assert expected == am.to_dict()


@pytest.mark.parametrize(
    ("og", "to_merge", "expected"),
    [
        (AllowedMentions.none(), AllowedMentions.none(), AllowedMentions.none()),
        (AllowedMentions.none(), AllowedMentions(), AllowedMentions.none()),
        (AllowedMentions.all(), AllowedMentions(), AllowedMentions.all()),
        (AllowedMentions(), AllowedMentions(), AllowedMentions()),
        (AllowedMentions.all(), AllowedMentions.none(), AllowedMentions.none()),
        (
            AllowedMentions(everyone=False),
            AllowedMentions(users=True),
            AllowedMentions(everyone=False, users=True),
        ),
        (
            AllowedMentions(users=[Object(x) for x in [123, 456, 789]]),
            AllowedMentions(users=False),
            AllowedMentions(users=False),
        ),
    ],
)
def test_merge(og: AllowedMentions, to_merge: AllowedMentions, expected: AllowedMentions) -> None:
    merged = og.merge(to_merge)

    assert expected.everyone is merged.everyone
    assert expected.users is merged.users
    assert expected.roles is merged.roles
    assert expected.replied_user is merged.replied_user


def test_from_message() -> None:
    # as we don't have a message mock yet we are faking a message here with the necessary components
    msg = mock.NonCallableMock()
    msg.mention_everyone = True
    users = [Object(x) for x in [123, 456, 789]]
    msg.mentions = users
    roles = [Object(x) for x in [123, 456, 789]]
    msg.role_mentions = roles
    msg.reference = None

    am = AllowedMentions.from_message(msg)

    assert am.everyone is True
    # check that while the list matches, it isn't the same list
    assert am.users == users
    assert am.users is not users

    assert am.roles == roles
    assert am.roles is not roles

    assert am.replied_user is False


def test_from_message_replied_user() -> None:
    message = mock.Mock(Message)
    author = Object(123)
    message.mentions = [author]
    assert AllowedMentions.from_message(message).replied_user is False

    message.type = MessageType.reply
    assert AllowedMentions.from_message(message).replied_user is False

    resolved = mock.Mock(Message, author=author)
    message.reference = mock.Mock(resolved=resolved)
    assert AllowedMentions.from_message(message).replied_user is True
