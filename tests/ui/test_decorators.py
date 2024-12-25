# SPDX-License-Identifier: MIT

import contextlib
from typing import Any, Iterator, Type, TypeVar

import pytest
from typing_extensions import assert_type

from disnake import ui
from disnake.ui.button import V_co

V = TypeVar("V", bound=ui.View)
I = TypeVar("I", bound=ui.Item)


@contextlib.contextmanager
def create_callback(
    view_type: Type[V], item_type: Type[I]
) -> Iterator["ui.item.ItemCallbackType[V, I]"]:
    async def callback(self: V, item: I, inter) -> None:
        pytest.fail("callback should not be invoked")

    yield callback

    # ensure instantiation works
    assert callback.__discord_ui_model_type__(**callback.__discord_ui_model_kwargs__)


class _CustomButton(ui.Button[V_co]):
    def __init__(self, *, param: float = 42.0) -> None:
        pass


class _CustomView(ui.View):
    ...


class TestDecorator:
    def test_default(self) -> None:
        with create_callback(_CustomView, ui.Button[ui.View]) as func:
            res = ui.button(custom_id="123")(func)
            assert_type(res, ui.item.DecoratedItem[ui.Button[_CustomView]])

            assert func.__discord_ui_model_type__ is ui.Button[Any]
            assert func.__discord_ui_model_kwargs__ == {"custom_id": "123"}

        with create_callback(_CustomView, ui.StringSelect[ui.View]) as func:
            res = ui.string_select(custom_id="123")(func)
            assert_type(res, ui.item.DecoratedItem[ui.StringSelect[_CustomView]])

            assert func.__discord_ui_model_type__ is ui.StringSelect[Any]
            assert func.__discord_ui_model_kwargs__ == {"custom_id": "123"}

    # from here on out we're mostly only testing the button decorator,
    # as @ui.string_select etc. works identically

    @pytest.mark.parametrize("cls", [_CustomButton, _CustomButton[Any]])
    def test_cls(self, cls: Type[_CustomButton[ui.View]]) -> None:
        with create_callback(_CustomView, cls) as func:
            res = ui.button(cls=cls, param=1337)(func)
            assert_type(res, ui.item.DecoratedItem[cls])

            assert func.__discord_ui_model_type__ is cls
            assert func.__discord_ui_model_kwargs__ == {"param": 1337}

    # typing-only check
    def _test_typing_cls(self) -> None:
        ui.button(
            cls=_CustomButton,
            this_should_not_work="h",  # type: ignore
        )
