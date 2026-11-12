# SPDX-License-Identifier: MIT

import inspect
from collections.abc import Sequence

import pytest

from disnake import components, ui

# note: these may contain duplicates for aliases (Select = StringSelect)
all_ui_component_types: list[type[ui.UIComponent]] = [
    c
    for c in ui.__dict__.values()
    if isinstance(c, type) and issubclass(c, ui.UIComponent) and not inspect.isabstract(c)
]
all_component_types: list[type[components.Component]] = [
    c
    for c in components.__dict__.values()
    if isinstance(c, type)
    and c not in (components.Component, components.BaseSelectMenu)
    and issubclass(c, components.Component)
]

all_ui_component_objects: list[ui.UIComponent] = [
    ui.ActionRow(),
    ui.Button(),
    ui.StringSelect(),
    ui.TextInput(),
    ui.UserSelect(),
    ui.RoleSelect(),
    ui.MentionableSelect(),
    ui.ChannelSelect(),
    ui.Section(accessory=ui.Button()),
    ui.TextDisplay(""),
    ui.Thumbnail(""),
    ui.MediaGallery(),
    ui.File("attachment://x"),
    ui.Separator(),
    ui.Container(),
    ui.Label("", ui.TextInput()),
    ui.FileUpload(),
    ui.RadioGroup([]),
    ui.CheckboxGroup([]),
    ui.Checkbox(),
]

_missing = set(all_ui_component_types) ^ set(map(type, all_ui_component_objects))
assert not _missing, f"missing component objects: {_missing}"


# TODO: this could be generalized for other classes making use of __repr_attributes__
@pytest.mark.parametrize(
    "cls",
    all_ui_component_types + all_component_types,
    ids=[cls.__name__ for l in (all_ui_component_types, all_component_types) for cls in l],
)
def test_ui__repr_attributes__(cls) -> None:
    assert hasattr(cls, "__repr_attributes__")
    assert not isinstance(cls.__repr_attributes__, str), "__repr_attributes__ should be a Sequence"
    assert isinstance(cls.__repr_attributes__, Sequence)
    assert cls.__repr_attributes__, "empty __repr_attributes__"
    assert all(isinstance(s, str) for s in cls.__repr_attributes__)


@pytest.mark.parametrize(
    "obj",
    all_ui_component_objects,
    ids=[o.__class__.__name__ for o in all_ui_component_objects],
)
def test_id_property(obj: ui.UIComponent) -> None:
    assert obj.id == 0
    obj.id = 1234
    assert obj.id == 1234

    obj2 = type(obj).from_component(obj._underlying)
    assert obj2.id == 1234
