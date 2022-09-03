from typing import Any
from unittest import mock

import pytest

from disnake import enums


@mock.patch.object(enums.EnumMeta, "__is_enum_instantiated__", new=False)
def test_init_first_enum():
    assert enums.EnumMeta.__is_enum_instantiated__ is False

    class Enum(metaclass=enums.EnumMeta):
        pass

    assert enums.EnumMeta.__is_enum_instantiated__ is True


def test_init_followup_enum():
    assert enums.EnumMeta.__is_enum_instantiated__ is True

    class TestEnum(int, enums.Enum):
        pass

    assert enums.EnumMeta.__is_enum_instantiated__ is True

    assert TestEnum.__mro__ == (TestEnum, int, enums.Enum, object)


def test_init_enum_incorrect_base_number():
    with pytest.raises(TypeError, match="at most two base classes"):

        class FailedEnum(int, str, enums.Enum):
            pass


def test_init_enum_incorrect_base_order():
    with pytest.raises(TypeError, match="first base class"):

        class FailedEnum(enums.Enum, int):
            pass


def test_init_enum_untyped_no_members():
    class UntypedEnum(enums.Enum):
        _private = "a"

    assert UntypedEnum._private == "a"


def test_init_enum_untyped_inheritance():
    with pytest.raises(TypeError):

        class UntypedEnum(enums.Enum):
            member = "a"


def test_init_enum_inheritance():
    class UntypedBaseEnum(enums.Enum):
        def x(self):
            return "woo"

    class TypedInheritor(int, UntypedBaseEnum):
        y = 1

    assert TypedInheritor.__base_type__ is int  # type: ignore
    assert TypedInheritor.y.x() == "woo"


def test_init_enum_typed_inheritance():
    class TypedBaseEnum(int, enums.Enum):
        def x(self):
            return "woo"

    class UntypedInheritor(TypedBaseEnum):
        # Base type <int> inferred from TypedBaseEnum
        y = 1

    assert UntypedInheritor.__base_type__ is int  # type: ignore
    assert UntypedInheritor.y.x() == "woo"


def test_init_enum_member_inheritance():
    class BaseEnum(int, enums.Enum):
        a = 1

    with pytest.raises(TypeError):

        class ChildEnum(BaseEnum):  # type: ignore
            b = 2


@pytest.mark.parametrize("name", ["mro", "name", "value"])
def test_init_enum_illegal_name(name: str):
    with pytest.raises(ValueError, match="Invalid Enum member name"):
        # TODO: come up with a better way of running this test.
        exec(f"class PainEnum(int, enums.Enum):\n\t{name} = 1\n", {"enums": enums})  # noqa: S102


def test_init_enum_type_mismatch():
    with pytest.raises(TypeError):

        class FailedEnum(int, enums.Enum):  # int here
            a = "abc"  # str here


def test_init_enum_preserve_privates_and_dunders():
    base = int

    class WhackEnum(base, enums.Enum):  # int here
        a = 1
        __b__ = "b"
        _c_ = "c"
        _d = "d"

    assert not isinstance(b := WhackEnum.__b__, base)
    assert b == "b"

    assert not isinstance(c := WhackEnum._c_, base)
    assert c == "c"

    assert not isinstance(d := WhackEnum._d, base)
    assert d == "d"


def test_init_enum_preserve_methods():
    class MethodEnum(int, enums.Enum):
        obligatory_field = 1

        def instance_method(self):
            assert isinstance(self, MethodEnum)
            return "works"

        @classmethod
        def class_method(cls):
            assert cls is MethodEnum
            return "works"

        @staticmethod
        def static_method():
            return "works"

    # Need an instance (field) for the instance method
    assert MethodEnum.obligatory_field.instance_method() == "works"

    assert MethodEnum.class_method() == "works"

    assert MethodEnum.static_method() == "works"


def test_init_enum_preserve_descriptors():
    class DescriptorEnum(str, enums.Enum):
        bar = "bar"

        @property
        def foo(self):
            return "foo"

    assert isinstance(DescriptorEnum.foo, property)
    assert DescriptorEnum.bar.foo == "foo"


def test_init_enum_duplicate_name():
    with pytest.raises(TypeError):

        class DumbEnum(int, enums.Enum):
            a = 1
            a = 2  # type: ignore


def test_init_enum_duplicate_value():
    class Enum(int, enums.Enum):
        a = 1
        b = 1

    assert Enum.a == Enum.b == 1


def test_call_enum_success():
    class Enum(int, enums.Enum):
        a = 1

    assert Enum.a is Enum(1) == 1


def test_call_enum_duplicate_value():
    class Enum(int, enums.Enum):
        a = 1
        b = 1

    assert Enum.a is Enum(1) == 1  # prioritize first just like vanilla enums


def test_call_enum_wrong_value():
    class Enum(int, enums.Enum):
        a = 1

    with pytest.raises(ValueError, match="is not a valid"):
        Enum(2)


def test_get_enum_success():
    class Enum(int, enums.Enum):
        a = 1

    assert Enum.a is Enum["a"] == 1


def test_get_enum_wrong_name():
    class Enum(int, enums.Enum):
        a = 1

    with pytest.raises(KeyError):
        Enum["b"]


def test_enum_contains():
    class Enum(int, enums.Enum):
        a = 1

    assert 1 in Enum
    assert 2 not in Enum


def test_enum_iter():
    class Enum(int, enums.Enum):
        a = 1
        b = 2

    enum_iter = iter(Enum)
    assert Enum.a is next(enum_iter) == 1
    assert Enum.b is next(enum_iter) == 2

    with pytest.raises(StopIteration):
        next(enum_iter)


@pytest.mark.parametrize("value", [1, "a"])
def test_try_enum_hit(value: Any):
    type_ = type(value)

    class Enum(type_, enums.Enum):
        a = value

    new = enums.try_enum(Enum, value)

    assert Enum.a is new == value


@pytest.mark.parametrize(
    ("value", "unknown"),
    [
        (1, 2),
        ("a", "b"),
        (1, None),  # wrong type altogether should also work
    ],
)
def test_try_enum_miss(value: Any, unknown: Any):
    type_ = type(value)

    class Enum(type_, enums.Enum):
        a = value

    new = enums.try_enum(Enum, unknown)

    assert new not in Enum  # type: ignore
    assert new == unknown
