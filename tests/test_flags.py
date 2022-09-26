# SPDX-License-Identifier: MIT

from __future__ import annotations

import re

import pytest

from disnake import flags


class TestFlags(flags.BaseFlags):
    """A test class for flag testing."""

    __test__ = False

    @flags.flag_value
    def one(self):
        return 1 << 0

    @flags.flag_value
    def two(self):
        return 1 << 1

    @flags.flag_value
    def four(self):
        return 1 << 2

    @flags.alias_flag_value
    def three(self):
        return 1 << 0 | 1 << 1

    @flags.flag_value
    def sixteen(self):
        return 1 << 4


class OtherTestFlags(flags.BaseFlags):
    """Another test class for flag testing."""

    @flags.flag_value
    def other_one(self):
        return 1 << 0


def test_all_flags_value() -> None:
    assert flags.all_flags_value(TestFlags.VALID_FLAGS) == 0b10111


def test_flag_creation() -> None:
    assert TestFlags.VALID_FLAGS == {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "sixteen": 16,
    }

    assert TestFlags.DEFAULT_VALUE == 0


def test_flag_creation_inverted() -> None:
    class InvertedFlags(flags.BaseFlags, inverted=True):
        @flags.flag_value
        def one(self):
            return 1 << 0

        @flags.flag_value
        def two(self):
            return 1 << 1

        @flags.flag_value
        def four(self):
            return 1 << 2

        @flags.alias_flag_value
        def three(self):
            return 1 << 0 | 1 << 1

        @flags.flag_value
        def sixteen(self):
            return 1 << 4

    assert InvertedFlags.VALID_FLAGS == {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "sixteen": 16,
    }

    assert InvertedFlags.DEFAULT_VALUE == 0b10111


def test_flag_creation_empty() -> None:
    with pytest.raises(RuntimeError, match="At least one flag must be defined"):

        class InvertedFlags(flags.BaseFlags):
            not_a_flag = 2


class TestFlagValue:
    def test_flag_value_creation(self) -> None:
        flag = flags.flag_value(lambda x: 1 << 2)
        assert 1 << 2 == flag.flag

    def test_flag_value_or(self) -> None:
        ins = TestFlags.four | TestFlags.one

        assert isinstance(ins, TestFlags)
        assert ins.value == 5
        assert (TestFlags.two | ins).value == 7

        assert not ins.value & TestFlags.sixteen.flag
        ins |= TestFlags.sixteen
        assert ins.value == 21

        ins = TestFlags()
        assert ins.value == 0
        assert (ins | TestFlags.one).value == 1

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = TestFlags.four | 32  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = 32 | TestFlags.four  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = TestFlags.four | OtherTestFlags.other_one  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = TestFlags.four | OtherTestFlags(other_one=True)  # type: ignore

    def test_flag_value_invert(self) -> None:
        ins = ~TestFlags.four
        assert isinstance(ins, TestFlags)

        assert ins.value == 23 - 4

    def test_flag_value_xor(self) -> None:
        ins = TestFlags(one=True, two=True)

        ins ^= TestFlags.two
        assert ins.value == 1

        ins ^= TestFlags.three
        assert ins.value == 2

        assert (ins ^ TestFlags.four).value == 6


class TestBaseFlags:
    def test__init__default_value(self) -> None:
        ins = TestFlags()
        assert ins.DEFAULT_VALUE is ins.value

    def test__init__kwargs(self) -> None:
        ins = TestFlags(one=True, two=False)
        assert ins.one is True
        assert ins.two is False

    def test__init__invalid_kwargs(self) -> None:
        with pytest.raises(TypeError, match="'h' is not a valid flag name."):
            TestFlags(h=True)

    def test_set_require_bool(self) -> None:
        with pytest.raises(TypeError, match="Value to set for TestFlags must be a bool."):
            TestFlags(one="h")  # type: ignore

        ins = TestFlags()

        with pytest.raises(TypeError, match="Value to set for TestFlags must be a bool."):
            ins.two = "h"  # type: ignore

    def test__eq__(self) -> None:
        ins = TestFlags(one=True, two=True)
        other = TestFlags(one=True, two=True)

        assert ins is not other
        assert ins == other
        assert not ins != other

        ins.two = False
        assert not ins == other
        assert ins != other

    def test__and__(self) -> None:
        ins = TestFlags(one=True, two=True)
        other = TestFlags(one=True, two=True)

        third = ins & other
        assert third is not ins
        assert third.value == 0b011
        assert third == ins == other

        ins.one = False
        third = ins & other
        assert third is not ins
        assert third.value == 0b010

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for &:")):
            _ = ins & "44"  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for &:")):
            _ = "44" & ins  # type: ignore

    def test__iand__(self) -> None:
        ins = TestFlags(one=True, two=True)
        other = TestFlags(one=True, two=True)

        third = ins
        ins &= other
        assert third is ins
        assert ins.value == 0b011

        other.two = False
        other.four = True
        ins &= other
        assert third is ins
        assert ins.value == 0b001

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for &=:")):
            ins &= 14  # type: ignore

    def test__or__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins | other
        assert third is not ins
        assert ins.value == 0b001
        assert other.value == 0b010
        assert third.value == 0b011

        ins.one = False
        third = ins | other
        assert third.value == 0b010
        assert third is not ins

        ins.value = other.value
        third = ins | other
        assert third is not ins
        assert third.value == 0b10

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = ins | 28  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = 28 | ins  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |:")):
            _ = ins | OtherTestFlags.other_one  # type: ignore

    def test__ior__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins
        ins |= other
        assert ins is third
        assert ins.value == 0b011
        assert other.value == 0b010

        other.four = True
        ins |= other
        assert ins.value == 0b111

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |=:")):
            ins |= True  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for |=:")):
            ins |= OtherTestFlags.other_one  # type: ignore

    def test__xor__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins ^ other
        assert third.value == 0b011
        assert third is not ins

        other.one = True
        third = ins ^ other
        assert third.value == 0b010

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ^:")):
            _ = ins ^ "h"  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ^:")):
            _ = "h" ^ ins  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ^:")):
            _ = ins ^ OtherTestFlags.other_one  # type: ignore

    def test__ixor__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins
        ins ^= other
        assert ins is third
        assert ins.value == 0b011

        ins.two = False
        other.one = True
        ins ^= other
        assert ins.value == 0b010

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ^=:")):
            ins ^= "stability"  # type: ignore

        with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for ^=:")):
            ins ^= OtherTestFlags.other_one  # type: ignore

    def test__le__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins <= other
        other.one = True
        assert ins <= other

        with pytest.raises(
            TypeError, match="'<=' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins <= 4  # type: ignore

        other.value = ins.value
        assert ins <= other

    def test__ge__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins >= other
        ins.two = True
        assert ins >= other

        with pytest.raises(
            TypeError, match="'>=' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins >= 4  # type: ignore

        other.value = ins.value
        assert ins >= other

    def test__lt__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins < other
        other.one = True
        assert ins < other

        with pytest.raises(
            TypeError, match="'<' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins < 4  # type: ignore

        other.value = ins.value
        assert not ins < other

    def test__gt__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins > other
        ins.two = True
        assert ins > other

        with pytest.raises(
            TypeError, match="'>' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins > 4  # type: ignore

        other.value = ins.value
        assert not ins > other

    def test__invert__(self) -> None:
        ins = TestFlags(one=True)
        assert ins.value == 0b0001
        other = ~ins
        # assert that invert does not modify anything in-place
        assert ins.value == 0b0001
        # the other `0` here is because invert does not invert values that are not defined
        # assert other.value == goal
        assert other.value == 0b10110

    def test__hash__(self) -> None:
        ins = TestFlags(one=True)
        assert hash(ins) == hash(ins.value)

    def test_iter(self) -> None:
        ins = TestFlags(one=True, two=False)

        assert len(list(iter(ins))) == 4

        for flag, value in iter(ins):
            assert flag in ins.VALID_FLAGS
            assert getattr(ins, flag) == value

    def test_from_value(self) -> None:
        ins = TestFlags._from_value(0b101)
        assert ins.value == 0b101

    def test_set_and_get_flag(self) -> None:
        ins = TestFlags()
        assert ins.DEFAULT_VALUE == ins.value

        ins.two = True
        assert ins.two is True
        assert ins.value == TestFlags.two.flag == 1 << 1

    def test_alias_flag_value(self) -> None:
        ins = TestFlags(three=True)
        assert ins.value == 0b11
        ins.three = False
        assert ins.value == 0

    def test_alias_priority(self) -> None:
        ins = TestFlags(three=False, two=True, one=False)
        assert ins.value == 0b10

        ins = TestFlags(three=True, two=False, one=False)
        assert ins.value == 0b00

        ins = TestFlags(three=True, two=False)
        assert ins.value == 0b01

        ins = TestFlags(two=False, three=True)
        assert ins.value == 0b11

        ins = TestFlags(two=True, three=False)
        assert ins.value == 0b00


class _ListFlags(flags.ListBaseFlags):
    @flags.flag_value
    def flag1(self):
        return 1 << 0

    @flags.flag_value
    def flag2(self):
        return 1 << 1

    @flags.flag_value
    def flag3(self):
        return 1 << 2


class TestListBaseFlags:
    @pytest.mark.parametrize(
        ("kwargs", "expected_value", "expected_values"),
        [
            ({}, 0, []),
            ({"flag2": True}, 2, [1]),
            ({"flag3": True, "flag2": False, "flag1": True}, 5, [0, 2]),
        ],
    )
    def test_init(self, kwargs, expected_value, expected_values) -> None:
        flags = _ListFlags(**kwargs)
        assert flags.value == expected_value
        assert flags.values == expected_values

    def test_class_vars(self) -> None:
        assert _ListFlags.DEFAULT_VALUE == 0
        assert _ListFlags.VALID_FLAGS == {"flag1": 1, "flag2": 2, "flag3": 4}

    def test_from_values(self) -> None:
        flags = _ListFlags._from_values([0, 2, 3, 4, 5, 10])
        assert flags.value == 1085
        assert flags.values == [0, 2, 3, 4, 5, 10]

    @pytest.mark.parametrize("value", [-10, -1, 100])
    def test_from_values__invalid(self, value) -> None:
        with pytest.raises(ValueError, match=re.escape("Flag values must be within [0, 64)")):
            _ListFlags._from_values([0, 2, value, 3])

    def test_update(self) -> None:
        flags = _ListFlags(flag2=True)
        flags.flag2 = False
        flags.flag3 = True
        assert flags.value == 4
        assert flags.values == [2]

    def test_operators(self) -> None:
        a = _ListFlags(flag1=True, flag3=True)
        b = _ListFlags(flag1=False, flag3=True)
        assert a.values == [0, 2]
        assert b.values == [2]
        assert (~(a & b)).values == [0, 1]


class TestIntents:
    def test_all_only_valid(self) -> None:
        """Test that Intents.all() doesn't include flags that aren't defined."""

        intents = flags.Intents.all()

        assert not (1 << 18 | 1 << 17) & intents.value
        assert 1 << 20 & intents.value
