# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

import disnake
from disnake import InteractionResponseType as ResponseType  # shortcut
from disnake.state import ConnectionState
from disnake.utils import MISSING

if TYPE_CHECKING:
    from disnake.types.interactions import ResolvedPartialChannel as ResolvedPartialChannelPayload
    from disnake.types.member import Member as MemberPayload
    from disnake.types.user import User as UserPayload


@pytest.mark.asyncio
class TestInteractionResponse:
    @pytest.fixture
    def response(self):
        inter = mock.Mock(disnake.Interaction)
        return disnake.InteractionResponse(inter)

    @pytest.fixture
    def adapter(self):
        adapter = mock.AsyncMock()
        disnake.interactions.base.async_context.set(adapter)
        return adapter

    @pytest.mark.parametrize(
        ("parent_type", "with_message", "expected"),
        [
            # application_command
            (
                disnake.InteractionType.application_command,
                MISSING,
                {"type": ResponseType.deferred_channel_message.value, "data": {"flags": 0}},
            ),
            (
                disnake.InteractionType.application_command,
                False,
                {"type": ResponseType.deferred_channel_message.value, "data": {"flags": 0}},
            ),
            (
                disnake.InteractionType.application_command,
                True,
                {"type": ResponseType.deferred_channel_message.value, "data": {"flags": 0}},
            ),
            # component
            (
                disnake.InteractionType.component,
                MISSING,
                {"type": ResponseType.deferred_message_update.value, "data": None},
            ),
            (
                disnake.InteractionType.component,
                False,
                {"type": ResponseType.deferred_message_update.value, "data": None},
            ),
            (
                disnake.InteractionType.component,
                True,
                {"type": ResponseType.deferred_channel_message.value, "data": {"flags": 0}},
            ),
            # modal_submit
            (
                disnake.InteractionType.modal_submit,
                MISSING,
                {"type": ResponseType.deferred_channel_message.value, "data": {"flags": 0}},
            ),
            (
                disnake.InteractionType.modal_submit,
                False,
                {"type": ResponseType.deferred_message_update.value, "data": None},
            ),
            (
                disnake.InteractionType.modal_submit,
                True,
                {"type": ResponseType.deferred_channel_message.value, "data": {"flags": 0}},
            ),
        ],
    )
    async def test_defer(
        self, response: disnake.InteractionResponse, adapter, parent_type, with_message, expected
    ) -> None:
        response._parent.type = parent_type

        await response.defer(with_message=with_message)
        adapter.create_interaction_response.assert_awaited_once_with(
            response._parent.id,
            response._parent.token,
            session=response._parent._session,
            **expected,
        )

    @pytest.mark.parametrize(
        ("with_message", "expected_data"),
        [
            (False, None),
            (True, {"flags": 64}),
        ],
    )
    async def test_defer_ephemeral(
        self, response: disnake.InteractionResponse, adapter, with_message, expected_data
    ) -> None:
        response._parent.type = disnake.InteractionType.component

        await response.defer(with_message=with_message, ephemeral=True)
        adapter.create_interaction_response.assert_awaited_once_with(
            response._parent.id,
            response._parent.token,
            session=response._parent._session,
            type=mock.ANY,
            data=expected_data,
        )

    async def test_defer_invalid_parent(
        self, response: disnake.InteractionResponse, adapter
    ) -> None:
        # autocomplete can't be deferred
        response._parent.type = disnake.InteractionType.application_command_autocomplete

        with pytest.raises(TypeError, match="This interaction must be of type"):
            await response.defer()
        adapter.create_interaction_response.assert_not_called()


class TestInteractionDataResolved:
    # TODO: use proper mock models once we have state/guild mocks
    @pytest.fixture
    def state(self):
        s = mock.Mock(spec_set=ConnectionState)
        s._get_guild.return_value = None
        return s

    def test_init_member(self, state) -> None:
        member_payload: MemberPayload = {
            "roles": [],
            "joined_at": "2022-09-02T22:00:55.069000+00:00",
            "deaf": False,
            "mute": False,
            "flags": 0,
        }

        user_payload: UserPayload = {
            "id": "1234",
            "discriminator": "1111",
            "username": "h",
            "avatar": None,
        }

        # user only, should deserialize user object
        resolved = disnake.InteractionDataResolved(
            data={"users": {"1234": user_payload}},
            state=state,
            guild_id=1234,
        )
        assert len(resolved.members) == 0
        assert len(resolved.users) == 1

        # member only, shouldn't deserialize anything
        resolved = disnake.InteractionDataResolved(
            data={"members": {"1234": member_payload}},
            state=state,
            guild_id=1234,
        )
        assert len(resolved.members) == 0
        assert len(resolved.users) == 0

        # user + member, should deserialize member object only
        resolved = disnake.InteractionDataResolved(
            data={"users": {"1234": user_payload}, "members": {"1234": member_payload}},
            state=state,
            guild_id=1234,
        )
        assert len(resolved.members) == 1
        assert len(resolved.users) == 0

    @pytest.mark.parametrize("channel_type", [t.value for t in disnake.ChannelType])
    def test_channel(self, state, channel_type) -> None:
        channel_data: ResolvedPartialChannelPayload = {
            "id": "42",
            "type": channel_type,
            "permissions": "7",
            "name": "a-channel",
        }
        if channel_type in (10, 11, 12):  # thread
            channel_data["parent_id"] = "123123"
            channel_data["thread_metadata"] = {
                "archived": False,
                "auto_archive_duration": 60,
                "archive_timestamp": "2022-09-02T22:00:55.069000+00:00",
                "locked": False,
            }

        resolved = disnake.InteractionDataResolved(
            data={"channels": {"42": channel_data}}, state=state, guild_id=1234
        )
        assert len(resolved.channels) == 1

        channel = next(iter(resolved.channels.values()))
        # should be partial if and only if it's a dm/group
        # TODO: currently includes directory channels (14), see `InteractionDataResolved.__init__`
        assert isinstance(channel, disnake.PartialMessageable) == (channel_type in (1, 3, 14))
