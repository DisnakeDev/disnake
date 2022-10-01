# SPDX-License-Identifier: MIT

from typing import Union
from unittest import mock

import pytest

import disnake
from disnake import Member, Role, User
from disnake.ext import commands

OptionType = disnake.OptionType


class TestParamInfo:
    @pytest.mark.parametrize(
        ("annotation", "expected_type", "arg_types"),
        [
            # should accept user or member
            (disnake.abc.User, OptionType.user, [User, Member]),
            (User, OptionType.user, [User, Member]),
            (Union[User, Member], OptionType.user, [User, Member]),
            # only accepts member, not user
            (Member, OptionType.user, [Member]),
            # only accepts role
            (Role, OptionType.role, [Role]),
            # should accept member or role
            (Union[Member, Role], OptionType.mentionable, [Member, Role]),
            # should accept everything
            (Union[User, Role], OptionType.mentionable, [User, Member, Role]),
            (Union[User, Member, Role], OptionType.mentionable, [User, Member, Role]),
            (disnake.abc.Snowflake, OptionType.mentionable, [User, Member, Role]),
        ],
    )
    @pytest.mark.asyncio
    async def test_verify_type(self, annotation, expected_type, arg_types) -> None:
        # tests that the Discord option type is determined correctly,
        # and that valid argument types are accepted
        info = commands.ParamInfo()
        info.parse_annotation(annotation)

        # type should be valid
        assert info.discord_type is expected_type

        for arg_type in arg_types:
            arg_mock = mock.Mock(arg_type)
            assert await info.verify_type(mock.Mock(), arg_mock) is arg_mock

    @pytest.mark.parametrize(
        ("annotation", "arg_types"),
        [
            (Member, [User]),
            (Union[Member, Role], [User]),
        ],
    )
    @pytest.mark.asyncio
    async def test_verify_type__invalid_member(self, annotation, arg_types) -> None:
        # tests that invalid argument types result in `verify_type` raising an exception
        info = commands.ParamInfo()
        info.parse_annotation(annotation)

        for arg_type in arg_types:
            arg_mock = mock.Mock(arg_type)
            with pytest.raises(commands.errors.MemberNotFound):
                await info.verify_type(mock.Mock(), arg_mock)
