# SPDX-License-Identifier: MIT

from datetime import datetime, timezone

import pytest

from disnake import Object

snowflake = 881536165478499999  # date/time of first commit


def test_init():
    with pytest.raises(
        TypeError, match=r"id parameter must be convertable to int not <class 'str'>"
    ):
        Object("hi")


def test_compare():
    assert Object(42) == Object(42)
    assert Object(42) != Object(43)


def test_hash():
    assert hash(Object(snowflake)) == 210174600000


def test_created_at():
    assert Object(snowflake).created_at == datetime(2021, 8, 29, 13, 50, 0, tzinfo=timezone.utc)
