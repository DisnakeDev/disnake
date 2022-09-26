# SPDX-License-Identifier: MIT

from unittest import mock

import pytest

import disnake
from disnake import InteractionResponseType as ResponseType  # shortcut
from disnake.utils import MISSING


@pytest.mark.asyncio
class TestInteractionResponse:
    @pytest.fixture()
    def response(self):
        inter = mock.Mock(disnake.Interaction)
        return disnake.InteractionResponse(inter)

    @pytest.fixture()
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
    ):
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
    ):
        response._parent.type = disnake.InteractionType.component

        await response.defer(with_message=with_message, ephemeral=True)
        adapter.create_interaction_response.assert_awaited_once_with(
            response._parent.id,
            response._parent.token,
            session=response._parent._session,
            type=mock.ANY,
            data=expected_data,
        )

    async def test_defer_invalid_parent(self, response: disnake.InteractionResponse, adapter):
        # autocomplete can't be deferred
        response._parent.type = disnake.InteractionType.application_command_autocomplete

        with pytest.raises(TypeError, match="This interaction must be of type"):
            await response.defer()
        adapter.create_interaction_response.assert_not_called()
