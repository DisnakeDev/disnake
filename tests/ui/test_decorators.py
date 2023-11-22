# SPDX-License-Identifier: MIT

import contextlib
from typing import Any, Iterator, Type, TypeVar

import pytest
from typing_extensions import assert_type

from disnake import ui
from disnake.ui.button import V_co

T = TypeVar("T", bound=ui.Item)


@contextlib.contextmanager
def create_callback(item_type: Type[T]) -> Iterator["ui.item.ItemCallbackType[T]"]:
    async def callback(self, item, inter) -> None:
        pytest.fail("callback should not be invoked")

    yield callback

    # ensure instantiation works
    assert callback.__discord_ui_model_type__(**callback.__discord_ui_model_kwargs__)


class _CustomButton(ui.Button[V_co]):
    def __init__(self, *, param: float = 42.0) -> None:
        pass


class TestDecorator:
    def test_default(self) -> None:
        with create_callback(ui.Button[ui.View]) as func:
            res = ui.button(custom_id="123")(func)
            assert_type(res, ui.item.DecoratedItem[ui.Button[ui.View]])

            assert func.__discord_ui_model_type__ is ui.Button
            assert func.__discord_ui_model_kwargs__ == {"custom_id": "123"}

        with create_callback(ui.StringSelect[ui.View]) as func:
            res = ui.string_select(custom_id="123")(func)
            assert_type(res, ui.item.DecoratedItem[ui.StringSelect[ui.View]])

            assert func.__discord_ui_model_type__ is ui.StringSelect
            assert func.__discord_ui_model_kwargs__ == {"custom_id": "123"}

    # from here on out we're mostly only testing the button decorator,
    # as @ui.string_select etc. works identically

    @pytest.mark.parametrize("cls", [_CustomButton, _CustomButton[Any]])
    def test_cls(self, cls: Type[_CustomButton]) -> None:
        with create_callback(cls) as func:
            res = ui.button(cls=cls, param=1337)(func)
            assert_type(res, ui.item.DecoratedItem[cls])

            # should strip to origin type
            assert func.__discord_ui_model_type__ is _CustomButton
            assert func.__discord_ui_model_kwargs__ == {"param": 1337}

    # typing-only check
    def _test_typing_cls(self) -> None:
        ui.button(
            cls=_CustomButton,
            this_should_not_work="h",  # type: ignore
        )

    @pytest.mark.parametrize(
        ("decorator", "invalid_cls"),
        [
            (ui.button, ui.StringSelect),
            (ui.string_select, ui.Button),
            (ui.user_select, ui.Button),
            (ui.role_select, ui.Button),
            (ui.mentionable_select, ui.Button),
            (ui.channel_select, ui.Button),
        ],
    )
    def test_cls_invalid(self, decorator, invalid_cls) -> None:
        for cls in [123, int, invalid_cls]:
            with pytest.raises(TypeError, match=r"cls argument must be"):
                decorator(cls=cls)
