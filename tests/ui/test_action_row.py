# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING
from unittest import mock

import pytest
from typing_extensions import assert_type

import disnake
from disnake.ui import (
    ActionRow,
    Button,
    Label,
    Separator,
    StringSelect,
    TextInput,
    WrappedComponent,
)
from disnake.ui._types import ActionRowMessageComponent, ActionRowModalComponent
from disnake.ui.action_row import normalize_components, normalize_components_to_dict

button1 = Button()
button2 = Button()
button3 = Button()
select = StringSelect()
text_input = TextInput(label="a", custom_id="b")
separator = Separator()
label__text = Label("a", text_input)
label__select = Label("a", select)


class TestActionRow:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ([], 0),
            ([button1], 1),
            ([button1] * 4, 4),
            ([select], 5),
        ],
    )
    def test_width(self, value, expected) -> None:
        assert ActionRow(*value).width == expected

    def test_append_item(self) -> None:
        r = ActionRow()
        r.append_item(button1)
        r.append_item(button2)

        with pytest.raises(ValueError, match=r"Too many components in this row"):
            r.append_item(select)

        assert list(r.children) == [button1, button2]

    def test_insert_item(self) -> None:
        r = ActionRow()
        r.insert_item(0, button1)
        r.insert_item(0, button2)
        r.insert_item(1, button3)

        assert list(r.children) == [button2, button3, button1]

        r.insert_item(-2, button1)
        assert list(r.children) == [button2, button1, button3, button1]

    @pytest.mark.parametrize("index", [None, 1])
    def test_add_button(self, index) -> None:
        r = ActionRow(button1, button2)
        r.add_button(
            **({"index": index} if index is not None else {}),
            custom_id="asdf",
        )

        new_button = disnake.utils.get(r.children, custom_id="asdf")
        assert isinstance(new_button, Button)
        if index is None:
            assert list(r.children) == [button1, button2, new_button]
        else:
            assert list(r.children) == [button1, new_button, button2]

        if TYPE_CHECKING:
            _ = ActionRow().add_button
            _ = ActionRow.with_message_components().add_button
            # should not work
            _ = ActionRow.with_modal_components().add_button  # type: ignore

    def test_add_select(self) -> None:
        r = ActionRow.with_message_components()
        r.add_string_select(custom_id="asdf")

        (c,) = r.children
        assert isinstance(c, StringSelect)
        assert c.custom_id == "asdf"

        if TYPE_CHECKING:
            _ = ActionRow().add_string_select
            _ = ActionRow.with_message_components().add_string_select
            # should not work
            _ = ActionRow.with_modal_components().add_select  # type: ignore

    def test_add_text_input(self) -> None:
        with pytest.warns(DeprecationWarning):
            r = ActionRow.with_modal_components()
        with pytest.warns(DeprecationWarning):
            r.add_text_input(label="a", custom_id="asdf")

        (c,) = r.children
        assert isinstance(c, TextInput)
        assert c.custom_id == "asdf"

        if TYPE_CHECKING:
            _ = ActionRow().add_text_input
            _ = ActionRow.with_modal_components().add_text_input
            # should not work
            _ = ActionRow.with_message_components().add_text_input  # type: ignore

    def test_clear_items(self) -> None:
        r = ActionRow(button1, button2)
        r.clear_items()
        assert list(r.children) == []

    def test_remove_item(self) -> None:
        r = ActionRow(button1, button2)
        r.remove_item(button1)
        assert list(r.children) == [button2]

    def test_pop(self) -> None:
        r = ActionRow(button1, button2)
        assert r.pop(0) is button1
        assert list(r.children) == [button2]

    def test_dunder(self) -> None:
        r = ActionRow(button1, button2)
        assert r[1] is button2

        del r[0]
        assert list(r.children) == [button2]

    def test_with_components(self) -> None:
        with pytest.warns(DeprecationWarning):
            row_modal = ActionRow.with_modal_components()
        assert list(row_modal.children) == []
        row_msg = ActionRow.with_message_components()
        assert list(row_msg.children) == []

        assert_type(row_modal, ActionRow[ActionRowModalComponent])
        assert_type(row_msg, ActionRow[ActionRowMessageComponent])

    def test_rows_from_message(self) -> None:
        rows = [
            ActionRow(button1, button2),
            ActionRow(select),
            ActionRow(button2),
            ActionRow(button3),
        ]

        message = mock.Mock(disnake.Message)
        message.components = [r._underlying for r in rows]
        result = ActionRow.rows_from_message(message)

        assert len(result) == len(rows)
        # compare component types and IDs
        for actual, expected in zip(result, rows, strict=False):
            assert [(type(c), c.custom_id) for c in actual] == [
                (type(c), c.custom_id) for c in expected
            ]

    def test_rows_from_message__invalid(self) -> None:
        message = mock.Mock(disnake.Message)
        message.components = [ActionRow(text_input)._underlying]

        # check non-strict behavior
        non_strict = ActionRow.rows_from_message(message, strict=False)
        assert len(non_strict) == 1
        assert len(non_strict[0]) == 0

        # check (default) strict behavior
        with pytest.raises(TypeError, match=r"Encountered unknown component type: .*text_input"):
            ActionRow.rows_from_message(message)

    def test_walk_components(self) -> None:
        rows = [
            ActionRow(button1, button2),
            ActionRow(select),
            ActionRow(button2),
            ActionRow(button3),
        ]

        expected = [(row, component) for row in rows for component in row.children]
        for (act_row, act_cmp), (exp_row, exp_cmp) in zip(
            ActionRow.walk_components(rows), expected, strict=False
        ):
            # test mutation (rows)
            # (remove row below the one containing select1)
            if act_cmp is select:
                rows.pop(rows.index(act_row) + 1)

            # test mutation (children)
            # (remove button1 from rows)
            if act_cmp is button1:
                act_row.remove_item(act_cmp)

            assert act_row is exp_row
            assert act_cmp is exp_cmp

    # this method is mainly for pyright to check, the asserts wouldn't do anything at runtime
    def _test_typing_init(self) -> None:  # pragma: no cover
        assert_type(ActionRow(), ActionRow[WrappedComponent])

        assert_type(ActionRow(button1), ActionRow[ActionRowMessageComponent])
        assert_type(ActionRow(select), ActionRow[ActionRowMessageComponent])
        assert_type(ActionRow(text_input), ActionRow[ActionRowModalComponent])

        assert_type(ActionRow(button1, select), ActionRow[ActionRowMessageComponent])
        assert_type(ActionRow(select, button1), ActionRow[ActionRowMessageComponent])


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ([], []),
        ([[]], [[]]),
        # nested lists
        (button1, [[button1]]),
        ([button1], [[button1]]),
        ([button1, button2], [[button1, button2]]),
        ([text_input, select], [[text_input], [select]]),
        (([button1],), [[button1]]),
        ([(button1,), button2], [[button1], [button2]]),
        # actionrows
        (ActionRow(button1), [[button1]]),
        ([ActionRow(button1)], [[button1]]),
        ([ActionRow(button1), button2], [[button1], [button2]]),
        ([button1, button2, ActionRow(button3)], [[button1, button2], [button3]]),
        # width limit
        ([button1] * 10, [[button1] * 5] * 2),
        ([button1, select], [[button1], [select]]),
        ([select, button1, button2], [[select], [button1, button2]]),
    ],
)
def test_normalize_components__actionrow(value, expected) -> None:
    rows = normalize_components(value)
    assert all(isinstance(row, ActionRow) for row in rows)
    assert [list(row.children) for row in rows] == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # simple cases
        ([separator], [separator]),
        ([separator, ActionRow(button1)], [separator, [button1]]),
        ([ActionRow(button1), separator], [[button1], separator]),
        ([separator, ActionRow(button1), separator], [separator, [button1], separator]),
        # flat list
        ([button1, separator], [[button1], separator]),
        ([separator, button1], [separator, [button1]]),
        (
            [separator, button1, button2, separator, button3],
            [separator, [button1, button2], separator, [button3]],
        ),
    ],
)
def test_normalize_components__v2(value, expected) -> None:
    result = normalize_components(value)
    assert [(list(c.children) if isinstance(c, ActionRow) else c) for c in result] == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ([text_input], [[text_input]]),
        ([select], [select]),  # should not wrap select in action row
        (
            [label__text, text_input, select, label__select, text_input],
            [label__text, [text_input], select, label__select, [text_input]],
        ),
    ],
)
def test_normalize_components__modal(value, expected) -> None:
    result = normalize_components(value, modal=True)
    assert [(list(c.children) if isinstance(c, ActionRow) else c) for c in result] == expected


def test_normalize_components__invalid() -> None:
    for value in (42, [42], [ActionRow(), 42], iter([button1])):
        with pytest.raises(TypeError, match=r"`components` must be a"):
            normalize_components(value)  # type: ignore
    for value in ([[[]]], [[[ActionRow()]]]):
        with pytest.raises(TypeError, match=r"components should be of type"):
            normalize_components(value)  # type: ignore


def test_normalize_components_to_dict() -> None:
    result, is_v2 = normalize_components_to_dict([button1, button2, select, ActionRow(button3)])
    assert result == [
        {
            "type": 1,
            "id": 0,
            "components": [button1.to_component_dict(), button2.to_component_dict()],
        },
        {
            "type": 1,
            "id": 0,
            "components": [select.to_component_dict()],
        },
        {
            "type": 1,
            "id": 0,
            "components": [button3.to_component_dict()],
        },
    ]
    assert not is_v2


def test_normalize_components_to_dict__v2() -> None:
    _, is_v2 = normalize_components_to_dict([button1, separator, button2])
    assert is_v2
