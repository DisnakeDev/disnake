# SPDX-License-Identifier: MIT

from unittest import mock

import pytest

import disnake
from disnake import ui


class TestDefaultValues:
    @pytest.mark.parametrize(
        "value",
        [
            disnake.Object(123),
            disnake.SelectDefaultValue(123, disnake.SelectDefaultValueType.channel),
            mock.Mock(disnake.TextChannel, id=123),
        ],
    )
    def test_valid(self, value) -> None:
        s = ui.ChannelSelect(default_values=[value])
        assert s.default_values[0].id == 123
        assert s.default_values[0].type == disnake.SelectDefaultValueType.channel

    @pytest.mark.parametrize(
        ("select_type", "value_type"),
        [
            (ui.ChannelSelect, disnake.Member),
            # MentionableSelect in particular should reject `Object` due to ambiguities
            (ui.MentionableSelect, disnake.Object),
        ],
    )
    def test_invalid(self, select_type, value_type) -> None:
        with pytest.raises(TypeError, match="Expected type of default value"):
            select_type(default_values=[mock.Mock(value_type, id=123)])

    @pytest.mark.parametrize(
        ("value_type", "expected"),
        [
            (disnake.Member, disnake.SelectDefaultValueType.user),
            (disnake.ClientUser, disnake.SelectDefaultValueType.user),
            (disnake.Role, disnake.SelectDefaultValueType.role),
        ],
    )
    def test_mentionable(self, value_type, expected) -> None:
        s = ui.MentionableSelect(default_values=[mock.Mock(value_type, id=123)])
        assert s.default_values[0].type == expected
