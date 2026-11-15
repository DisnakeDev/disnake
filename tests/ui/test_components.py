# SPDX-License-Identifier: MIT

import inspect
from collections.abc import Sequence

import pytest

import disnake
from disnake import ComponentType, components, ui

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
    ui.Button(custom_id=str(ComponentType.button)),
    ui.StringSelect(custom_id=str(ComponentType.string_select)),
    ui.TextInput(custom_id=str(ComponentType.text_input)),
    ui.UserSelect(custom_id=str(ComponentType.user_select)),
    ui.RoleSelect(custom_id=str(ComponentType.role_select)),
    ui.MentionableSelect(custom_id=str(ComponentType.mentionable_select)),
    ui.ChannelSelect(custom_id=str(ComponentType.channel_select)),
    ui.Section(accessory=ui.Button(custom_id=str(ComponentType.button))),
    ui.TextDisplay(""),
    ui.Thumbnail(""),
    ui.MediaGallery(),
    ui.File("attachment://x"),
    ui.Separator(),
    ui.Container(),
    ui.Label("", ui.TextInput(custom_id=str(ComponentType.text_input))),
    ui.FileUpload(custom_id=str(ComponentType.file_upload)),
    ui.RadioGroup([], custom_id=str(ComponentType.radio_group)),
    ui.CheckboxGroup([], custom_id=str(ComponentType.checkbox_group)),
    ui.Checkbox(custom_id=str(ComponentType.checkbox)),
]

_missing = set(all_ui_component_types) ^ set(map(type, all_ui_component_objects))
assert not _missing, f"missing component objects: {_missing}"


# TODO: this could be generalized for other classes making use of __repr_attributes__
@pytest.mark.parametrize(
    "cls",
    all_component_types,
    ids=[cls.__name__ for cls in all_component_types],
)
def test__repr_attributes__(cls) -> None:
    assert cls.__repr__ is not object.__repr__
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
def test_ui__repr__(obj: ui.UIComponent) -> None:
    eval_globals = disnake.__dict__ | ui.__dict__

    assert obj.__class__.__repr__ is not object.__repr__
    assert not hasattr(obj, "__repr_attributes__")
    repr_str = repr(obj)
    try:
        new_obj: ui.UIComponent = eval(repr_str, eval_globals)  # noqa: S307
    except SyntaxError as err:
        pytest.xfail(f"Component cannot be eval'd: {err}")
    # components don't define __eq__
    assert repr(new_obj) == repr_str
    assert repr(new_obj._underlying) == repr(obj._underlying)


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
