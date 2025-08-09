# SPDX-License-Identifier: MIT

import inspect
from typing import List, Type

import pytest

from disnake import ui

all_ui_component_types: List[Type[ui.UIComponent]] = [
    c
    for c in ui.__dict__.values()
    if isinstance(c, type) and issubclass(c, ui.UIComponent) and not inspect.isabstract(c)
]

all_ui_component_objects: List[ui.UIComponent] = [
    ui.ActionRow(),
    ui.Button(),
    ui.ChannelSelect(),
    ui.MentionableSelect(),
    ui.RoleSelect(),
    ui.StringSelect(),
    ui.UserSelect(),
    ui.TextInput(label="", custom_id=""),
    ui.Section(accessory=ui.Button()),
    ui.TextDisplay(""),
    ui.Thumbnail(""),
    ui.MediaGallery(),
    ui.File(""),
    ui.Separator(),
    ui.Container(),
]

_missing = set(all_ui_component_types) ^ set(map(type, all_ui_component_objects))
assert not _missing, f"missing component objects: {_missing}"


@pytest.mark.parametrize(
    "obj",
    all_ui_component_objects,
    ids=[type(o).__name__ for o in all_ui_component_objects],
)
def test_id_property(obj: ui.UIComponent) -> None:
    assert obj.id == 0
    obj.id = 1234
    assert obj.id == 1234

    if isinstance(obj, ui.Item):
        obj2 = type(obj).from_component(obj._underlying)
        assert obj2.id == 1234
