# SPDX-License-Identifier: MIT

from unittest import mock

import pytest

import disnake
from disnake.abc import GuildChannel
from disnake.utils import MISSING


@pytest.mark.asyncio
class TestGuildChannelEdit:
    # TODO: use proper mock models once we have state/guild mocks
    @pytest.fixture()
    def channel(self):
        ch = mock.Mock(GuildChannel, id=123, category_id=456)
        ch._state = mock.Mock(http=mock.AsyncMock())
        ch.guild = mock.Mock()

        parent = mock.Mock()
        parent._overwrites = [mock.Mock() for _ in range(3)]
        ch.guild.get_channel.return_value = parent

        return ch

    async def test_none(self, channel) -> None:
        res = await GuildChannel._edit(channel, reason="h")
        assert res is None

        channel._move.assert_not_called()
        channel._state.http.edit_channel.assert_not_called()

    async def test_all(self, channel) -> None:
        mock_role = mock.Mock(disnake.Role)
        mock_member = mock.Mock(disnake.Member)

        res = await GuildChannel._edit(
            channel,
            name="new name",
            topic="talk about things here",
            position=10,
            nsfw=True,
            sync_permissions=False,
            category=disnake.Object(321),
            slowmode_delay=8,
            default_thread_slowmode_delay=42,
            default_auto_archive_duration=disnake.ThreadArchiveDuration.hour,
            type=disnake.ChannelType.news,
            overwrites={
                mock_role: disnake.PermissionOverwrite(kick_members=False, send_messages=True),
                mock_member: disnake.PermissionOverwrite(ban_members=False),
            },
            bitrate=42000,
            user_limit=3,
            rtc_region="there",
            video_quality_mode=disnake.VideoQualityMode.full,
            flags=disnake.ChannelFlags(pinned=False, require_tag=True),
            available_tags=[disnake.ForumTag(name="tag", emoji="woo")],
            default_reaction=disnake.PartialEmoji(name="woo", id=9876),
            default_sort_order=disnake.ThreadSortOrder.creation_date,
            reason="stuff",
        )
        assert res is channel._state.http.edit_channel.return_value

        channel._move.assert_awaited_once_with(
            10, parent_id=321, lock_permissions=False, reason="stuff"
        )
        channel._state.http.edit_channel.assert_awaited_once_with(
            channel.id,
            name="new name",
            topic="talk about things here",
            nsfw=True,
            rate_limit_per_user=8,
            default_thread_rate_limit_per_user=42,
            default_auto_archive_duration=60,
            type=5,
            permission_overwrites=[
                {"allow": "2048", "deny": "2", "id": mock_role.id, "type": 0},
                {"allow": "0", "deny": "4", "id": mock_member.id, "type": 1},
            ],
            bitrate=42000,
            user_limit=3,
            rtc_region="there",
            video_quality_mode=2,
            flags=16,
            available_tags=[
                {"name": "tag", "moderated": False, "emoji_name": "woo", "emoji_id": None}
            ],
            default_reaction_emoji={"emoji_name": None, "emoji_id": 9876},
            default_sort_order=1,
            reason="stuff",
        )

    async def test_move_only(self, channel) -> None:
        # test position and related parameters, shouldn't call `edit_channel`
        res = await GuildChannel._edit(
            channel, position=42, category=disnake.Object(999), sync_permissions=True, reason="h"
        )
        assert res is None

        channel._move.assert_awaited_once_with(42, parent_id=999, lock_permissions=True, reason="h")
        channel._state.http.edit_channel.assert_not_called()

    async def test_sync_permissions(self, channel) -> None:
        # test common behavior
        res = await GuildChannel._edit(channel, sync_permissions=True, reason="yes")
        assert res is not None

        channel.guild.get_channel.assert_called_once_with(channel.category_id)
        channel._move.assert_not_called()
        channel._state.http.edit_channel.assert_awaited_once_with(
            channel.id,
            permission_overwrites=[
                o._asdict() for o in channel.guild.get_channel.return_value._overwrites
            ],
            reason="yes",
        )

    async def test_sync_permissions__no_parent(self, channel) -> None:
        # moving channel out of category, `sync_permissions` should do nothing
        res = await GuildChannel._edit(channel, category=None, sync_permissions=True)
        assert res is not None

        channel._move.assert_not_called()
        channel._state.http.edit_channel.assert_awaited_once_with(
            channel.id,
            parent_id=None,
            reason=None,
        )

    async def test_sync_permissions__no_parent_cache(self, channel) -> None:
        # assume parent category doesn't exist in cache
        channel.guild.get_channel.return_value = None

        res = await GuildChannel._edit(channel, sync_permissions=True)
        assert res is None

        channel._move.assert_not_called()
        channel._state.http.edit_channel.assert_not_called()

    @pytest.mark.parametrize("sync_permissions", [MISSING, True])
    async def test_overwrites(self, channel, sync_permissions) -> None:
        # overwrites should override `sync_permissions` parameter
        res = await GuildChannel._edit(channel, sync_permissions=sync_permissions, overwrites={})
        assert res is not None

        channel._move.assert_not_called()
        channel._state.http.edit_channel.assert_awaited_once_with(
            channel.id, permission_overwrites=[], reason=None
        )
